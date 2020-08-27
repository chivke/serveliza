
from pdfminer.layout import LTTextBoxHorizontal


class RollNoisedError(Exception):
    pass


class PdftotextAdapterMixin:
    '''
    '''

    def adapter_pdftotext(self, sheet):
        if not isinstance(sheet, str):
            raise ValueError('Unexpected type of sheet.')
        if len(sheet) > 100000:
            # indicate the pdf file is noised.
            raise RollNoisedError(
                'pdftotext processor cant process a noised roll. '
                'Try with the pdfminer processor.')
        return sheet


class PdfminerAdapterMixin:
    '''
    '''

    def adapter_pdfminersix(self, sheet):
        # purge the noise
        filtered = [x for x in sheet if isinstance(
            x, LTTextBoxHorizontal) and x.bbox[0] > 0]
        # group header & columns
        layout = {}
        elements = []
        for element in filtered:
            elements += [x for x in element]
        for element in elements:
            if element.bbox[1] not in layout:
                layout[element.bbox[1]] = [element]
            else:
                layout[element.bbox[1]].append(element)
        # ordering and serialization
        for height in layout:
            layout[height].sort(key=lambda x: x.bbox[0])
            stringed = ' \t '.join([x.get_text(
                ).replace('\n', '') for x in layout[height]]) + '\n'
            layout[height] = stringed
        # return in one string
        return ''.join([x[1] for x in sorted(
            layout.items(), key=lambda x:x[0], reverse=True)])


ADAPTERS = [PdftotextAdapterMixin, PdfminerAdapterMixin]


class RollAdapter(*ADAPTERS):
    '''
    '''
    @property
    def sheet(self):
        return self._sheet

    def __init__(self, sheet, processor, *args, **kwargs):
        if not isinstance(processor, str):
            raise ValueError('processor must be string.')
        adapter = getattr(self, 'adapter_'+processor, None)
        if not adapter:
            raise ValueError(f'Processor {processor} dont have valid method.')
        self._sheet = adapter(sheet)
