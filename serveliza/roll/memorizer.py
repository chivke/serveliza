
class RollMemorizer:
    '''
    :param bool memorize: If the memorizer is activated (default True)

    :class:`RollMemorizer <.RollMemorizer>` is a class that allows it \
    to store data and errors from the electoral roll. It is instantiated \
    within an instance of :class:`ElectoralRoll <.ElectoralRoll>`.
    '''

    @property
    def storage(self):
        '''
        :return: dictionary with all data.

        Property where all the memorized data are stored.
        '''
        return self._storage

    @property
    def errors(self):
        '''
        :return: list with errors.

        Property where the errors found are stored.
        '''
        return self._errors

    @property
    def is_active(self):
        '''
        :return: boolean.

        Property that indicates if the memorizer is active as defined \
        in the constructor.
        '''
        return self._is_active

    def memorize(self, parsed):
        '''
        :param obj parsed: an instance of :class:`RollParser <.RollParser>`.

        :meth:`memorize <.RollMemorizer.memorize>` is the main method of \
        :class:`RollMemorizer <.RollMemorizer>`. It will memorize the \
        metadata of an analyzed sheet, if the memorizer is active (see \
        :attr:`is_active <.RollMemorizer.is_active>` property) it will \
        also memorize the analyzed entries. The methods executed to \
        memorize the metadata in order:

        * :meth:`prepare_rid \
            <.RollMemorizer.prepare_rid>`.
        * :meth:`store_metadata_places \
            <.RollMemorizer.store_metadata_places>`.
        * :meth:`store_metadata_entries \
            <.RollMemorizer.store_metadata_entries>`.
        * :meth:`store_metadata_nulls \
            <.RollMemorizer.store_metadata_nulls>`.
        * :meth:`store_metadata_nulls \
            <.RollMemorizer.store_metadata_nulls>`.

        It then stores, if active, the entries and errors.
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
        :param obj parsed: an instance of :class:`RollParser <.RollParser>`.

        :meth:`prepare_rid <.RollMemorizer.prepare_rid>` is a method that \
        prepares the :attr:`storage <.RollMemorizer.storage>` property for \
        storing metadata and electoral roll data. Use the electoral *roll \
        identifier* (see more in :attr:`rid <.ElectoralRoll.rid>`) as the \
        key for the :attr:`storage <.RollMemorizer.storage>` property.
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
        :param obj parsed: an instance of :class:`RollParser <.RollParser>`.

        :meth:`store_metadata_places <.RollMemorizer.store_metadata_places>` \
        is a method to memorize the places (regions, provinces and communes) \
        present in the parsed sheet.
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
        :param obj parsed: an instance of :class:`RollParser <.RollParser>`.

        :meth:`store_metadata_entries <.RollMemorizer.store_metadata_entries>`\
         is a method to memorize the metadata of the entries (*total*, \
         *rescued*, *errors*) present in the parsed sheet. If the total \
         number of entries is declared in the header, it is added as \
         *declared*.
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
        :param obj parsed: an instance of :class:`RollParser <.RollParser>`.

        :meth:`store_metadata_nulls <.RollMemorizer.store_metadata_nulls>` \
        is a method to memorize the metadata of the null data in the entries \
        (total and for each field with null data) present in the parsed sheet.
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
