from pathlib import Path
from datetime import datetime, timedelta
from string import ascii_letters
import random
import yaml
from slugify import slugify
import csv


class RollExporter:
    '''
    '''
    _modes = ['unified', 'separated']
    _mode_sep_opts = ['commune', 'region']

    def export_sheet(self, parsed):
        if not self.export:
            return None
        # rid = parsed.metadata['rid']
        file, created = self.get_or_create_file(parsed)
        with file.open('a') as f:
            writer = csv.writer(f)
            if created:
                writer.writerow(parsed.fields)
            for entry in parsed.entries:
                writer.writerow(entry)
        return str(file.absolute())

    def export_summary(self, rid, metadata):
        def metadata_serializer(meta):
            meta = {**meta}
            for key in meta:
                if isinstance(meta[key], dict):
                    meta[key] = metadata_serializer(meta[key])
                elif isinstance(meta[key], datetime) or isinstance(
                        meta[key], timedelta):
                    meta[key] = str(meta[key])
                else:
                    continue
            return meta
        if not self.export or not self.summary:
            return None
        metadata = metadata_serializer(metadata)
        # files_num = len(metadata['files'])
        # analysis = metadata['analysis']
        # duration = analysis['finalized'] - analysis['started']
        # durations = analysis['durations']
        # rolls = metadata['rolls']
        file = self.create_summary(rid)
        with file.open('w') as f:
            f.write('# Serveliza summary\n')
            f.write(yaml.dump(metadata))
        return str(file.absolute())

    def get_or_create_file(self, parsed):
        suffix, created = '', False
        if self.mode == 'separated':
            suffix = slugify(parsed.header[self.mode_sep]) + '-'
        name = f'{parsed.metadata["rid"]}-{suffix}data'
        if self.random_suffix:
            name += f'-{self.random_suffix}'
        name += '.csv'
        file = self.output / name
        if not file.exists():
            created = True
            file.touch()
        return file, created

    def create_summary(self, rid):
        name = f'{rid}-summary'
        if self.random_suffix:
            name += f'-{self.random_suffix}'
        name += '.txt'
        summary = self.output / name
        return summary

    @property
    def output(self):
        '''
        Directory to store the data in .csv.
        '''
        return self._output

    @output.setter
    def output(self, output):
        output_path = Path(str(output))
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise FileExistsError(output+' file already exists.')
        self._output = output_path

    @property
    def mode(self):
        '''
        'Determines the data export mode in files. If it is "unified" \
        (default) it creates a single csv file with the data, or if it \
        is "separated" into several according to communal or \
        regional criteria.'
        '''
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode not in self._modes:
            raise TypeError('mode must be: '
                            ','.join(self._modes))
        self._mode = mode

    @property
    def mode_sep(self):
        '''
        Criteria for separating files in export in separate mode.
        '''
        return self._mode_sep

    @mode_sep.setter
    def mode_sep(self, mode_sep):
        if mode_sep not in self._mode_sep_opts:
            raise TypeError('mode_sep must be: '
                            ','.join(self._mode_sep_opts))
        self._mode_sep = mode_sep

    @property
    def export(self):
        '''
        '''
        return self._export

    @property
    def random_suffix(self):
        '''
        Determines whether exported files have a random \
        text string appended to the end.
        '''
        return self._random_suffix

    @property
    def summary(self):
        '''
        Determines whether to generate a summary file of \
        the export and the extracted data.
        '''
        return self._summary

    def __init__(self, *args, **kwargs):
        self._export = bool(kwargs.get('export', False))
        if not self.export:
            return None
        self.output = kwargs.get('output', 'output')
        self.mode = kwargs.get('mode', 'unified')
        if self.mode == 'separated':
            self.mode_sep = kwargs.get('mode_sep', 'commune')
        self._random_suffix = False
        if kwargs.get('random_suffix', True):
            self._random_suffix = ''.join([random.choice(
                ascii_letters) for x in range(5)])
        self._summary = bool(kwargs.get('summary', True))
