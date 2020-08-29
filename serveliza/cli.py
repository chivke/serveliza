"""Console script for serveliza."""
import argparse
import sys
from . import __version__, __author__
from serveliza.roll.exporter import RollExporter
from serveliza.roll import ElectoralRoll
from serveliza import serveliza

DESC = 'Serveliza is an application to extract data of ' \
       'the Chilean Electoral Service (SERVEL) from different ' \
       'sources.'

DESC_SUBCMDS = 'Serveliza has different utilities to extract data ' \
               'which are accessed through its subcommand. For more ' \
               'information check the help of each one.'

DESC_ROLL = 'The roll command allows the extraction of ' \
            'electoral roll data from pdf files to csv files.'

EPILOG = f'Made with ♥ by @{__author__}.'


def roll_cli_wrapper(args, parser):
    source = args.source
    if not source:
        parser.print_help()
        return 0
    kwargs = {
        'source': source,
        'output': args.output,
        'processor': args.processor,
        'mode': args.mode,
        'mode_sep': args.separator,
        'no_suffix': args.no_suffix,
        'recursive': args.recursive,
        'no_summary': args.no_summary,
        'silent': args.silent,
        'no_colors': args.no_colors}
    try:
        serveliza.roll_from_pdf_to_csv(**kwargs)
    except TypeError as error:
        print(f'Error! > {error}')


def roll_parser(subparser):
    parser_roll = subparser.add_parser(
        'roll', help=DESC_ROLL, description=DESC+' '+DESC_ROLL,
        epilog=EPILOG)
    parser_roll.set_defaults(func=roll_cli_wrapper)
    parser_roll.add_argument(
        'source', nargs='*', type=str,
        help=ElectoralRoll.source.__doc__)
    parser_roll.add_argument(
        '-o', '--output', help=RollExporter.output.__doc__,
        nargs=1, type=str, metavar='output', default='output')
    parser_roll.add_argument(
        '-p', '--processor', help=ElectoralRoll.processor.__doc__,
        nargs=1, type=str, default='pdftotext',
        choices=[x[0] for x in ElectoralRoll.processor_ref.items()])
    parser_roll.add_argument(
        '-m', '--mode', help=RollExporter.mode.__doc__,
        nargs=1, type=str, default='unified', choices=RollExporter._modes)
    parser_roll.add_argument(
        '-s', '--separator', help=RollExporter.mode_sep.__doc__,
        nargs=1, type=str, choices=RollExporter._mode_sep_opts)
    parser_roll.add_argument(
        '-r', '--recursive', help=ElectoralRoll.recursive.__doc__,
        action='store_true', default=False)
    parser_roll.add_argument(
        '--no-suffix', help=RollExporter.random_suffix.__doc__,
        action='store_true', default=False)
    parser_roll.add_argument(
        '--no-summary', help=RollExporter.summary.__doc__,
        action='store_true', default=False)
    parser_roll.add_argument(
        '--silent', help='Does not print application progress on screen.',
        action='store_true', default=False)
    parser_roll.add_argument(
        '--no-colors', help='Does not colorize screen prints.',
        action='store_true', default=False)
    return parser_roll


def main():
    '''Console script for serveliza.'''
    parser = argparse.ArgumentParser(
        prog='serveliza', description=DESC, epilog=EPILOG)
    # version
    parser.add_argument(
        '-v', '--version', action='version',
        version="%(prog)s "+__version__)
    subparser = parser.add_subparsers(
        title='sub-commands', description=DESC_SUBCMDS, help='description:')
    # roll subcommand parser:
    parser_roll = roll_parser(subparser)
    # insert other subcommands here:
    # parser_cmd = cmd_parser(subparser)
    # ...
    args = parser.parse_args()
    if hasattr(args, 'func') and args.func == roll_cli_wrapper:
        args.func(args, parser_roll)
    else:
        parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
