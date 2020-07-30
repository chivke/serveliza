from datetime import datetime, timedelta


def storage_rid(obj, parsed):
    rid = parsed.metadata['rid']
    if rid in obj._storage:
        return rid
    metadata = {
        'register': parsed.header['register'],
        'election': parsed.header['election'],
        'year':     parsed.header['year'],
        'regions':      [],
        'communes':     [],
        'provinces':    [],
        'times': {
            'total':    timedelta(),
            'header':   timedelta(),
            'fields':   timedelta(),
            'entries':  timedelta()},
        'nulls': {
            'total': 0},
        'entries': {'total': 0, 'rescue': 0, 'errors': 0},
        'entries-total': 0,
        'entries-rescue': 0}
    obj._storage[rid] = {
        'entries':  [],
        'fields':   parsed.fields,
        'metadata': metadata}
    return rid


def metadata_times(obj, parsed, rid):
    last_metadata = obj.storage[rid]['metadata']
    last_total = last_metadata['times']['total']
    total = last_total + parsed.metadata['times']['total']
    last_header = last_metadata['times']['header']
    header = last_header + parsed.metadata['times']['header']
    last_fields = last_metadata['times']['fields']
    fields = last_fields + parsed.metadata['times']['fields']
    last_entries = last_metadata['times']['entries']
    entries = last_entries + parsed.metadata['times']['entries']
    times = {
        'total': total, 'header': header,
        'fields': fields, 'entries': entries}
    obj._storage[rid]['metadata']['times'].update(times)


def metadata_place(obj, parsed, rid):
    region = parsed.header['region']
    regions = obj.storage[rid]['metadata']['regions']
    province = parsed.header['province']
    provinces = obj.storage[rid]['metadata']['provinces']
    commune = parsed.header['commune']
    communes = obj.storage[rid]['metadata']['communes']
    if region not in regions:
        obj._storage[rid]['metadata']['regions']\
            .append(region)
    if province not in provinces:
        obj._storage[rid]['metadata']['provinces']\
            .append(province)
    if commune not in communes:
        obj._storage[rid]['metadata']['communes']\
            .append(commune)


def metadata_entries(obj, parsed, rid):
    entries = obj.storage[rid]['metadata']['entries']
    pentries = parsed.metadata['entries']
    #last_total = entries['total']
    total = entries['total'] + len(parsed.entries)
    #last_rescue = entries['rescue']
    rescue = entries['rescue'] + pentries.get('rescue', 0)
    #last_errors = entries['errors']
    errors = entries['errors'] + len(parsed.errors)
    entries = {'total': total, 'rescue': rescue, 'errors': errors}
    obj._storage[rid]['metadata']['entries'] = entries


def metadata_nulls(obj, parsed, rid):
    pnulls = parsed.metadata['nulls']
    if not pnulls['total']:
        return None
    nulls = obj.storage[rid]['metadata']['nulls']
    total = nulls['total'] + pnulls['total']
    fields = parsed.metadata['fields']
    result = {'total': total}
    for field in fields:
        if field not in pnulls:
            continue
        result[field] = pnulls[field]
        if field in nulls:
            result[field] += nulls[field]
    obj._storage[rid]['metadata']['nulls'].update(result)
