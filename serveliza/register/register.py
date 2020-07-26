import os
from datetime import datetime, timedelta
from tqdm import tqdm
from ..mixins import DirFilePDFMixin
from ..utils import colors
from .parsers import SheetRegisterParser


class ElectoralRegister(DirFilePDFMixin):
    '''
    Class to process electoral register \
    file (padrón electoral) of chilean electoral \
    service (Servicio Electoral de Chile, Servel) \
    in PDF format.

    The constructor of instance require specify a \
    \'source\' param with the path string of directory \
    or PDF file to process. The constructor is heredit \
    of <.DirFilePDFMixin>.

    Testing with electoral register of 2013 (presidential, \
    senatorial, parliamentary and regional councilors) and \
    2016 (municipal) elections. *16/07/20*
    '''
    parser_class    = SheetRegisterParser
    
    @property
    def resume(self):
        return print(self)

    def __str__(self):
        resume = f'{self.__class__.__name__} instance'
        if self.runned:
            resume += colors.OK(' [runned]')
            resume += colors.LEAD(f' {str(len(self.metadata["files"]))} file')
            if len(self.metadata['files']) > 1:
                resume += 's'
        else:
            resume += colors.WARN(' [not runned]')
        resume += colors.LEAD('\n'+('-'*len(resume)))
        storages = len(self.storage)
        if storages > 1:
            resume += colors.WARN(f'\n[warn]: {str(storages)}'\
                +' different electoral register loaded. Dont do it,'\
                +' there may be repetitions of people.')
        screen_width = os.get_terminal_size().columns
        for key,bucket in self.storage.items():
            column_width = screen_width // len(bucket['fields'])
            total_entries = bucket["metadata"]["entries-total"]
            resume += '\n['+colors.OK(key)\
                +f']: data of {colors.INFO(total_entries)} people'
            errors = (100 / total_entries)*len(self.errors)
            resume += colors.LEAD(f' [{errors:.5} % of errors]')
            divider = colors.LEAD('|')
            divider_width = colors.LEAD('\n'+('-'*screen_width))
            cutter = lambda x: '.' if len(x) - (column_width -4) > 0 else (' ')
            column_aux = colors.LEAD(divider+' {:<'+str(column_width -3 )+'} ')
            fields = '\n' + str(column_aux*len(bucket['fields'])).format(
                *[colors.INFO(x[:column_width -4])+cutter(x) for x in bucket['fields']]) + divider
            resume += divider_width + fields + divider_width
            resume += '\n' + str(column_aux*len(bucket['fields'])).format(
                *[x[:column_width -4]+cutter(x) for x in bucket['entries'][0]]) + divider
            resume += divider_width
            total_msg = colors.OK(f'[ {str(total_entries - 2)} entries ]')
            separator = ( screen_width - len(total_msg) ) // 2
            resume += '\n'+colors.LEAD('-'*separator)+total_msg+colors.LEAD('-'*separator)
            resume += divider_width
            resume += '\n' + str(column_aux*len(bucket['fields'])).format(
                *[x[:column_width -4]+cutter(x) for x in bucket['entries'][-1]]) + divider
            resume += divider_width
        return resume

    @property
    def runned(self):
        return self._runned
    
    @property
    def storage(self):
        return self._storage
    
    @property
    def errors(self):
        return self._errors
    
    @property
    def metadata(self):
        stored = {}
        for k,v in self.storage.items():
            if 'metadata' in v:
                stored[k] = v['metadata']
        return { **self._metadata, **stored }
    
    @property
    def entries(self):
        if self.storage and 'entries' \
        in self.storage[self.register]:
            return self.storage[self.register]['entries']
    
    @property
    def fields(self):
        if self.storage and 'fields' \
        in self.storage[self.register]:
            return self.storage[self.register]['fields']

    @property
    def register(self):
        if self.storage:
            registers = [x for x in self.storage]
            return registers[0]

    def run(self):
        starting = datetime.now()
        self.metadata['analysis'] = {'starting': starting}
        sheets = self.sheets
        if self.verbose:
            total_sheets = colors.INFO(len(sheets))
            print(f'Initiating analysis of {total_sheets} sheets')
            print(colors.LEAD(f"At {str(starting)}"))
            sheets = tqdm(sheets)
        for idx,sheet in enumerate(sheets):
            if self.verbose:
                sheets.set_description(
                    f'> {str(idx)}/{total_sheets} sheets')
            parsed = self.parse_sheet(sheet)
            parsed = self.storage_sheet(parsed)
        self._runned = True
        self.storage_consolidate()
        self.resume

    def parse_sheet(self, sheet):
        return self.parser_class(sheet=sheet)

    def storage_sheet(self, parsed):
        # ..
        rid = parsed.metadata['rid']
        # prepare schema
        metadata = {}
        if not rid in self._storage:
            self._storage[rid] = {}
            self._storage[rid]['entries'] = []
            self._storage[rid]['fields'] = parsed.fields
            self._storage[rid]['metadata'] = {
                'regions'  : [],
                'communes' : [],
                'provinces': [],
                'times'    : {
                    'total': timedelta(),
                    'parse-header': timedelta(),
                    'parse-fields': timedelta(),
                    'parse-entries': timedelta(),},
                'nulls-total':      0,
                'entries-total':    0,
                'entries-rescue':   0,}
            metadata['register'] = parsed.header['register']
            metadata['election'] = parsed.header['election']
            metadata['year']     = parsed.header['year']
        # times
        total = self._storage[rid]['metadata']\
            ['times']['total'] + parsed.metadata['times']['total']
        parse_header = self.storage[rid]['metadata']\
            ['times']['parse-header'] + parsed.metadata['times']['parse-header']
        parse_fields = self.storage[rid]['metadata']\
            ['times']['parse-fields'] + parsed.metadata['times']['parse-fields']
        parse_entries = self.storage[rid]['metadata']\
            ['times']['parse-entries'] + parsed.metadata['times']['parse-entries']
        times = {'total': total, 'parse-header': parse_header,
            'parse-fields': parse_fields, 'parse-entries': parse_entries}
        metadata['times'] = times
        # nulls
        nulls_total = parsed.metadata['nulls-total']
        if nulls_total:
            nulls_total += self.storage[rid]['metadata']['nulls-total']
            metadata['nulls-total'] = nulls_total
            kfields = ['name','rut','sex','table']
            for k in kfields:
                prefix = lambda x:'nulls-'+x
                if prefix(k) in parsed.metadata:
                    metadata[prefix(k)] = parsed.metadata[prefix(k)]
                    if prefix(k) in self.storage[rid]['metadata']:
                        metadata[prefix(k)] += self.storage[rid]['metadata'][prefix(k)]  
        # territory
        region    = parsed.header['region']
        regions   = self.storage[rid]['metadata']['regions']
        province  = parsed.header['province']
        provinces = self.storage[rid]['metadata']['provinces']
        commune   = parsed.header['commune']
        communes  = self.storage[rid]['metadata']['communes']
        if not region in regions:
            self._storage[rid]['metadata']['regions']\
                .append(region)
        if not province in provinces:
            self._storage[rid]['metadata']['provinces']\
                .append(province)
        if not commune in communes:
            self._storage[rid]['metadata']['communes']\
                .append(commune)
        self._storage[rid]['metadata'].update(metadata)
        # ..
        self._storage[rid]['entries'] += parsed.entries
        self._storage[rid]['metadata']['entries-total'] += parsed.metadata['entries-total']
        self._storage[rid]['metadata']['entries-rescue'] += parsed.metadata['entries-rescue']
        self._errors += parsed.errors
        return parsed

    def storage_consolidate(self):
        pass

    def __init__(self, auto=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._storage = {}
        self._errors = []
        self._runned = False
        if auto: 
            if self.verbose:
                print(colors.INFO('Automatic initialization'))
            self.run()
