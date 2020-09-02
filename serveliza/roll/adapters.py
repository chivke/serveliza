
from pdfminer.layout import LTTextBoxHorizontal


class RollNoisedError(Exception):
    '''
    Exception that indicates an error when analyzing because the \
    pattern is noisy, that is, it has watermarks to prevent the \
    coherent extraction of text.
    '''
    pass


class PdftotextAdapterMixin:
    '''
    :class:`PdftotextAdapterMixin <.PdftotextAdapterMixin>` is an adapter for \
    the `pdftotext <https://github.com/jalan/pdftotext>`_ processor.

    It is a mixin designed to be inherited in :class:`RollAdapter \
    <.RollAdapter>`.
    '''

    def adapter_pdftotext(self, sheet):
        '''
        :param str sheet: sheet in text string.
        :raises ValueError: Unexpected type of sheet.
        :raises RollNoisedError: pdftotext processor cant process a \
            noised roll. Try with the pdfminersix processor.
        :return: sheet adapted.

        Method to adapt a sheet processed by `pdftotext \
        <https://github.com/jalan/pdftotext>`_ before being \
        passed to the parser.
        '''
        if not isinstance(sheet, str):
            raise ValueError('Unexpected type of sheet.')
        if len(sheet) > 100000:
            # indicate the pdf file is noised.
            raise RollNoisedError(
                'pdftotext processor cant process a noised roll. '
                'Try with the pdfminersix processor.')
        return sheet


class PdfminersixAdapterMixin:
    '''
    :class:`PdfminersixAdapterMixin <.PdfminersixAdapterMixin>` is an adapter \
    for the `pdfminersix <https://pdfminersix.readthedocs.io/>`_ processor.

    It is a mixin designed to be inherited in :class:`RollAdapter \
    <.RollAdapter>`.
    '''

    def adapter_pdfminersix(self, sheet):
        '''
        :param list sheet: sheet in list of pdfminersix elements.
        :return: sheet adapted in text string.

        Method to adapt a sheet processed by `pdfminersix \
        <https://pdfminersix.readthedocs.io/>`_ before being \
        passed to the parser.

        It is also capable of eliminating possible noise with watermarks.
        '''
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


ADAPTERS = [PdftotextAdapterMixin, PdfminersixAdapterMixin]


class RollAdapter(*ADAPTERS):
    '''
    :param obj sheet: sheet of the type according to the processor used.
    :param str processor: processor used in the sheet.

    :class:`RollAdapter <.RollAdapter>` is a class that is instantiated \
    for a sheet by routing it to the appropriate method according to \
    the processor defined in the constructor parameter of the same name.

    Practical use:

    >>> adapted = RollAdapted(processed_sheet, 'processor-name').sheet
    '''
    @property
    def sheet(self):
        '''
        Property where the adapted sheet is stored in the constructor.
        '''
        return self._sheet

    def __init__(self, sheet, processor, *args, **kwargs):
        if not isinstance(processor, str):
            raise ValueError('processor must be string.')
        adapter = getattr(self, 'adapter_'+processor, None)
        if not adapter:
            raise ValueError(f'Processor {processor} dont have valid method.')
        self._sheet = adapter(sheet)
