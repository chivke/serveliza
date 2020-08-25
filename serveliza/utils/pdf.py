from pathlib import Path
from datetime import datetime


def is_valid_pdf(pathfile, raise_exception=False):
    '''
    '''
    path = Path(str(pathfile))
    msg, valid = '', False
    if not path.exists():
        msg = 'Path no exists.'
    elif not path.is_file():
        msg = 'Path is not a file.'
    elif path.suffix not in ['.pdf', '.PDF']:
        msg = 'Path dont have pdf suffix.'
    else:  # valid pdf
        valid = True
    if not valid and raise_exception:
        raise TypeError(msg)
    return valid


def get_all_pdf_in_path(path, recursively=False):
    '''
    '''
    pattern = '**/*' if recursively else '*'
    return [x for x in Path(path).glob(pattern) if x.is_file()
            and x.suffix in ['.pdf', '.PDF']]


def get_metadata_from_pdfs(filelist, output='dict'):
    '''
    '''
    if not isinstance(filelist, list) or output not in ['dict', 'list']:
        TypeError('filelist must be list and output '
                  'must be \'dict\' or \'list\'')
    metadata = []
    for pdf in filelist:
        path = Path(pdf)
        meta = {
            'name': path.name, 'bytes': path.stat().st_size,
            'relative': str(path.relative_to('.')),
            'absolute': str(path.absolute()),
            'mtime': datetime.fromtimestamp(path.stat().st_mtime),
            'atime': datetime.fromtimestamp(path.stat().st_mtime),
            }
        metadata.append(meta)
    if output == 'list':
        return metadata
    elif output == 'dict':
        dict_metadata = {}
        for meta in metadata:
            dict_metadata[meta['name']] = meta
        return dict_metadata
