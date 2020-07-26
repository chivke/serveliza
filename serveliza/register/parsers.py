
import re

from datetime import datetime as dt
from slugify import slugify
import json


class SheetRegisterParser:
    '''
    Sheet electoral register parser.

    Sheet to parse must be provied in construtor \
    and be string.
    '''
    regex_begin = r'^REPUBLICA\s+DE\s+CHILE'
    regex_register = r'(PADRON\s+ELECTORAL\s+[A-Z]+)\s+-?\s+ELECCIONES'
    regex_election = r'ELECCIONES[A-Z,\s]+\d+'
    regex_region = r'REGION[0,]*\s*:\s*([A-Z\s]*\s{3})'
    regex_commune = r'COMUNA[0,]*\s*:\s*([A-Z\s]*\s{3})'
    regex_province = r'PROVINCIA[0,]*\s*:\s*([A-Z\s]*)'

    regex_name  = r'^[A-ZÑa-z\s]+' 
    regex_rut   = r'\d*\.?\d+\.\d+-[0-9kK]'
    regex_sex   = r'\sVAR\s|\sMUJ\s'
    regex_table = r'\s(\d+\s?\w?)\s*\d*$'

    dpa_fixture_path = 'serveliza/utils/fixtures/'\
        'DPA-commune-circuns.json'

    @property
    def sheet(self):
        return self._sheet

    @property
    def header(self):
        return self._header
    
    @property
    def fields(self):
        return self._fields
    
    @property
    def entries(self):
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
        start_at   = dt.now()
        self.decompose()
        header_at  = dt.now()
        self.parse_header()
        fields_at  = dt.now()
        self.parse_fields()
        entries_at = dt.now()
        self.parse_entries()
        finish_at = dt.now()
        times = {}
        times['total'] = finish_at - start_at
        times['parse-header'] = fields_at - header_at
        times['parse-fields'] = entries_at - fields_at
        times['parse-entries'] = finish_at - entries_at
        if not 'times' in self._metadata:
            self._metadata['times'] = {}
        self._metadata['times'].update(times)

    def parser(self, regex, target, ecode):
        parsed = re.findall(regex, target)
        if not bool(parsed):
            #import pdb; pdb.set_trace()
            self._errors.append( {
                'code'  : ecode,
                'regex' : regex,
                'target': target } )
            return None
        return parsed[0].strip()

    def parse_header(self):
        '''Return header data.'''
        header = {}
        # validate begin of sheet
        self.parser(self.regex_begin, self.sheet[0],
            'header-invalid-begin')
        # type of electoral register
        attributes = [
            ('register', self.sheet[0]),
            ('election', self.sheet[0]),
            ('region',   self.sheet[1]+self.sheet[2]),
            ('commune',  self.sheet[1]+self.sheet[2]),
            ('province', self.sheet[2]+'--'+self.sheet[3])]
        for key,target in attributes:
            header[key] = self.parser(
                regex=getattr(self,'regex_'+key),
                target=target, ecode='header-no-'+key )
        header['year'] = int( self.parser(r'\d+$', 
            header['election'], 'header-no-year') )
        id_reg = ''.join( [w[0] for w in header['register']\
            .split(' ') ])
        id_ele = re.sub(r'[0-9Y]','',''.join(
            [w[0] for w in header['election'].split(' ') ]) )
        identify = f'{id_reg}-{id_ele}-{str(header["year"])}'
        # load header to de property
        self._header = header
        self._metadata['rid'] = identify
        # load valid circunscriptions
        with open(self.dpa_fixture_path) as f:
            fixture = json.load(f)
        if header['commune'] in fixture:
            self._circuns = fixture[header['commune']]
        else:
            self._errors.append( {
            'code'  : 'commune-not-in-fixture',
            'fixture': self.dpa_fixture_path,
            'target': header['commune'] } )

    def get_fields_index(self):
        if self.fields_index:
            return self.fields_index
        regex = r'^NOMBRE\s+C'
        for idx,line in enumerate(self.sheet):
            if re.match(regex, line):
                self._fields_index = idx
                return idx
        self._errors.append( {
            'code'  : 'fields-no-index',
            'regex' : regex,
            'target': self.sheet } )

    def parse_fields(self):
        index = self.get_fields_index()
        if not index:
            return None
        fields_line = self.sheet[index]
        fields_line = fields_line.replace(
            'LIO ELE', 'LIO-ELE')
        self._fields = list(map(lambda x: slugify(x), 
            fields_line.split()) )
        self._fields.insert(3, 'comuna')
        self._fields.insert(3, 'provincia')
        self._fields.insert(3, 'region')

    def parse_entries(self):
        index = self.get_fields_index() + 1
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
            else:
                import pdb; pdb.set_trace()
        #self._entries = entries
        total_entries = len(entries)
        self._metadata['entries-total'] = total_entries
        if malformed:
            # try to take entry again
            pentries = []
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
                        'code'  : 'malformed-no-start',
                        'target': txt } )
            for e in pentries:
                entry = self.parse_entry(e)
                if not entry:
                    self._errors.append({
                        'code'  : 'malformed-no-entry',
                        'target': e } )
                else:
                    entries.append(entry)
            self._metadata['entries-rescue'] = len(entries) - total_entries
            self._metadata['entries-total'] += self._metadata['entries-rescue']
        self._entries = entries

    def parse_entry(self, line):
        entry = []
        first_fields = ['name','rut','sex','circun','table']
        dir_ini = None
        dir_end = None
        for key in first_fields:
            value = None
            if key == 'circun':
                for cir in self.circuns:
                    if cir in line:
                        value = cir
            else:
                value = self.parser(
                    regex=getattr(self, 'regex_'+key),
                    target=line, ecode='entry-'+key)
            if value:
                if key == 'sex':
                    dir_ini = re.search(value, line).end()
                elif key == 'circun':
                    dir_end = re.search(value, line).start()
            else:
                self._metadata['nulls-total'] += 1
                if not 'nulls-'+key in self._metadata:
                    self._metadata['nulls-'+key] = 1
                else:
                    self._metadata['nulls-'+key] += 1
            entry.append(value)
        # electoral direction
        direction = None
        if dir_ini and dir_end:
            direction = line[dir_ini:dir_end].strip()
        else:
            self._metadata['nulls-total'] += 1
            if not 'nulls-dir' in self._metadata:
                self._metadata['nulls-dir'] = 1
            else:
                self._metadata['nulls-dir'] += 1
        entry.insert(3, direction)
        entry.insert(3, self.header['commune'])
        entry.insert(3, self.header['province'])
        entry.insert(3, self.header['region'])
        return entry

    def __init__(self, sheet, auto=True, *args, **kwargs):
        if not isinstance(sheet, str):
            raise TypeError('\'sheet\' arg must be string')
        self._decomposed = False
        self._metadata = { 
            'nulls-total' :  0,
            'entries-total': 0,
            'entries-rescue':0,}
        self._sheet = sheet
        self._header = {}
        self._fields = []
        self._entries = []
        self._errors = []
        self._fields_index = None
        self._circuns_of = None
        if auto:
            self.run()