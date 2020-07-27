'''
PDF Mixins
-----------

:mod:`serveliza.mixins.pdf`

This module contains the mixins associated with the handling of PDF files.

'''

# builtin libraries
from pathlib import Path
from datetime import datetime

# third party libraries
from tqdm import tqdm

# internal modules
from ..utils import colors

# PDF processors libraries : 
import pdftotext

class ProcessorPDFMixin:
    '''
    Mixin that allows an instance the ability to process \
    PDF files with certain libraries. In the constructor, \
    the processor to be used is defined with the argument \
    of the same name, binding the :attr:`process_pdf \
    <.ProcesosrPDFMixin.process_pdf>` property to the \
    method related to it.

    PDF processor availables:

     - `pdftotext <https://github.com/jalan/pdftotext>`_ \
        (0.1.0 release) with :meth:`pdftotext_processor \
        <.ProcessorPDFMixin.processor_pdftotext>`
    '''
    _processors_availables = ['pdftotext']

    @property
    def process_pdf(self):
        '''
        Property that calls the method corresponding to the PDF file \
        processor configured in the instance initialization.

        >>> obj.process_pdf(*args)
        list # with strings
        '''
        return self._process_pdf
    
    @property
    def processor_name(self):
        '''
        Property containing the name of the PDF processor used \
        in the instance.

        >>> obj.processor_module
        str # with the name of processor
        '''
        return self._processor_name
    
    def processor_pdftotext(self, pathfile):
        '''
        Method to use `pdftotext <https://github.com/jalan/pdftotext>`_ \
        in a file specified in the argument as a path.
        
        >>> obj.pdftotext_processor('/path/to/file.pdf')
        list # with strings
        '''
        with open(pathfile, "rb") as f:
            pdf = pdftotext.PDF(f)
        return pdf

    def __init__(self, processor='pdftotext',*args, **kwargs):
        if not processor in self._processors_availables:
            raise TypeError(f'{str(processor)} must be a available '
                f'processor {str(self._processors_availables)}')
        self._process_pdf = getattr(self, 'processor_'+processor)
        self._processor_name = processor

