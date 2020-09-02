.. highlight:: shell

============
Installation
============

System requirements
-------------------

Serveliza needs the installation of system requirements due to the use of the `pdftotext`_ package as a text processor from pdf files.

.. code-block:: console

    $ sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev

Stable release
--------------

To install serveliza, run this command:

.. code-block:: console

    $ pip install serveliza

This is the preferred method to install serveliza, as it will always install the most recent stable release.

From sources
------------

The sources for serveliza can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/chivke/serveliza

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

.. _Github repo: https://github.com/chivke/serveliza
.. _pdftotext: https://github.com/jalan/pdftotext`