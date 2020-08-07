'''
Register parsers
-----------------

:mod:`serveliza.register.parsers`

Contains parser class for electoral register.
'''

# builtin libraries
import re
import json
from datetime import datetime as dt

# third party libraries
from slugify import slugify


class SheetRegisterParser:
    '''
    Parser is intended to be instantiated by each sheet.

    Class attributes beginning with "*regex_*" correspond to the regular \
    expressions used to detect fields in the header. The *regexs_entries* \
    class attribute contains a dictionary with the regular expressions \
    for the fields in each record and a key name for each. Finally, the \
    *dpa_fixture_path* class attribute defines the path of the .json file \
    that contains a compressed dictionary with communes and constituencies.
    '''

    regex_begin = r'^REPUBLICA\s+DE\s+CHILE'
    regex_register = r'(PADRON\s+ELECTORAL\s+[A-Z]+)\s+-?\s+ELECCIONES'
    regex_election = r'ELECCIONES[A-Z,\s]+\d+'
    regex_region = r'REGION[0,]*\s*:\s*([A-Z\s.]*\s{3})'
    regex_commune = r'COMUNA[0,]*\s*:\s*([A-Z\s]*\s{3})'
    regex_province = r'PROVINCIA[0,]*\s*:\s*([A-Z\s]*)'

    regexs_entries = {
        'name': r'^[A-ZÑa-z\s]+',
        'rut': r'\d*\.?\d+\.\d+-[0-9kK]',
        'sex': r'\sVAR\s|\sMUJ\s',
        'table': r'\s(\d+\s?\w?)\s*\d*$'}

    dpa_fixture_path = 'serveliza/utils/fixtures/'\
        'DPA-commune-circuns.json'

    # Properties
    # -----------
    #
    @property
    def sheet(self):
        '''
        Property that contains a text string of the entire sheet to parse or \
        the list of text lines if it is decomposed.

        >>> parser.sheet
        '...' | ['...', '...']
        '''
        return self._sheet

    @property
    def header(self):
        '''
        Property that contains the result of method :meth:`parse_header \
        <.SheetRegisterParser.parse_header>`. It consists of a \
        dictionary with the data from the header of the electoral roll sheet.

        >>> parser.header
        {
            'register': 'PADRON...',
            'election': 'ELECCION...',
            'year':     2020,
            'region':   'METRO...',
            'commune':  'SANTIA...',
            'province': 'SANTIA...',
        }
        '''
        return self._header

    @property
    def fields(self):
        '''
        Property that contains the fields of the electoral register \
        detected in the sheet through the :meth:`parse_fields \
        <.SheetRegisterParser.parse_fields` method.
        '''
        return self._fields

    @property
    def entries(self):
        '''
        Property containing a list of entries from the electoral register \
        sheet. Each entry corresponds to a list of data in the order of the \
        fields defined in the :attr:`fields <SheetRegisterParser.fields>` \
        property.
        '''
        return self._entries

    @property
    def metadata(self):
        return self._metadata

    @property
    def errors(self):
        return self._errors

    @property
    def has_errors(self):
        return bool(self._errors)

    @property
    def decomposed(self):
        return self._decomposed

    @property
    def fields_index(self):
        return self._fields_index

    @property
    def circuns(self):
        return self._circuns

    def decompose(self):
        '''
        Method to decompose raw sheet in to \
        list of lines.
        '''
        if not self.decomposed:
            self._sheet = self._sheet.split('\n')
            self._decomposed = True

    def run(self):
        start_at = dt.now()
        self.decompose()
        header_at = dt.now()
        self.parse_header()
        fields_at = dt.now()
        self.parse_fields()
        entries_at = dt.now()
        self.parse_entries()
        finish_at = dt.now()
        times = {
            'total': finish_at - start_at,
            'header': fields_at - header_at,
            'fields': entries_at - fields_at,
            'entries': finish_at - entries_at}
        if 'times' not in self._metadata:
            self._metadata['times'] = {}
        self._metadata['times'].update(times)

    def parse_header(self):
        '''
        Return header data.
        '''
        def __identify(header):
            id_reg = ''.join([w[0] for w in header['register'].split(' ')])
            id_ele = re.sub(r'[0-9Y]', '', ''.join(
                [w[0] for w in header['election'].split(' ')]))
            return f'{id_reg}-{id_ele}-{str(header["year"])}'
        self.__parser(
            self.regex_begin, self.sheet[0],
            'header-invalid-begin')
        attributes = [
            ('register', self.sheet[0]),
            ('election', self.sheet[0]),
            ('region',   self.sheet[1]+self.sheet[2]),
            ('commune',  self.sheet[1]+self.sheet[2]),
            ('province', self.sheet[2]+'--'+self.sheet[3])]
        header = {}
        for key, target in attributes:
            header[key] = self.__parser(
                regex=getattr(self, 'regex_'+key),
                target=target, ecode='header-no-'+key)
        header['year'] = int(self.__parser(
            r'\d+$', header['election'], 'header-no-year'))
        self._metadata['rid'] = __identify(header)
        self._header = header
        with open(self.dpa_fixture_path) as f:
            fixture = json.load(f)
        if header['commune'] in fixture:
            self._circuns = fixture[header['commune']]
        else:
            self._circuns = None
            self._errors.append({
                'code': 'commune-not-in-fixture',
                'fixture': self.dpa_fixture_path,
                'target': header['commune']})

    def parse_fields(self):
        index = self.__get_fields_index()
        if not index:
            return None
        fields_line = self.sheet[index]
        fields_line = fields_line.replace(
            'LIO ELE', 'LIO-ELE')
        self._fields = list(map(
            lambda x: slugify(x),
            fields_line.split()))
        self._fields.insert(3, 'comuna')
        self._fields.insert(3, 'provincia')
        self._fields.insert(3, 'region')

    def parse_entries(self):
        index = self.__get_fields_index() + 1
        if not index:
            return None
        entries = []
        malformed = []
        for line in self.sheet[index:]:
            if not re.match(r'^\w+.+\d+\s?\w?$', line):
                if line.strip():
                    malformed.append(line)
                continue
            entry = self.parse_entry(line)
            if entry:
                entries.append(entry)
        total_entries = len(entries)
        self.metadata['entries'] = {}
        if malformed:
            # try to take entry again
            rescue_entries = self.__rescue_entries(malformed)
            entries += rescue_entries
            self._metadata['entries']['rescue'] = len(entries) - total_entries
            total_entries = len(entries)
        self._metadata['entries']['total'] = total_entries
        self._entries = entries

    def parse_entry(self, line):
        def __regex_fields(line, fields):
            attr_fields = ['name', 'rut', 'sex', 'table']
            fields = [fields[0], fields[1], fields[2], fields[-1]]
            values = []
            for idx, field in enumerate(fields):
                value = self.__parser(
                    regex=self.regexs_entries[attr_fields[idx]],
                    target=line, ecode='entry-'+field)
                values.append(value)
                if not value:
                    if field not in self._metadata['nulls']:
                        self._metadata['nulls'][field] = 1
                    else:
                        self._metadata['nulls'][field] += 1
            return values

        def __parse_circun(line, field):
            value = None
            for cir in self.circuns:
                if cir in line:
                    value = cir
            if not value:
                self._errors.append({
                    'code': 'entry-' + field + '-not-found',
                    'circuns': self.circuns,
                    'target': line})
                if field not in self._metadata['nulls']:
                    self._metadata['nulls'][field] = 1
                else:
                    self._metadata['nulls'][field] += 1
            return value

        def __parse_dir(line, sex, circun, field):
            ini = re.search(sex, line).end()
            end = re.search(circun, line).start()
            if ini and end:
                return line[ini:end].strip()
            else:
                self._errors.append({
                    'code': 'entry-' + field + '-not-found',
                    'reason': 'sex end and circun init not found',
                    'target': line})
                if field not in self._metadata['nulls']:
                    self._metadata['nulls'][field] = 1
                else:
                    self._metadata['nulls'][field] += 1

        if 'nulls' not in self.metadata:
            self._metadata['nulls'] = {'total': 0}
        regex_vals = __regex_fields(line, self.fields)
        entry = regex_vals
        circun = __parse_circun(line, self.fields[-2])
        entry.insert(3, circun)
        direction = __parse_dir(line, regex_vals[2], circun, self.fields[-3])
        entry.insert(3, direction)
        entry.insert(3, self.header['commune'])
        entry.insert(3, self.header['province'])
        entry.insert(3, self.header['region'])
        return entry

    def __rescue_entries(self, malformed):
        pentries = []
        entries = []
        lastentry = ''
        for txt in malformed:
            if re.match(r'^\w+', txt):
                if lastentry:
                    pentries.append(lastentry)
                lastentry = txt
            elif lastentry:
                lastentry += txt
            else:
                self._errors.append({
                    'code': 'malformed-no-start',
                    'target': txt})
        for e in pentries:
            entry = self.parse_entry(e)
            if not entry:
                self._errors.append({
                    'code': 'malformed-no-entry',
                    'target': e})
            else:
                entries.append(entry)
        return entries

    def __get_fields_index(self):
        if self.fields_index:
            return self.fields_index
        regex = r'^NOMBRE\s+C'
        for idx, line in enumerate(self.sheet):
            if re.match(regex, line):
                self._fields_index = idx
                return idx
        self._errors.append({
            'code': 'fields-no-index',
            'regex': regex,
            'target': self.sheet})

    def __parser(self, regex, target, ecode):
        parsed = re.findall(regex, target)
        if not bool(parsed):
            self._errors.append({
                'code': ecode,
                'regex': regex,
                'target': target})
            return None
        return parsed[0].strip()

    def __launch_props(self):
        self._decomposed = False
        self._fields_index = None
        self._metadata = {}
        self._header = {}
        self._fields = []
        self._entries = []
        self._errors = []

    def __init__(self, sheet, auto=True, *args, **kwargs):
        if not isinstance(sheet, str):
            raise TypeError('\'sheet\' arg must be string')
        self.__launch_props()
        self._sheet = sheet
        if auto:
            self.run()
