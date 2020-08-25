
def this_bytes(bts, short=False):
    if not isinstance(bts, int):
        return None
    measures = [
        (1000000000, 'gigabytes', 'gb'),
        (1000000, 'megabytes', 'mb'),
        (1000, 'kilobytes', 'kb'),
        (1, 'bytes', 'b')
    ]
    for measure in sorted(measures, reverse=True, key=lambda x: x[0]):
        if bts > measure[0]:
            msr = measure[1] if not short else measure[2]
            return str(bts // measure[0]) + ' ' + msr