class DirFilePDFMixin(ProcessorPDFMixin):
    '''
    Mixin that allows an instance to organize the processing \
    of PDF files. This is done in the constructor using the \
    :meth:`pathfile_to_sheets <.DirFilePDFMixin.pathfile_to_sheets>` \
    and :meth:`path_to_sheets <.DirFilePDFMixin.path_to_sheets>` methods \
    by storing the results in the :attr:`sheets <.DirFilePDFMixin.sheets>` \
    property.
    
    The path to consider is indicated through the "source" \
    argument defined in the constructor. If the path is a PDF \
    file it will be processed, however if it is a directory \
    it will be recursively traversed processing all the PDF \
    files it finds.

    In addition, it defines the :attr:`metadata <.DirFilePDFMixin.metadata>` \
    property to store information related to the processed files and the \
    :attr:`verbose <.DirFilePDFMixin.verbose>` property that determines \
    if the process and results is printed on the screen. The latter is \
    definable through the constructor as a "verbose" argument and only \
    supports boolean value.
    
    It is a subclass of :class:`ProcessorPDFMixin <.ProcessorPDFMixin>`.

    >>> class MyClass(ProcessorPDFMixin):
            pass
    >>> obj = MyClass(source='/path/to/directory/or/file',
            verbose=False)
    >>> obj.metadata
    {
        'files': [
            {   
                'name': 'pdf-file-name.pdf', size: bytes,
                'relative': 'relative/path/to.pdf',
                'absolute': 'absolute/path/to.pdf',
                'sheets': total_sheets }) 
            },
        ],
        'processor' : 'processor-name',
        'ini': {
            'starting': datetime object,
            'ending': datetime object,
            'duration': deltatime object,
        },
    }
    >>> len(obj.sheets)
    int # total number of sheets
    '''

    @property
    def sheets(self):
        '''
        Property to store the list of sheets or pages in text \
        chain of the processed PDF files.

        >>> obj.sheets
        list # of strings
        '''
        return self._sheets
    
    @property
    def verbose(self):
        '''
        Property that defines whether the instance prints its \
        progress or results on the screen. This property is only \
        definable in the constructor of the class in the "verbose" \
        argument with a boolean value.

        >>> obj.verbose
        bool
        '''
        return self._verbose

    @property
    def metadata(self):
        '''
        Property that stores in a dictionary the metadata of the \
        processed documents ('files' key), the library used to process \
        it ('processor' key) and the initialization times ('ini' key).

        >>> obj.metadata
        {
            'files': [
                {   
                    'name': 'pdf-file-name.pdf', size: bytes,
                    'relative': 'relative/path/to.pdf',
                    'absolute': 'absolute/path/to.pdf',
                    'sheets': total_sheets }) 
                },
            ],
            'processor' : 'processor-name',
            'ini': {
                'starting': datetime object,
                'ending': datetime object,
                'duration': deltatime object,
            },
        }
        '''
        return self._metadata
        
    def pathfile_to_sheets(self, pathfile, depth=1):
        '''
        Method takes a valid path for a PDF file, uses a PDF processor, \
        and then returns a list with the sheets in text string.

        If a object is configured as verbose, that is to say property 
        :attr:`verbose <.DirFilePDFMixin.verbose>` is true, \
        it will print on the screen the process and details of the \
        extraction result. By default it will not print anything on screen.
        
        This method internally records metadata from file processing in \
        the :attr:`metadata <.DirFilePDFMixin.metadata>` property with \
        the "files" key.

        The 'depth' argument is for the indentation of the screen print \
        in case it is in verbose mode.

        Its manual use is not recommended but it is feasible, the method \
        is intended to be activated from the constructor.
        '''
        if not issubclass(pathfile.__class__, Path):
            raise TypeError('\'pathfile\' param must be Path subclass')
        relative = pathfile.relative_to('.')
        absolute = pathfile.absolute()
        if self.verbose:
            depth_flag = colors.LEAD('-'*depth)
            print(f'{depth_flag} Proccessing {colors.INFO(relative)} file')
        pdf = self.process_pdf(pathfile)
        size = pathfile.stat().st_size
        if self.verbose:
            print(f'{depth_flag} File size: {str(size)} bytes.')
        total_sheets = len(pdf)
        if self.verbose:
            print(f'{depth_flag} Extracting the content of '
                f'{colors.OK(str(total_sheets))} sheets')
            pdf = tqdm(pdf)
        sheetslist = []
        for i,sheet in enumerate(pdf):
            sheetslist.append(sheet)
            if self.verbose:
                pdf.set_description(
                    f'{depth_flag} > {i}/{str(total_sheets)} sheets')
        if not 'files' in self._metadata:
            self._metadata['files'] = []
        self._metadata['files'].append({
            'name':     pathfile.name,
            'size':     size,
            'relative': str(relative),
            'absolute': str(absolute),
            'sheets':   total_sheets}) 
        return sheetslist

    def path_to_sheets(self, path, depth=1, max_depth=5):
        '''
        Method receives a path that it searches for PDF files to apply method \
        :meth:`pathfile_to_sheets <.DirFilePDFMixin.pathfile_to_sheets>` to each one. \
        The result is returned in a single list of sheets.
        
        It applies recursion to go deeper into the directories using the 'depth' and \
        'max_depth' parameters. The 'depth' parameter indicates the depth in relation \
        to the first call, it also implements indentation on screen printing. The 'max_depth' \
        parameter determines the maximum depth in which to search for PDF files.

        Its manual use is not recommended but it is feasible, the method \
        is intended to be activated from the constructor.
        '''
        if not issubclass(path.__class__, Path):
            raise TypeError('\'path\' param must be Path subclass')
        sheets = []
        if self.verbose:
            dflag = colors.LEAD('-'*depth)
            relative = colors.INFO(path.relative_to("."))
            print(f'{dflag} Analyzing {relative} directory')
        for p in path.iterdir():
            relative = p.relative_to('.')
            if p.is_dir() and depth <= max_depth:
                if self.verbose:
                    print(f'{dflag}' + colors.LEAD(
                        f"> New directory: {relative}"))
                sheets += self.path_to_sheets(p, depth=depth+1)
            elif p.is_file() and p.suffix in ['.pdf', '.PDF']:
                if self.verbose:
                    print(f'{dflag}' + colors.OK("> PDF file founded")+\
                        f': {colors.INFO(relative)}')
                sheets += self.pathfile_to_sheets(p, depth=depth)
            elif self.verbose:
                print(f'{dflag}{colors.LEAD(f" | Omitted: ")}'\
                    +colors.LEAD(relative))
        return sheets

    def __init__(self, source, verbose=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # validate the type of source
        self._metadata = {}
        self._metadata['processor'] = self.processor_name
        self._metadata['init'] = {'starting': datetime.now()}
        if verbose:
            self._verbose = True
            print(colors.INFO(f'Initializing instance of {self.__class__.__name__}'))
            print(colors.LEAD(f"At {str(self._metadata['init']['starting'])}"))
            print(colors.LEAD(f'PDF Processor library: {self.processor_name}'))
        else:
            self._verbose = False
        if not isinstance(source, str):
            raise TypeError((
                f'{self.__class__.__name__} > ' 
                'the \'source\' param must be string '
                f'and not {source.__class__.__name__}.'))
        path = Path(source)
        if not path.exists():
            raise ValueError((
                f'{self.__class__.__name__} > '
                f'\'{source}\' path not exists.'))
        sheets = []
        # define if source is directory or pdf file
        if path.is_file() and path.suffix in ['.pdf', '.PDF']:
            self._sheets = self.pathfile_to_sheets(path)
        elif path.is_dir():
            if self.verbose:
                print(f'Source absolute path: {colors.INFO(path.absolute())}')
            self._sheets = self.path_to_sheets(path)
        self._metadata['init']['ending'] = datetime.now()
        ending   = self._metadata['init']['ending']
        starting = self._metadata['init']['starting']
        duration = ending - starting
        self._metadata['init']['duration'] = duration
        if self.verbose:
            print(colors.LEAD(f"Initialization complete at {ending}"))
            print(colors.LEAD(f"Duration time: {str(duration)} seconds"))
            print(colors.OK(f'Files processed: {len(self._metadata["files"])}'))
            for file in self._metadata['files']:
                print(colors.INFO(f'- file name \t: {file["name"]}'))
                print(colors.LEAD(f'-- size \t: {str(file["size"])} bytes'))
                print(colors.LEAD(f'-- path \t: {file["relative"]}'))
                print(colors.LEAD(f'-- sheets \t: {str(file["sheets"])}'))

