# builtin libraries
import os
import re
import json
from datetime import datetime as dt

# third party libraries
from slugify import slugify


class RollParser:
    '''
    :class:`RollParser <.RollParser>` is intended to be instantiated \
    by each sheet.

    Class attributes beginning with "*regex_*" correspond to the regular \
    expressions used to detect fields in the header. The *regexs_entries* \
    class attribute contains a dictionary with the regular expressions \
    for the fields in each record and a key name for each. Finally, the \
    *dpa_fixture_path* class attribute defines the path of the .json file \
    that contains a compressed dictionary with communes and constituencies.
    '''
    # regex_begin = r'^REPUBLICA\s+DE\s+CHILE'
    #: roll name regex
    regex_roll = r'PADRO?Ó?N\s+ELECTORAL\s+[A-Z,\s-]+\d+'
    #: region regex
    regex_region = r'REGIO?Ó?N[0,]*\s*:\s*([A-ZÑ\'\s.]*\s{3})'
    #: commune regex
    regex_commune = r'COMUNA[0,]*\s*:\s*([A-ZÑ\' ]*\s{3})'
    #: province regex
    regex_province = r'PROVINCIA[0,]*\s*:\s*([A-ZÑ\' ]*)'
    #: total entries regex (optional)
    regex_total_entries = r'Registros\s*:\s*(\d+)'
    #: pagination regex (optional)
    regex_pagination = r'[PAaáGgIiNn]+\s*:?\s*(\d*)\s*de\s*(\d*)'
    #: regex's for parsing entries.
    regexs_entries = {
        'name': r'^[A-ZÑa-z\s]+',
        'rut': r'\d*\.?\d+\.\d+-[0-9kK]',
        'sex': r'\s(VAR|MUJ)[ONER]*\s',
        'table': r'\s(\d+\s?\w?)\s*\d*$'}
    #: path to commune-circuns json.
    dpa_fixture_path = '../utils/fixtures/'\
        'DPA-commune-circuns.json'

    def run(self):
        '''
        Method that starts the voter registry sheet analyzer by executing:
        * :meth:`decompose <.RollParser.decompose>`
        * :meth:`parse_header <.RollParser.parse_header>`
        * :meth:`parse_fields <.RollParser.parse_fields>`
        * :meth:`parse_entries <.RollParser.parse_entries>`

        It measures the duration times of each method executed and saves \
        them in the :attr:`metadata[times] <.RollParser.metadata>` \
        property.
        '''
        self.decompose()
        header_at = dt.now()
        self.parse_header()
        fields_at = dt.now()
        self.parse_fields()
        entries_at = dt.now()
        self.parse_entries()
        finish_at = dt.now()
        times = {
            'header': fields_at - header_at,
            'fields': entries_at - fields_at,
            'entries': finish_at - entries_at}
        times['total'] = times['header'] + times['fields'] + times['entries']
        if 'times' not in self._metadata:
            self._metadata['times'] = {}
        self._metadata['times'].update(times)

    def decompose(self):
        '''
        Method that descompose a :attr:`sheet <.RollParser.sheet>` \
        of the electoral roll in a text string into a list with each line.
        '''
        if not self.is_decomposed:
            self._sheet = self._sheet.split('\n')

    @property
    def is_decomposed(self):
        '''
        :return: boolean.

        Property that indicates whether the '*sheet*' property is decomposed \
        into a list of lines or not.
        '''
        return isinstance(self.sheet, list)

    @property
    def sheet(self):
        '''
        Property that contains a text string of the entire sheet to parse or \
        the list of text lines if it is decomposed.

        >>> parser.is_descomposed
        False
        >>> parser.sheet
        'text-\\n-string'
        >>> parser.descompose
        >>> parser.sheet
        ['text-', '-string']
        '''
        return self._sheet

    def parse_header(self):
        '''
        Method that parses the head of the sheet and extracts the data \
        from *roll*, *election*, *year*, *region*, *province* and \
        *commune* to store it in the :attr:`header \
        <.RollParser.header>` property.

        It also builds a unique identifier of the electoral roll that \
        it stores in the :attr:`metadata <.RollParser.metadata>` \
        property with the *rid* key.
        '''
        def __identify(header):
            id_roll = re.sub(r'[0-9\tYa-z]', '', ''.join(
                [w[0] for w in header['roll'].split(' ') if len(w) > 2]))
            return f'{id_roll}-{str(header["year"])}'
        idx = self.__get_fields_index()
        target = ' \t '.join(self.sheet[:idx])
        attributes = ['roll', 'region', 'commune', 'province']
        header = {}
        for attr in attributes:
            header[attr] = self.__parser(
                regex=getattr(self, 'regex_'+attr),
                target=target, ecode='header-no-'+attr)
        year = self.__parser(
            r'\d+$', header['roll'], 'header-no-year')
        if year:
            header['year'] = int(year)
        total_entries = re.findall(self.regex_total_entries, target)
        if total_entries:
            header['total_entries'] = int(total_entries[0].strip())
        pagination = re.findall(self.regex_pagination, target)
        if pagination and len(pagination[0]) > 2 and pagination[0]:
            header['pagination'] = pagination[0]
        self._metadata['rid'] = __identify(header)
        self._header = header
        with open(os.path.dirname(__file__)+'/'+self.dpa_fixture_path) as f:
            fixture = json.load(f)
        if 'PAGINA' in header['commune']:
            header['commune'] = header['commune'].replace('PAGINA', '').strip()
        if header['commune'] in fixture:
            self._circuns = fixture[header['commune']]
        else:
            self._circuns = None
            self._errors.append({
                'code': 'commune-not-in-fixture',
                'fixture': self.dpa_fixture_path,
                'target': header['commune']})

    @property
    def header(self):
        '''
        Property that contains the result of method :meth:`parse_header \
        <.SheetRollParser.parse_header>`. It consists of a \
        dictionary with the data from the header of the electoral roll sheet.

        >>> parser.header
        {
            'roll': 'PADRON...',
            'election': 'ELECCION...',
            'year':     2020,
            'region':   'METRO...',
            'commune':  'SANTIA...',
            'province': 'SANTIA...',
        }
        '''
        return self._header

    def parse_fields(self):
        '''
        Method to analyze and extract the fields of the electoral roll. \
        The direct fields of the sheet (*nombre*, *c-identidad*, *sex|o*, \
        *domicilio-electoral*, *circunscripcion* y *mesa*) are taken and \
        commune, province and region (*comuna*, *provincia*, *region*) are \
        added. Result is stored in the :attr:`fields \
        <.RollParser.fields>` property, the method returns nothing.
        '''
        index = self.__get_fields_index()
        if not index:
            return None
        fields_line = self.sheet[index]
        fields_line = fields_line.replace(
            'LIO ELE', 'LIO-ELE')
        self._fields = list(map(
            lambda x: slugify(x),
            fields_line.split()))
        if self.more_fields:
            self._fields.insert(3, 'comuna')
            self._fields.insert(3, 'provincia')
            self._fields.insert(3, 'region')
            self._fields.append('reference')

    @property
    def fields(self):
        '''
        Property that contains the fields of the electoral roll \
        detected in the sheet through the :meth:`parse_fields \
        <.RollParser.parse_fields>` method.
        '''
        return self._fields

    def parse_entries(self):
        '''
        Method that analyzes and extracts each data entry from the voter \
        registration sheet.

        First determine if each line of text is well composed, that is, \
        it begins with at least one letter and ends with a number or a space \
        next to a single letter. Then each line of text is analyzed as if it \
        were an input through the :meth:`parse_entry \
        <.RollParser.parse_entry>` method.

        Afterwards, the lines considered malformed are internally processed, \
        joining them in relation to whether they start with a letter or a \
        space. Then use the :meth:`parse_entry \
        <.RollParser.parse_entry>` method again for each of them. \
        Those that are rescued will remain in the :attr:`metadata \
        <.RollParser.metadata>` property in the keys *entires* > \
        *rescue*.
        '''
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
        self._metadata['entries']['errors'] = len(self.errors)
        self._metadata['entries']['total'] = total_entries
        self._entries = entries

    def parse_entry(self, line):
        '''
        A method that extracts the data from a voter registry entry in text \
        line format.

        Finds the fields found by regular expressions that are stored in the \
        class attribute: :attr: `regexs_entries \
        <.RollParser.regexs_entries>`.

        Then it looks for the district from a list according to its commune \
        and in relation to this it determines the place of the electoral \
        domicile.
        '''
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
            largest = len(sorted(self.circuns, key=lambda x: len(x))[-1])
            table_position = re.search(
                r'\s*'+self.regexs_entries['table'], line)
            if not table_position:
                table_position = 150
            else:
                table_position = table_position.start()
            cut = table_position - largest
            value = [c for c in self.circuns if c+'  ' in line[cut:]]
            if not value:
                value = [c for c in self.circuns if c in line[cut:]]
                if value and len(value) == 1:
                    return value[0]
                self._errors.append({
                    'code': 'entry-' + field + '-not-found',
                    'circuns': self.circuns,
                    'target': line})
                if field not in self._metadata['nulls']:
                    self._metadata['nulls'][field] = 1
                else:
                    self._metadata['nulls'][field] += 1
                return None
            return value[0]

        def __parse_dir(line, sex, circun, field):
            ini = re.search(sex, line)
            end = re.search(
                str(circun) + r'\s*' + self.regexs_entries['table'], line)
            if not end:
                end = -1
            else:
                end = end.start()
            if not ini:
                self._errors.append({
                    'code': 'entry-' + field + '-not-found',
                    'reason': 'sex end not found',
                    'target': line})
            else:
                ini = ini.end()
                direction = line[ini:end].strip()
                if direction:
                    return direction
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
        direction = __parse_dir(
            line, self.regexs_entries['sex'], circun, self.fields[-3])
        entry.insert(3, direction)
        if self.more_fields:
            entry.insert(3, self.header['commune'])
            entry.insert(3, self.header['province'])
            entry.insert(3, self.header['region'])
            reference = self.metadata['rid']
            reference += '-' + slugify(self.header['commune'])
            if 'pagination' in self.header:
                pag = self.header['pagination']
                reference += '-page-' + str(pag[0]) + '-of-' + str(pag[1])
            entry.append(reference)
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
        parsed = re.findall(regex, target) if isinstance(target, str) else None
        if not bool(parsed):
            self._errors.append({
                'code': ecode,
                'regex': regex,
                'target': target})
            return None
        return re.sub(r'\s+', ' ', parsed[0].strip())

    @property
    def entries(self):
        '''
        Property containing a list of entries from the electoral roll \
        sheet. Each entry corresponds to a list of data in the order of the \
        fields defined in the :attr:`fields <RollParser.fields>` \
        property.
        '''
        return self._entries

    @property
    def metadata(self):
        '''
        Property contains the metadata extracted during the parser analysis \
        of the electoral roll sheet.

        The metadata is stored as a dictionary, the *rid* key \
        corresponding to the unique identifier of the voter registry of the \
        sheet, the *times* key stores how long the analysis took (in \
        total, during header, fields and entries), the *entries* key \
        contains the total number of entries extracted , the amount of \
        rescued and errors. Finally, the NULLS key contains the total \
        number of null data inside each row or entry, as well as the detail \
        of the fields, if there is any.

        >>> parser.metadata
        {
            'rid': 'PEA-EM-2016',
            'entries': {'total': 1, 'rescue': 0, 'errors': 0},
            'nulls': {'total': 0}
        }
        '''
        return self._metadata

    @property
    def errors(self):
        '''
        Property contains a list with the errors found in the sheet analysis. \
        Each error corresponds to a dictionary with at least two keys: \
        *code* with a semantic slug text of the error and '*target*' that \
        contains what generated the error.
        '''
        return self._errors

    @property
    def fields_index(self):
        '''
        Property that contains the index where the fields are located in the \
        decomposed sheet as a list.
        '''
        return self._fields_index

    @property
    def circuns(self):
        '''
        :return: a dictionary with communes as key and list of \
            circunscriptions as value.

        Property that contains the possible electoral circunscriptions \
        within the commune defined in the :attr:`header \
        <.RollParser.header>` property. It will return None if \
        the :meth:`parse_header <.RollParser.parse_header>` \
        method has not been executed.
        '''
        return self._circuns

    @property
    def more_fields(self):
        '''
        :return: boolean.

        Property where the option of whether to add fields to the \
        input is stored.
        '''
        return self._more_fields

    def __launch_props(self):
        self._fields_index = None
        self._metadata = {}
        self._header = {}
        self._fields = []
        self._entries = []
        self._errors = []

    def __init__(self, sheet, auto=True, more_fields=True, *args, **kwargs):
        if not isinstance(sheet, str) or not sheet:
            raise TypeError('\'sheet\' arg must be string')
        self._more_fields = bool(more_fields)
        self.__launch_props()
        self._sheet = sheet
        if auto:
            self.run()
