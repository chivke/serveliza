"""Main module."""
from serveliza.roll import ElectoralRoll


def roll_from_pdf_to_csv(
        source, output='output',
        processor=None, mode=None, mode_sep=None,
        no_suffix=False, recursive=False, no_summary=False,
        silent=False, no_colors=False,):
    roll = ElectoralRoll(
        source=source, output=output,
        mode=mode, mode_sep=mode_sep,
        random_suffix=False if no_suffix else True,
        summary=False if no_summary else True,
        memorize=False, processor=processor,
        recursive=recursive,
        verbose=False if silent else True,
        colors=False if no_colors else True,
        export=True)
    roll.run()
    return roll.metadata['exported_to']


def roll_from_pdf_to_dataframe(
        source, recursive=False,
        verbose=False, processor=None):
    roll = ElectoralRoll(
        source=source, recursive=recursive,
        verbose=verbose, processor=None)
    roll.run()
    return roll.to_dataframe()
