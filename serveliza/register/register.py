import os
from datetime import datetime, timedelta
from tqdm import tqdm
from ..mixins.pdf import DirFilePDFMixin
from ..utils import colors
from .parsers import SheetRegisterParser
from . import printers
from . import serializers


class ElectoralRegister(DirFilePDFMixin):
    '''
    :class:`ElectoralRegister <.ElectoralRegister>` allows to \
    instantiate an electoral register of the chilean Electoral Service \
    (Servicio Electoral de Chile, SERVEL) from PDF files.

    The path of the directory or file to be used as the data source must \
    be specified through the "source" parameter when instantiating the \
    object. The "verbose" parameter determines if the progress and the \
    result will be printed on the screen or will be kept silent, it accepts \
    only Boolean values. Both characteristics are inherited from \
    :class:`DirFilePDFMixin <.DirFilePDFMixin>` class.

    The :meth:`run <.ElectoralRegister.run>` method starts the analysis \
    process of the text extracted from each sheet of the files. A parser \
    (:class:`SheetRegisterParser <.SheetRegisterParser>`) will be iterated \
    over each sheet, which will be instantiated from the class defined in \
    the class attribute :attr:`parser_class <.ElectoralRegister.parser_class` \
    and called through the :meth:`parse_sheet <.ElectoralRegister.parse_sheet>`
    method. Each resulting object will be sent to the :meth:`serialize_sheet \
    <.ElectoralRegister.serialize_sheet>` method that will store the result \
    in the :attr:`storage <.ElectoralRegister.storage>` property, and then \
    generate a partial export ( with the :meth:`export_sheet \
    <.ElectoralRegister.export_sheet` method) if so specified.

    Setting the parameter "auto" to true in the constructor will \
    automatically start the :meth:`run <.ElectoralRegister.run>` method.

    >>> obj = ElectoralRegister(
        source='/path/to/the/pdf/file(s)',
        verbose=True,
        auto=True)

    '''
    parser_class = SheetRegisterParser

    @property
    def resume(self):
        return print(self)

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
        self._metadata['analysis'] = {'starting': starting}
        sheets = self.sheets
        if self.verbose:
            total_sheets = colors.INFO(len(sheets))
            print(f'Initiating analysis of {total_sheets} sheets')
            print(colors.LEAD(f"At {str(starting)}"))
            sheets = tqdm(sheets)
        for idx, sheet in enumerate(sheets):
            if self.verbose:
                sheets.set_description(
                    f'> {str(idx)}/{total_sheets} sheets')
            parsed = self.parse_sheet(sheet)
            parsed = self.serialize_sheet(parsed)
        self._runned = True
        self.storage_consolidate()
        #self.resume

    def parse_sheet(self, sheet):
        return self.parser_class(sheet=sheet)

    def serialize_sheet(self, parsed):
        rid = serializers.storage_rid(self, parsed)
        payload = self, parsed, rid
        serializers.metadata_times(*payload)
        serializers.metadata_place(*payload)
        serializers.metadata_entries(*payload)
        serializers.metadata_nulls(*payload)
        self._storage[rid]['entries'] += parsed.entries
        self._errors += parsed.errors

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

    def __str__(self):
        return printers.resume_electoral(self)

    def __repr__(self):
        return printers.repr_electoral(self)
