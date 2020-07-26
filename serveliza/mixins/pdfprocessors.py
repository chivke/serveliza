
import pdftotext

class ProcesorsPDFMixin:
    '''
    Mixin with the instance method \
    :meth:`process_pdf <.ProcessorsPDFMixin.process_pdf>`.

    This method uses the processor library specify in \
    the constructor \'processor\' argumment.
    '''
    _processors_availables = ['pdftotext']

    @property
    def process_pdf(self):
        return self._process_pdf
    
    @property
    def processor_module(self):
        return self._processor_module
    
    def pdftotext_processor(self, pathfile):
        with open(pathfile, "rb") as f:
            pdf = pdftotext.PDF(f)
        return pdf

    def __init__(self, processor='pdftotext',*args, **kwargs):
        if not processor in self._processors_availables:
            raise TypeError(f'{str(processor)} must be a available '
                f'processor {str(self._processors_availables)}')
        if processor == 'pdftotext':
            self._process_pdf = self.pdftotext_processor
            self._processor_module = pdftotext.__name__
