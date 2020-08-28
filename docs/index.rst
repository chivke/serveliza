Serveliza's documentation
=========================

.. image:: https://img.shields.io/pypi/v/serveliza.svg
        :target: https://pypi.python.org/pypi/serveliza

.. image:: https://img.shields.io/travis/chivke/serveliza.svg
        :target: https://travis-ci.com/chivke/serveliza

.. image:: https://readthedocs.org/projects/serveliza/badge/?version=latest
        :target: https://serveliza.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Serveliza is an application to extract data of the Chilean Electoral Service (SERVEL) from different open sources.

A first step to democratize data is to make it accessible for free use.

+---------------+---------------+-------------+
|:ref:`genindex`|:ref:`modindex`|:ref:`search`|
+---------------+---------------+-------------+

Quick start
------------

.. code-block:: console

    $ pip install serveliza
    $ serveliza -h

Features
--------

* It analyzes, extracts and exports data from the **electoral roll**, having as a source the public pdf files distributed by SERVEL.

  |Roll|

  *Added in the first release (0.1.0.)*

Contents
---------

.. toctree::
   :maxdepth: 2

   installation
   usage
   reference
   contributing
   authors
   history

.. |Roll| image:: https://github.com/chivke/serveliza/raw/master/images/readme-roll.gif
    :align: middle
    :alt: Electoral roll example gif

