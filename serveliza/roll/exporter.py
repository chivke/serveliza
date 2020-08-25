from pathlib import Path
from string import ascii_letters
import random
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

    def export_summary(self, metadata):
        if not self.export:
            return None

    def get_or_create_file(self, parsed):
        suffix, created = '', False
        if self.mode == 'separated':
            suffix = slugify(parsed.header[self.mode_sep]) + '-'
        name = f'{parsed.metadata["rid"]}-{suffix}data'
        if self.random_suffix:
            name += f'-{self.random_suffix}'
        name += '.txt'
        file = self.output / name
        if not file.exists():
            created = True
            file.touch()
        return file, created

    def get_or_create_summary(self, parsed):
        created = False
        name = f'{parsed.metadata["rid"]}-summary'
        if self.random_suffix:
            name += f'-{self.random_suffix}'
        name += '.txt'
        summary = self.output / name
        if not summary.exists():
            created = True
            summary.touch()
        return summary, created

    @property
    def output(self):
        '''
        '''
        return self._output

    @output.setter
    def output(self, output):
        '''
        '''
        output_path = Path(str(output))
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise FileExistsError(output+' file already exists.')
        self._output = output_path

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode not in self._modes:
            raise TypeError('mode must be: '
                            ','.join(self._modes))
        self._mode = mode

    @property
    def mode_sep(self):
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
        return self._random_suffix

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
        self._summary = bool(kwargs.get('random_suffix', True))
