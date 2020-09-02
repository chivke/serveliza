from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path
from pandas import pandas as pd
import numpy as np


from serveliza.mixins.pdf import PDFProcessorMixin
from serveliza.utils import pdf as pdf_utils
from .parsers import RollParser
from .adapters import RollAdapter
from .printer import RollPrinter
from .memorizer import RollMemorizer
from .exporter import RollExporter


DURATIONS_SCHEMA = {
    'processing': timedelta(),
    'adapting': timedelta(),
    'parsing': timedelta(),
    'memorizing': timedelta(),
    'exporting': timedelta()}


class ElectoralRoll(PDFProcessorMixin):
    '''ElectoralRoll

    :class:`ElectoralRoll <.ElectoralRoll>` allows to \
    instantiate an electoral roll of the chilean Electoral Service \
    (*Servicio Electoral de Chile*, SERVEL) from PDF files.

    Different parameters are handled in the constructor of this class. In \
    itself it handles the *source* parameter that determines the path \
    where to recognize pdf files (it can be a directory path or a file), \
    the *recursive* parameter that determines whether to search in the \
    root of the defined path or in each of its subdirectories, and \
    the *auto* parameter that determines if the extraction is automatic. \
    It also inherits parameters from :class:`PDFProcessorMixin \
    <.PDFProcessorMixin>` (*processor*). Likewise, in the constructor \
    it instantiates other nested classes by routing their parameters.

    :param str source: The source path of pdf files.
    :param bool auto: Run the extract in the instantation.
    :param bool recursive: Determines if the search for pdf files in the \
        delivered source is recursive or is only for the root of the \
        indicated directory,
    :param str processor: Processor to use (default='pdftotext', see \
        more in :class:`PDFProcessorMixin <.PDFProcessorMixin>`).
    :param bool memorize: Storage data in memory of instance (default=True, \
        see more in :class:`RollMemorizer <.RollMemorizer>`).
    :param bool export: If export data in csv file (default=False, \
        see more in :class:`RollExporter <.RollExporter>`).
    :param str output: Directory to store the data in csv file(s) (\
        see more in :class:`RollExporter <.RollExporter>`).
    :param str mode: Determines the data export mode in files. If it \
        is *unified* (default) it creates a single csv file with the data,\
         or if it is *separated* into several according to communal or \
        regional criteria (see more in :class:`RollExporter <.RollExporter>`).
    :param str mode_sep: Criteria for separating files in export in \
        separate mode (*commune* or *region*, default="commune", \
        see more in :class:`RollExporter <.RollExporter>`).
    :param bool random_suffix: Determines whether exported files have a \
        random text string appended to the end (see more in \
        :class:`RollExporter <.RollExporter>`).
    :param bool summary: Determines whether to generate a summary file of \
        the export and the extracted data (see more in :class:`RollExporter \
        <.RollExporter>`).

    Anyway, only the *source* parameter is required:

    >>> obj = ElectoralRoll(source='/path/to/the/pdf/file(s')
    >>> obj.run()  # Start the analysis and extraction of data.

    Setting the parameter *auto* to true in the constructor will \
    automatically start the :meth:`run <.ElectoralRoll.run>` method:

    >>> obj = ElectoralRoll(source='/path/to/the/pdf/file(s', auto=True)

    See the :meth:`run <.ElectoralRoll.run>` at that method for a better \
    understanding of this class.
    '''

    inner_class_parser = RollParser
    inner_class_adapter = RollAdapter
    inner_class_printer = RollPrinter
    inner_class_memorizer = RollMemorizer
    inner_class_exporter = RollExporter

    # Operational methods
    # --------------------
    def run(self):
        '''
        :meth:`ElectoralRoll.run <.ElectoralRoll.run>` is the main method \
        within the class logic that executes the complete flow of data \
        analysis and extraction:

        * Iterate over the found files, ordered by size from smallest \
        to largest, executing the :meth:`run_file <.ElectoralRoll.run_file>` \
        method with the file, its index and the total.
        * It iterates on each page of each file:
            * *Processing* it with the library determined in the processor \
            property and defined in the constructor (see more in \
            :class:`PDFProcessorMixin <.PDFProcessorMixin>`).
            * *Adapting* the rendered page if required by the application \
            and the processor used (see more in :class:`RollAdapter \
            <.RollAdapter>`).
            * *Analyzing* the content text to extract its data (see more \
            in :class:`RollParser <.RollParser>`).
            * *Memorizing* your data in a consolidated data stored in the \
            memorizer. Its execution can be skipped by setting the \
            *memorizer* parameter to false in the constructor (see more \
            in :class:`RollMemorizer <.RollMemorizer>`).
            * *Exporting* your data to one or more csv files depending on \
            how the exporter is configured. Its execution can be activated \
            by defining the *export* parameter as true in the constructor \
            (see more in :class:`RollExporter <RollExporter>`).
        * The printer (:class:`RollPrinter <.RollPrinter>` instance) is \
        executed in each part of the flow and it determines if and how it \
        prints on the screen (as declared in the constructor).

        >>> roll.run()
        '''
        started = dt.now()
        self._metadata['analysis']['started'] = started
        files = self._metadata['files']
        self.printer.run_started(started, files)
        files = [x[1] for x in sorted(
            files.items(), key=lambda x: x[1]['bytes'])]
        for idx, file in enumerate(files):
            self.run_file(file, idx, len(files))
        finalized = dt.now()
        self._metadata['analysis']['finalized'] = finalized
        summary = self.exporter.export_summary(self.rid, self.metadata)
        if summary:
            self._metadata['exported_to'].append(summary)
        self._is_runned = True
        self.printer.run_finalized(finalized, self.metadata)

    def run_file(self, file, file_num, file_total):
        '''
        :param dict file: data of file
        :param int file_num: the number of file to analize.
        :param int file_total: the total of files to analize.
            this param and before is needed for printer.

        The :meth:`run_file <.ElectoralRoll.run_file>` method is called by \
        the :meth:`run <.ElectoralRoll.run>` method and iterates on each page \
        of each file:

            * *Processing* it with the library determined in the processor \
            property and defined in the constructor (see more in \
            :class:`PDFProcessorMixin <.PDFProcessorMixin>`).
            * *Adapting* the rendered page if required by the application \
            and the processor used (see more in :class:`RollAdapter \
            <.RollAdapter>`).
            * *Analyzing* the content text to extract its data (see more \
            in :class:`RollParser <.RollParser>`).
            * *Memorizing* your data in a consolidated data stored in the \
            memorizer. Its execution can be skipped by setting the \
            *memorizer* parameter to false in the constructor (see more \
            in :class:`RollMemorizer <.RollMemorizer>`).
            * *Exporting* your data to one or more csv files depending on \
            how the exporter is configured. Its execution can be activated \
            by defining the *export* parameter as true in the constructor \
            (see more in :class:`RollExporter <RollExporter>`).

        Stores metadatas of the extraction of each file.
        '''

        def get_progress(self, rid, files, sheets):
            metadata = self.metadata['rolls'].get(rid, {})
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
                self, file['name'], 'adapting', 'inner_class_adapter',
                [processed, self.processor]).sheet
            # parsingd
            parsed = duration_wrapper(
                self, file['name'], 'parsing', 'sheet_parse', [adapted])
            # memorizing
            duration_wrapper(self, file['name'], 'memorizing',
                             'sheet_memorize', [parsed])
            # exporting
            exported = duration_wrapper(
                self, file['name'], 'exporting', 'sheet_export', [parsed])
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

    def sheet_parse(self, sheet, *args, **kwargs):
        '''
        :param str sheet: sheet in string.
        :return: instance of :class:`RollParser <.RollParser>`.

        Method that calls the class defined in the :attr:`inner_class_parser \
        <.ElectoralRoll.inner_class_parser>` class attribute, initializing it \
        with the sheet argument.
        '''
        return self.inner_class_parser(sheet, *args, **kwargs)

    def sheet_memorize(self, parsed, *args, **kwargs):
        '''
        :param str parsed: instance of :class:`RollParser <.RollParser>`.

        Method that routes a parsed page to the :meth:`memorize \
        <.RollMemorizer.memorize>` method of the memorizer.
        '''
        return self.memorizer.memorize(parsed, *args, **kwargs)

    def sheet_export(self, parsed, *args, **kwargs):
        '''
        :param str parsed: instance of :class:`RollParser <.RollParser>`.
        :return: Absolute path of the csv file where the data was exported.

        Method that routes a parsed page to the :meth:`export_sheet \
        <.RollExporter.export_sheet>` method of the exporter.
        '''
        return self.exporter.export_sheet(parsed, *args, **kwargs)

    @property
    def printer(self):
        '''
        :return: inner instance of :class:`RollPrinter <.RollPrinter>`.

        Property to call the :class:`RollPrinter <.RollPrinter>` object \
        instanciated in constructor.

        >>> roll.printer.__class__
        serveliza.roll.printer.RollPrinter
        '''
        return self._printer

    @property
    def memorizer(self):
        '''
        :return: inner instance of :class:`RollMemorizer <.RollMemorizer>`.

        Property to call the :class:`RollMemorizer <.RollMemorizer>` object \
        instanciated in constructor.

        >>> roll.memorizer.__class__
        serveliza.roll.memorizer.RollMemorizer
        '''
        return self._memorizer

    @property
    def exporter(self):
        '''
        :return: inner instance of :class:`RollExporter <.RollExporter>`.

        Property to call the :class:`RollExporter <.RollExporter>` object \
        instanciated in constructor.

        >>> roll.exporter.__class__
        serveliza.roll.exporter.RollExporter
        '''
        return self._exporter

    # Operational properties
    # -----------------------
    @property
    def is_runned(self):
        '''
        :return: boolean.

        Boolean property that indicates whether the instance has executed the \
        :meth:`run <.ElectoralRoll.run>` method or not.

        >>> roll.is_runned
        True  # or False
        '''
        return self._is_runned

    @property
    def metadata(self):
        '''
        :return: dictionary with all metadata.

        Property that stores the analysis metadata.
        It integrates the metadata of each electoral register detected \
        in the analysis.

        >>> roll.is_runned
        False
        >>> roll.metadata
        {'files': {'filename.pdf': {'name': 'filename.pdf',
           'bytes': 10000,
           'relative': 'relative/path/filename.pdf',
           'absolute': '/absolute/path/filename.pdf',
           'mtime': datetime.datetime(...),
           'atime': datetime.datetime(...),
           'durations': {'processing': datetime.timedelta(0),
            'adapting': datetime.timedelta(0),
            'parsing': datetime.timedelta(0),
            'memorizing': datetime.timedelta(0),
            'exporting': datetime.timedelta(0)}}},
         'analysis': {'started': None,
          'finalized': None,
          'durations': {'processing': datetime.timedelta(0),
           'adapting': datetime.timedelta(0),
           'parsing': datetime.timedelta(0),
           'memorizing': datetime.timedelta(0),
           'exporting': datetime.timedelta(0)}},
         'rolls': {}}
        >>> roll.run()
        >>> roll.metadata
        {'files': {'filename.pdf': {'name': 'filename.pdf',
           ...
           'rid': 'RID-XXXX',
           'roll': 'PADRON ELECTORAL X - ELECCIONES X XXXX',
           'year': XXXX,
           'region': 'REGION',
           'province': 'PROVINCE',
           'commune': 'COMMUNE',
           'entries': {'total': 999, 'rescue': 0, 'errors': 0},
           'duration': datetime.timedelta(...)}},
         'analysis': {'started': datetime.datetime(...) ...},
         'rolls': {'RID-XXXX: {'roll': 'PADRON ELECTORAL X - ELE...',
           'year': XXXX,
           'regions': ['REGION', ...],
           'communes': ['COMMUNE', ...],
           'provinces': ['PROVINCE', ...],
           'nulls': {'total': 0},
           'entries': {'total': 999, 'rescue': 0, 'errors': 0}}}}
        '''
        stored = {'rolls': {}}
        for k, v in self.memorizer.storage.items():
            if 'metadata' in v:
                stored['rolls'][k] = v['metadata']
        return {**self._metadata, **stored}

    @property
    def rid(self):
        '''
        :return: string with first roll identifier.

        Property that returns the identifier of the electoral roll analyzed.
        If it will return only the first identifier detected, this should \
        not cause inconvenience unless pdf files from different electoral \
        rolls are loaded.

        >>> roll.rid
        'RID-XXXX'

        If the instance did not run, it returns None.
        '''
        if self.memorizer.storage:
            rids = [x for x in self.memorizer.storage]
            return rids[0]

    @property
    def roll(self):
        '''
        :return: name of electoral roll.

        Property that returns the full name of electoral roll analyzed.

        >>> roll.roll
        'PADRON ELECTORAL X - ELECCIONES X XXXX'

        Internaly use the :attr:`rid <.ElectoralRoll.rid>` property. If the \
        instance did not run, it returns None.
        '''
        if self.memorizer.storage:
            return self.memorizer.storage[self.rid]['metadata']['roll']

    @property
    def entries(self):
        '''
        :return: list of data entries of memorizer.

        Property that accesses the data entries of the electoral roll \
        analyzed. The data is stored in the :class:`RollMemorizer \
        <.RollMemorizer>` instance.

        >>> roll.entries
        [[...]...]

        Internaly use the :attr:`rid <.ElectoralRoll.rid>` property. If the \
        instance did not run, it returns None.
        '''
        storage = self.memorizer.storage
        if storage and 'entries' in storage[self.rid]:
            return self.memorizer.storage[self.rid]['entries']

    @property
    def fields(self):
        '''
        :return: list of fields of electoral roll.

        Property that returns the fields of the electoral roll analyzed.

        >>> roll.fields
        ['nombre',
         'c-identidad',
         'sex',
         'region',
         'provincia',
         'comuna',
         'domicilio-electoral',
         'circunscripcion',
         'mesa',
         'reference']

        Internaly use the :attr:`rid <.ElectoralRoll.rid>` property. If the \
        instance did not run, it returns None.
        '''
        storage = self.memorizer.storage
        if storage and 'fields' in storage[self.rid]:
            return self.memorizer.storage[self.rid]['fields']

    @property
    def errors(self):
        '''
        :return: list of errors found.

        Property that stores the errors of the analysis. List of errors \
        found in the analysis. Errors are dictionaries with data to keep \
        track of. The purpose of registering them is to improve the \
        development of serveliza.

        >>> roll.errors
        [...]
        '''
        return self.memorizer.errors

    @property
    def to_dataframe(self):
        '''
        :return: Pandas DataFrame instance.
        :raises UserWarning: You need to run the application before \
            converting the result to Pandas DataFrame.

        Property that returns the electoral roll data in a new Pandas \
        `DataFrame`_ instance.

        .. _DataFrame: https://pandas.pydata.org/pandas-docs/stable/\
            reference/api/pandas.DataFrame.html
        '''
        if not self.is_runned:
            raise UserWarning('You need to run the application before '
                              'converting the result to Pandas DataFrame.')
        return pd.DataFrame(np.array(self.entries), columns=self.fields)

    @property
    def source(self):
        '''
        :return: list of paths to valid pdf files.
        :raises TypeError: source param must be string or list.
        :raises TypeError: source doesnt have valid PDF files.

        Property that stores paths of pdf files obtained from a list or \
        string with file paths or directories.

        >>> roll.source
        ['relative / path / to / file.pdf']

        The source is loaded into the constructor through the parameter \
        of the same name. It is also possible to redefine through the \
        property setter:

        >>> roll.source = ['path / to / file.pdf', '/ path / to / dir']
        >>> roll.source = '/path/to/dir/o/file.pdf'
        '''
        return self._source

    @source.setter
    def source(self, source):
        paths = []
        if isinstance(source, str):
            paths.append(source)
        elif isinstance(source, list):
            paths += source
        else:
            raise TypeError('source param must be string or list.')
        files = []
        for path in paths:
            if isinstance(path, str) and pdf_utils.is_valid_pdf(path):
                files += [path]
            elif isinstance(path, str) and Path(path).is_dir():
                files += self.printer.init_search(
                    pdf_utils.get_all_pdf_in_path, [path, self.recursive])
        if not files:
            raise TypeError('Source doesnt have valid PDF files.')
        self._source += files
        meta_files = pdf_utils.get_metadata_from_pdfs(files)
        self.printer.init_founded(meta_files)
        for file in meta_files:
            meta_files[file]['durations'] = DURATIONS_SCHEMA
        self._metadata['files'].update(meta_files)

    @property
    def recursive(self):
        '''
        Property that determines if the search for pdf files in the \
        delivered source is recursive or is only for the root of the \
        indicated directory,
        '''
        return self._recursive

    def __init__(self, source, auto=False, *args, **kwargs):
        processor = kwargs.get('processor', self.processor)
        self.processor = processor
        self._printer = self.inner_class_printer(**kwargs)
        self._memorizer = self.inner_class_memorizer(**kwargs)
        self._exporter = self.inner_class_exporter(**kwargs)
        self._metadata = {'files': {}}
        self._is_runned = False
        self._recursive = bool(kwargs.get('recursive', False))
        self._source = []
        self.source = source
        self._metadata['analysis'] = {
            'started': None,
            'finalized': None,
            'durations': DURATIONS_SCHEMA}
        if auto:
            self.printer.init_auto()
            self.run()

    def __repr__(self):
        return self.printer.repr(self)
