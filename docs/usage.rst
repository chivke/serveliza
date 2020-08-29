=====
Usage
=====

Serveliza can be used in different ways.

Command line usage
------------------

|Intro|

If you run from the command line you can access help on its use.

.. code-block:: console

    $ serveliza -h

    usage: serveliza [-h] [-v] {roll} ...

    Serveliza is an application to extract data of the Chilean Electoral Service
    (SERVEL) from different sources.

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit

    sub-commands:
      Serveliza has different utilities to extract data which are accessed
      through its subcommand. For more information check the help of each one.

      {roll}         description:
        roll         The roll command allows the extraction of electoral roll data
                     from pdf files to csv files.

    Made with ♥ by @chivke.

As well as each of the available subcommands.

.. code-block:: console

    $ serveliza roll -h
    usage: serveliza roll [-h] [-o output] [-p {pdftotext,pdfminersix}]
                          [-m {unified,separated}] [-s {commune,region}] [-r]
                          [--no-suffix] [--no-summary] [--silent] [--no-colors]
                          [source [source ...]]

    Serveliza is an application to extract data of the Chilean Electoral Service
    (SERVEL) from different sources. The roll command allows the extraction of
    electoral roll data from pdf files to csv files.

    positional arguments:
      source                Directory(ies) or file(s) to search for valid
                            electoral rolls.

    optional arguments:
      -h, --help            show this help message and exit
      -o output, --output output
                            Directory to store the data in .csv.
      -p {pdftotext,pdfminersix}, --processor {pdftotext,pdfminersix}
                            Processor (library) to extract text from pdf file.
      -m {unified,separated}, --mode {unified,separated}
                            'Determines the data export mode in files. If it is
                            "unified" (default) it creates a single csv file with
                            the data, or if it is "separated" into several
                            according to communal or regional criteria.'
      -s {commune,region}, --separator {commune,region}
                            Criteria for separating files in export in separate
                            mode.
      -r, --recursive       Property that determines if the search for pdf files
                            in the delivered source is recursive or is only for
                            the root of the indicated directory,
      --no-suffix           Determines whether exported files have a random text
                            string appended to the end.
      --no-summary          Determines whether to generate a summary file of the
                            export and the extracted data.
      --silent              Does not print application progress on screen.
      --no-colors           Does not colorize screen prints.

    Made with ♥ by @chivke.


Programmatic usage
------------------

You can use the serveliza components by importing from their sub-packages as :py:mod:`serveliza.roll`, :py:mod:`serveliza.utils` or :py:mod:`serveliza.mixins`.

For example, you can import the main class that works with electoral rolls.

.. code-block:: python

    from serveliza.roll import ElectoralRoll

It can also be imported in abbreviated form defined in the ``__init__.py`` file.

.. code-block:: python

    from serveliza.roll import ER

Inside serveliza, the module of the same name defines functions as shortcuts for specific actions, instantiating the classes in a transparent way. The command line interface is powered by these functions. 

For example, you can get a pandas dataframe object through a function:

.. code-block:: python

    from serveliza import serveliza
    data = serveliza.roll_from_pdf_to_dataframe('.')

That otherwise it would be like this:

.. code-block:: python

    from serveliza.roll import ElectoralRoll
    roll = ElectoralRoll('.')
    roll.run()
    data = roll.roll_from_pdf_to_dataframe('.')


.. |Intro| image:: https://github.com/chivke/serveliza/raw/master/images/serveliza_intro.gif
    :align: middle
    :alt: intro to cli
    :width: 80%