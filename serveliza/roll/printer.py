import os
from serveliza.utils import humanize


class ColorMixin:
    '''
    '''
    def info(self, text):
        if self.colors:
            return f'\033[0;94m{str(text)}\033[0m'
        return text

    def ok(self, text):
        if self.colors:
            return f'\033[0;32m{str(text)}\033[0m'
        return text

    def warn(self, text):
        if self.colors:
            return f'\033[0;33m{str(text)}\033[0m'
        return text

    def lead(self, text):
        if self.colors:
            return f'\033[0;90m{str(text)}\033[0m'
        return text

    def error(self, text):
        if self.colors:
            return f'\033[0;31m{str(text)}\033[0m'
        return text


class RollPrinter(ColorMixin):
    '''
    '''

    @property
    def verbose(self):
        return self._verbose

    @property
    def colors(self):
        return self._colors

    @property
    def log(self):
        return self._log

    def init_search(self, func, args):
        '''
        '''
        if not self.verbose:
            return func(*args)
        msg = self.info('Searching')
        if args[1]:
            msg += self.lead(' (recursively) ')
        msg += self.lead('... ')
        print(msg, end='')
        result = func(*args)
        if result:
            print(self.ok('OK'))
        return result

    def init_founded(self, files):
        '''
        '''
        if not self.verbose:
            return None
        plural = 's' if len(files) > 1 else ''
        msg = self.info(f'Founded {len(files)} pdf file{plural}: \n')
        for file, meta in files.items():
            size = humanize.this_bytes(meta['bytes'])
            msg += ' '+self.ok(file)+' - '
            msg += self.lead(f'({size}) {meta["relative"]}')+'\n'
        print(msg)

    def init_auto(self):
        if not self.verbose:
            return None
        print(self.warn('Running automatically'))

    def run_started(self, started, files):
        if not self.verbose:
            return None
        msg = self.info(f'Running analysis of electoral roll'
                        f' in {str(len(files))} pdf files')+'\n'
        msg += self.lead(f'At {str(started)[:-7]}.')+'\n'
        msg += self.info('Each file will be processed, adapted, '
                         'analyzed, memorized and exported in a '
                         'single cycle for better performance. '
                         'It will start with the smallest files.')+'\n'
        print(msg)

    def run_file_start(self, file, number):
        if not self.verbose:
            return None
        size = humanize.this_bytes(file['bytes'])
        msg = f'\r> {str(number)}: {self.ok(file["name"])} '
        msg += self.lead(f' ({size}) ')
        msg += self.lead(f' {file["relative"]}')
        self.clean_line()
        print(msg)

    def run_file_progress(self, pro):
        if not self.verbose:
            return None
        # spinner cycle
        if self._tmp_run_count > 3:
            self._tmp_run_count = 0
        cycle = self.info(r'-\|/'[self._tmp_run_count])
        self._tmp_run_count += 1
        entries = self.ok(
            f"{pro['entries']}") if pro['entries'] else '0'
        errors = self.error(
            f"{pro['errors']}") if pro['errors'] else '0'
        self.clean_line()
        print(f'\r{cycle} Files: {pro["files"][0]}/{pro["files"][1]} '
              f'[{self.percent(*pro["files"])}%]',
              f'Sheet: {str(pro["sheets"][0])}/{str(pro["sheets"][1])} '
              f'[{self.percent(*pro["sheets"])}%] ',
              f'[{entries}/{errors}]',
              f'Time: {str(pro["duration"])[:-7]}',
              end='', sep=' | ', flush=True)

    def run_file_end(self, metadata):
        if not self.verbose:
            return None
        self.clean_line()
        msg = self.lead('\r- ') + self.info(metadata['rid'])
        roll = self.lead(metadata['roll'][:17]+'...'+metadata['roll'][-10:])
        commune = metadata['commune']
        meta_entries = metadata['entries']
        entries = self.ok(
            meta_entries['total']) if meta_entries['total'] else '0'
        errors = self.error(
            meta_entries['errors']) if meta_entries['errors'] else '0'
        msg += f' {roll} > {self.info(commune)} '
        msg += f'({entries}/{errors})'
        msg += f' | {str(metadata["duration"])[:-7]}'
        print(msg)

    def run_finalized(self, finalized, metadata):
        '''
        '''
        if not self.verbose:
            return None
        files_num = len(metadata['files'])
        analysis = metadata['analysis']
        duration = analysis['finalized'] - analysis['started']
        durations = analysis['durations']
        rolls = metadata['rolls']
        msg = ''
        for rid, roll in rolls.items():
            re = [x for x in roll['regions'] if x]
            pro = [x for x in roll['provinces'] if x]
            com = [x for x in roll['communes'] if x]
            ent = roll['entries']
            regions = ','.join(re) if len(re) < 3 else str(len(re))
            provinces = ','.join(pro) if len(pro) < 3 else str(len(pro))
            communes = ','.join(com) if len(com) < 3 else str(len(com))
            msg += self.info('Roll: ')+f'{roll["roll"]}.\n'
            msg += self.info('Entries: ')+self.ok(
                f"{ent['total']:_}".replace('_', '.'))+'\t'
            msg += self.info('Errors: ')+self.error(ent['errors'])+'\n'
            msg += self.info('Region(s): ')+regions+'.\n'
            msg += self.info('Province(s): ')+provinces+'.\n'
            msg += self.info('Commune(s): ')+communes+'.\n'
        if 'exported_to' in metadata:
            msg += '\nExported to:'
            for path in metadata['exported_to']:
                msg += self.ok(f'\n > {path}')
        msg += self.info(
            f'\n\nAnalysis of {str(files_num)} files finished.')+'\n'
        msg += self.lead(f'At {str(finalized)[:-7]}.')
        msg += '\n'+self.warn('Duration: ')+f'{str(duration)[:-7]}'
        msg += self.lead(
            f'\n- processing: {str(durations["processing"])}'
            f'\n- adapting: {str(durations["adapting"])}'
            f'\n- parsing: {str(durations["parsing"])}')
        if durations['memorizing']:
            msg += self.lead(
                f'\n- memorizing: {str(durations["memorizing"])}')
        if durations['exporting']:
            msg += self.lead(
                f'\n- exporting: {str(durations["exporting"])}')
        print(msg)

    def __init__(self, *args, **kwargs):
        # temp attrs
        self._tmp_run_count = 0
        self._tmp_run_file_progress_dt = None
        if 'verbose' in kwargs:
            self._verbose = bool(kwargs['verbose'])
        else:
            self._verbose = False
        if 'colors' in kwargs:
            self._colors = bool(kwargs['colors'])
        self._colors = True
        self._log = []

    def percent(self, of, total):
        return str(int((100/total)*of))

    def clean_line(self):
        print('\r'+' '*os.get_terminal_size().columns, end='')

    def repr(self, obj):
        msg = '<' + self.info(obj.__class__.__name__)
        msg += ' instance ' + self.runned_tag(obj.runned)
        if obj.runned:
            entries = self.ok(
                len(obj.entries)) if len(obj.entries) else '0'
            errors = self.error(
                len(obj.errors)) if len(obj.errors) else '0'
            msg += f'[{self.ok(obj.rid)}]'
            msg += f'({entries}/{errors})'
            msg += f'[{(len(obj.metadata["files"]))} files]'
        msg += '>'
        return msg

    def runned_tag(self, runned):
        if runned:
            return f"[{self.ok('runned')}]"
        return f"[{self.warn('not runned')}]"
