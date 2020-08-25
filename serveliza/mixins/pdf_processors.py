# PDF processors libraries:
# --------------------------
import pdftotext
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator


class PdftotextMixin:
    '''
    '''
    def processor_pdftotext(self, pathfile):
        '''
        Method to use `pdftotext <https://github.com/jalan/pdftotext>`_ \
        in a file specified in the argument as a path.

        >>> obj.processor_pdftotext('/path/to/file.pdf')
        list # without processing
        '''
        self._tmp_file = open(str(pathfile), 'rb')
        return pdftotext.PDF(self._tmp_file)

    def processor_pdftotext_page(self, page):
        '''pdftotext not need that.'''
        return page


class PdfminersixMixin:
    '''
    '''
    def processor_pdfminersix(self, pathfile):
        '''
        '''
        self._tmp_file = open(str(pathfile), 'rb')
        return [x for x in PDFPage.get_pages(self._tmp_file)]

    def processor_pdfminersix_page(self, page):
        '''
        '''
        resource_manager = PDFResourceManager()
        device = PDFPageAggregator(resource_manager, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, device)
        interpreter.process_page(page)
        return device.get_result()


PROCESSORS = [PdftotextMixin, PdfminersixMixin]
