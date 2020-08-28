# builtin libraries
import sys

# internal modules
from .pdf_processors import PROCESSORS

# from pdfminer.high_level import extract_pages

# disables warinings of processors libs
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


class PDFProcessorMixin(*PROCESSORS):
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
     - `pdfminersix <https://pdfminersix.readthedocs.io/>`_ \
        (0.1.0 release) with :meth:`pdftotext_processor \
        <.ProcessorPDFMixin.processor_pdfminersix>`
    '''
    _processor = 'pdftotext'
    _tmp_file = None
    processor_ref = {
        'pdftotext':   'https://github.com/jalan/pdftotext',  # 0.1.0
        'pdfminersix': 'https://pdfminersix.readthedocs.io/',  # 0.1.0
        # dev note: add processors ref here {name:url}.
        }

    @property
    def processor(self):
        '''
        Processor (library) to extract text from pdf file.
        '''
        return self._processor

    @processor.setter
    def processor(self, value):
        if value in self.processor_ref:
            self._processor = value
            self._process_pdf = getattr(self, 'processor_'+value)
            self._process_pdf_page = getattr(self, 'processor_'+value+'_page')
            self._processor_name = value
            return None
        raise TypeError(
            f'{str(value)} must be a available '
            'processor: ' + ','.join(
                [x[0] for x in self.processors_ref.items()]))

    @property
    def process_pdf(self):
        '''
        Property that calls the method corresponding to the PDF file \
        processor configured in the instance initialization.

        >>> obj.process_pdf(*args)
        '''
        if self._tmp_file:
            self._tmp_file.close()  # ensure closing file.
            self._tmp_file = None
        return self._process_pdf

    @property
    def process_pdf_page(self):
        '''
        '''
        return self._process_pdf_page
