
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from ..utils import colors
from .pdfprocessors import ProcesorsPDFMixin

class DirFilePDFMixin(ProcesorsPDFMixin):
    '''
    Mixin to add capability an istance to \
    process PDF directory or file and unify \
    in to \'sheets\' property.
    '''

    @property
    def sheets(self):
        '''
        Property to storage a list of raw \
        string pages of processed pdf(s) file(s).
        '''
        return self._sheets
    
    @property
    def verbose(self):
        '''
        Property to define if the instance print \
        in console the progress of process.
        '''
        return self._verbose

    @property
    def metadata(self):
        '''
        Property to storage the metadata of files \
        or other util information.
        '''
        return self._metadata
        
    def pathfile_to_sheetslist(self, pathfile, depth=1):
        '''Method to take sheets of PDF file path'''
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

    def path_to_sheetslist(self, path, depth=1, max_depth=5):
        '''Method to take sheetlist of pdf available in directory'''
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
                sheets += self.path_to_sheetslist(p, depth=depth+1)
            elif p.is_file() and p.suffix in ['.pdf', '.PDF']:
                if self.verbose:
                    print(f'{dflag}' + colors.OK("> PDF file founded")+\
                        f': {colors.INFO(relative)}')
                sheets += self.pathfile_to_sheetslist(p, depth=depth)
            elif self.verbose:
                print(f'{dflag}{colors.LEAD(f" | Omitted: ")}'\
                    +colors.LEAD(relative))
        return sheets

    def __init__(self, source, verbose=False, *args, **kwargs):
        '''Constructor of :class:<.DirFileMixin>'''
        super().__init__(*args, **kwargs)
        # validate the type of source
        self._metadata = {}
        self._metadata['processor'] = self.processor_module
        self._metadata['init'] = {'starting': datetime.now()}
        if verbose:
            self._verbose = True
            print(colors.INFO(f'Initializing instance of {self.__class__.__name__}'))
            print(colors.LEAD(f"At {str(self._metadata['init']['starting'])}"))
            print(colors.LEAD(f'PDF Processor library: {self.processor_module}'))
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
            self._sheets = self.pathfile_to_sheetslist(path)
        elif path.is_dir():
            if self.verbose:
                print(f'Source absolute path: {colors.INFO(path.absolute())}')
            self._sheets = self.path_to_sheetslist(path)
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

