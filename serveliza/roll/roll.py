from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path
from pandas import pandas as pd
import numpy as np


from serveliza.mixins.pdf import PDFProcessorMixin
from serveliza.utils import pdf as pdf_utils
from .parsers import SheetRollParser
from .adapters import RollAdapter
from .printer import RollPrinter
from .memorizer import RollMemorizer
from .exporter import RollExporter


class ElectoralRoll(PDFProcessorMixin):
    '''
    :class:`ElectoralRoll <.ElectoralRoll>` allows to \
    instantiate an electoral register of the chilean Electoral Service \
    (Servicio Electoral de Chile, SERVEL) from PDF files.

    The path of the directory or file to be used as the data source must \
    be specified through the "source" parameter when instantiating the \
    object. The "verbose" parameter determines if the progress and the \
    result will be printed on the screen or will be kept silent, it accepts \
    only Boolean values. Both characteristics are inherited from \
    :class:`DirFilePDFMixin <.DirFilePDFMixin>` class.

    The :meth:`run <.ElectoralRoll.run>` method starts the analysis \
    process of the text extracted from each sheet of the files. A parser \
    (:class:`SheetRegisterParser <.SheetRegisterParser>`) will be iterated \
    over each sheet, which will be instantiated from the class defined in \
    the class attribute :attr:`parser_class <.ElectoralRoll.parser_class` \
    and called through the :meth:`parse_sheet <.ElectoralRoll.parse_sheet>`
    method. Each resulting object will be sent to the :meth:`serialize_sheet \
    <.ElectoralRoll.serialize_sheet>` method that will store the result \
    in the :attr:`storage <.ElectoralRoll.storage>` property, and then \
    generate a partial export ( with the :meth:`export_sheet \
    <.ElectoralRoll.export_sheet` method) if so specified.

    Setting the parameter "auto" to true in the constructor will \
    automatically start the :meth:`run <.ElectoralRoll.run>` method.

    >>> obj = ElectoralRoll(
        source='/path/to/the/pdf/file(s)',
        verbose=True,
        auto=True)
    '''
    parser_class = SheetRollParser
    adapter_class = RollAdapter
    printer_class = RollPrinter
    memorizer_class = RollMemorizer
    exporter_class = RollExporter

    # Operational methods
    # --------------------
    def run(self):
        '''
        Method that starts the analysis of the pdf files loaded in the \
        :attr:`sheets <.ElectoralRoll.sheets>` property. Iterate in each \
        one of them by running the :meth:`parse_sheet \
        <.ElectoralRoll.parse_sheet>` and :meth:`serializer_sheet \
        <.ElectoralRoll.serializer_sheet>` methods.

        Record in the :attr:`metadata <.ElectoralRoll.metadata>` property \
        in the *analysis* key the duration of the parsing and serialization, \
        as well as when it started and ended.

        >>> obj.run()
        '''
        started = dt.now()
        self._metadata['analysis']['started'] = started
        files = self._metadata['files']
        self.printer.run_started(started, files)
        files = [x[1] for x in sorted(
            files.items(), key=lambda x: x[1]['bytes'])]
        for idx, file in enumerate(files):
            self.run_file(file, idx+1, len(files))
        finalized = dt.now()
        self._metadata['analysis']['finalized'] = finalized
        self._runned = True
        self.printer.run_finalized(finalized, len(files))

    def run_file(self, file, file_num, file_total):
        '''
        '''

        def get_progress(self, rid, files, sheets):
            metadata = self.metadata.get(rid, {})
            if not metadata:
                metadata['entries'] = {'total': 0, 'errors': 0}
            return {
                'entries': metadata['entries']['total'],
                'errors': metadata['entries']['errors'],
                'files': files, 'sheets': sheets,
                'duration': dt.now() - self.metadata['analysis']['started'],
                }

        def duration_wrapper(self, file, stage, method, args):
            init = dt.now()
            method = getattr(self, method)
            result = method(*args)
            duration = dt.now() - init
            self._metadata['files'][file]['durations'][stage] += duration
            self._metadata['analysis']['durations'][stage] += duration
            return result

        def update_file_metadata(parsed, metadata):
            if not metadata:
                metadata['rid'] = parsed.metadata['rid']
                attributes = ['roll', 'year', 'region',
                              'province', 'commune']
                for attr in attributes:
                    metadata[attr] = parsed.header[attr]
                metadata['entries'] = {'total': 0, 'rescue': 0, 'errors': 0}
                declared = parsed.header.get('total_sheets', False)
                if declared:
                    metadata['entries']['declared'] = declared
            entries = parsed.metadata['entries']
            for meta in entries:
                metadata['entries'][meta] += entries[meta]
            return metadata

        # pre-processing
        init = dt.now()
        pdf = self.process_pdf(file['absolute'])
        total_sheets = len(pdf)  # number of pages.
        file_metadata = {}
        rid = None
        self.printer.run_file_start(file, file_num)
        for idx, sheet in enumerate(pdf):
            # printing
            progress = get_progress(
                self, rid, (file_num, file_total), (idx+1, total_sheets))
            self.printer.run_file_progress(progress)
            # processing
            processed = duration_wrapper(
                self, file['name'], 'processing', 'process_pdf_page', [sheet])
            # adapting
            adapted = duration_wrapper(
                self, file['name'], 'adapting', 'adapter_class',
                [processed, self.processor]).sheet
            # parsingd
            parsed = duration_wrapper(
                self, file['name'], 'parsing', 'parse_sheet', [adapted])
            # memorizing
            duration_wrapper(self, file['name'], 'memorizing',
                             'memorize_sheet', [parsed])
            # exporting
            exported = duration_wrapper(
                self, file['name'], 'exporting', 'export_sheet', [parsed])
            if exported:
                if 'exported_to' not in self.metadata:
                    self._metadata['exported_to'] = []
                if exported not in self._metadata['exported_to']:
                    self._metadata['exported_to'].append(exported)
            # update file metadata
            file_metadata = update_file_metadata(parsed, file_metadata)
            rid = file_metadata['rid']
        file_metadata['duration'] = dt.now() - init
        self._metadata['files'][file['name']].update(file_metadata)
        self.printer.run_file_end(file_metadata)

    def parse_sheet(self, sheet):
        '''
        Method that calls the class defined in the :attr:`parser_class \
        <.ElectoralRoll.parser_class>` class attribute, initializing it \
        with the sheet argument.
        '''
        return self.parser_class(sheet)

    def memorize_sheet(self, parsed):
        '''
        '''
        return self.memorizer.memorize(parsed)

    def export_sheet(self, parsed):
        '''
        '''
        return self.exporter.export_sheet(parsed)

    # Operational properties
    # -----------------------
    @property
    def runned(self):
        '''
        Boolean property that indicates whether the instance has executed the \
        :mth:`run <.ElectoralRoll.run>`method or not.
        '''
        return self._runned

    @property
    def metadata(self):
        '''
        Property that stores the analysis metadata.
        It integrates the metadata of each electoral register detected \
        in the analysis.
        '''
        stored = {}
        for k, v in self.memorizer.storage.items():
            if 'metadata' in v:
                stored[k] = v['metadata']
        return {**self._metadata, **stored}

    @property
    def printer(self):
        '''
        Property to call the RollPrinter object instanciated in constructor.
        '''
        return self._printer

    @property
    def memorizer(self):
        '''
        '''
        return self._memorizer

    @property
    def exporter(self):
        return self._exporter

    # Shortcut properties
    @property
    def rid(self):
        '''
        Property that returns the identifier of the electoral roll analyzed.
        If it will return only the first identifier detected, this should \
        not cause inconvenience unless pdf files from different electoral \
        rolls are loaded.
        '''
        if self.memorizer.storage:
            rids = [x for x in self.memorizer.storage]
            return rids[0]

    @property
    def roll(self):
        '''
        '''
        if self.memorizer.storage:
            return self.memorizer.storage[self.rid]['metadata']['roll']

    @property
    def entries(self):
        '''
        Property that accesses the data entries of the electoral roll analyzed.
        '''
        storage = self.memorizer.storage
        if storage and 'entries' in storage[self.rid]:
            return self.memorizer.storage[self.rid]['entries']

    @property
    def fields(self):
        '''Property that returns the fields of the electoral roll analyzed.'''
        storage = self.memorizer.storage
        if storage and 'fields' in storage[self.rid]:
            return self.memorizer.storage[self.rid]['fields']

    @property
    def errors(self):
        '''Property that stores the errors of the analysis.'''
        return self.memorizer.errors

    @property
    def to_dataframe(self):
        '''
        '''
        return pd.DataFrame(np.array(self.entries), columns=self.fields)

    # Constructor
    # ------------
    def __init__(self, source, auto=False, *args, **kwargs):
        # starting properties
        processor = kwargs.get('processor', self.processor)
        self.processor = processor
        self._printer = self.printer_class(**kwargs)  # load printer
        self._memorizer = self.memorizer_class(**kwargs)  # load memorizer
        self._exporter = self.exporter_class(**kwargs)  # load exporter
        self._metadata = {}
        self._runned = False
        recursively = bool(kwargs.get('recursively', False))
        files = []
        if pdf_utils.is_valid_pdf(str(source)):
            files += [source]
        elif Path(str(source)).is_dir():
            files += self.printer.init_search(
                pdf_utils.get_all_pdf_in_path, [source, recursively])
        if not files:
            raise TypeError('Source doesnt have valid PDF files.')
        files = pdf_utils.get_metadata_from_pdfs(files)
        self.printer.init_founded(files)
        durations_schema = {
                'processing': timedelta(),
                'adapting': timedelta(),
                'parsing': timedelta(),
                'memorizing': timedelta(),
                'exporting': timedelta()}
        for file in files:
            files[file]['durations'] = durations_schema
        self._metadata['files'] = files
        self._metadata['analysis'] = {
            'started': None,
            'finalized': None,
            'durations': durations_schema}
        if auto:
            self.printer.init_auto()
            self.run()

    def __repr__(self):
        return self.printer.repr(self)
