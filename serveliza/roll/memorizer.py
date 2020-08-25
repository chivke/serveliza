
class RollMemorizer:
    '''
    '''

    @property
    def storage(self):
        '''
        '''
        return self._storage

    @property
    def errors(self):
        '''
        '''
        return self._errors

    @property
    def is_active(self):
        '''
        '''
        return self._is_active

    def memorize(self, parsed):
        '''
        '''
        rid = parsed.metadata['rid']
        self.prepare_rid(parsed)
        self.store_metadata_places(parsed)
        self.store_metadata_entries(parsed)
        self.store_metadata_nulls(parsed)
        if self.is_active:
            self._storage[rid]['entries'] += parsed.entries
            self._errors += parsed.errors

    def prepare_rid(self, parsed):
        '''
        '''
        rid = parsed.metadata['rid']
        if rid in self.storage:
            return None
        metadata = {
            'roll': parsed.header['roll'],
            'year':     parsed.header['year'],
            'regions':      [],
            'communes':     [],
            'provinces':    [],
            'nulls': {'total': 0},
            'entries': {'total': 0, 'rescue': 0, 'errors': 0}}
        declared = parsed.header.get('total_sheets', False)
        if declared:
            metadata['entries']['declared'] = declared
        self._storage[rid] = {
            'entries':  [],
            'fields':   parsed.fields,
            'metadata': metadata}

    def store_metadata_places(self, parsed):
        '''
        '''
        rid = parsed.metadata['rid']
        region = parsed.header['region']
        regions = self.storage[rid]['metadata']['regions']
        province = parsed.header['province']
        provinces = self.storage[rid]['metadata']['provinces']
        commune = parsed.header['commune']
        communes = self.storage[rid]['metadata']['communes']
        if region not in regions:
            self._storage[rid]['metadata']['regions']\
                .append(region)
        if province not in provinces:
            self._storage[rid]['metadata']['provinces']\
                .append(province)
        if commune not in communes:
            self._storage[rid]['metadata']['communes']\
                .append(commune)

    def store_metadata_entries(self, parsed):
        '''
        '''
        rid = parsed.metadata['rid']
        entries = self.storage[rid]['metadata']['entries']
        pentries = parsed.metadata['entries']
        total = entries['total'] + len(parsed.entries)
        rescue = entries['rescue'] + pentries.get('rescue', 0)
        errors = entries['errors'] + len(parsed.errors)
        final_entries = {'total': total, 'rescue': rescue, 'errors': errors}
        declared = entries.get('declared', False)
        if declared:
            final_entries['declared'] = declared
        self._storage[rid]['metadata']['entries'] = final_entries

    def store_metadata_nulls(self, parsed):
        '''
        '''
        rid = parsed.metadata['rid']
        pnulls = parsed.metadata['nulls']
        if not pnulls['total']:
            return None
        nulls = self.storage[rid]['metadata']['nulls']
        total = nulls['total'] + pnulls['total']
        fields = parsed.metadata['fields']
        result = {'total': total}
        for field in fields:
            if field not in pnulls:
                continue
            result[field] = pnulls[field]
            if field in nulls:
                result[field] += nulls[field]
        self._storage[rid]['metadata']['nulls'].update(result)

    def __init__(self, *args, **kwargs):
        memorize = kwargs.get('memorize', True)
        self._is_active = bool(memorize)
        self._storage, self._errors = {}, []
