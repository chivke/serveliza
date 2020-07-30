import os
from ..utils import colors


def runned_tag(register):
    if register.runned:
        return colors.OK('[runned]')
    return colors.WARN('[not runned]')


def files_tag(register):
    files = len(register.metadata['files'])
    plural = 's' if files > 1 else ''
    return f'{str(files)} file{plural}'


def total_tag(register):
    if register.runned:
        return colors.OK(len(register.entries))
    return ''


def repr_electoral(register):
    return '<' + colors.INFO(register.__class__.__name__) \
        + ' instance ' + runned_tag(register) + f'[{total_tag(register)}]' \
        + colors.LEAD(f'[{files_tag(register)}]') \
        + '>'


def resume_electoral(register):
    ''''''
    resume = f'{register.__class__.__name__} instance'
    if register.runned:
        resume += colors.OK(' [runned]')
        resume += colors.LEAD(f' {str(len(register.metadata["files"]))} file')
        if len(register.metadata['files']) > 1:
            resume += 's'
    else:
        resume += colors.WARN(' [not runned]')
    resume += colors.LEAD('\n'+('-'*len(resume)))
    storages = len(register.storage)
    if storages > 1:
        resume += colors.WARN(
            f'\n[warn]: {str(storages)}'
            + ' different electoral register loaded. Dont do it,'
            + ' there may be repetitions of people.')
    screen_width = os.get_terminal_size().columns
    for key, bucket in register.storage.items():
        column_width = screen_width // len(bucket['fields'])
        total_entries = bucket["metadata"]["entries"]["total"]
        resume += '\n['+colors.OK(key)\
            + f']: data of {colors.INFO(total_entries)} people'
        errors = (100 / total_entries)*len(register.errors)
        resume += colors.LEAD(f' [{errors:.5} % of errors]')
        divider = colors.LEAD('|')
        divider_width = colors.LEAD('\n'+('-'*screen_width))
        cutter = lambda x: '.' if len(x) - (column_width - 4) > 0 else (' ')
        column_aux = colors.LEAD(divider+' {:<'+str(column_width - 3)+'} ')
        fields = '\n' + str(column_aux*len(bucket['fields'])).format(
            *[colors.INFO(x[:column_width - 4])
                + cutter(x) for x in bucket['fields']]) + divider
        resume += divider_width + fields + divider_width
        resume += '\n' + str(column_aux*len(bucket['fields'])).format(
            *[x[:column_width - 4]+cutter(x) for x in bucket['entries'][0]]) \
            + divider
        resume += divider_width
        total_msg = colors.OK(f'[ {str(total_entries - 2)} entries ]')
        separator = (screen_width - len(total_msg)) // 2
        resume += '\n'+colors.LEAD('-'*separator)+total_msg \
            + colors.LEAD('-'*separator)
        resume += divider_width
        resume += '\n' + str(column_aux*len(bucket['fields'])).format(
            *[x[:column_width - 4]+cutter(x) for x in bucket['entries'][-1]])\
            + divider
        resume += divider_width
    return resume
