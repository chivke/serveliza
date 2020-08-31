=========
Serveliza
=========

.. image:: https://img.shields.io/pypi/v/serveliza.svg
        :target: https://pypi.python.org/pypi/serveliza

.. image:: https://img.shields.io/travis/chivke/serveliza.svg
        :target: https://travis-ci.com/chivke/serveliza

.. image:: https://readthedocs.org/projects/serveliza/badge/?version=latest
        :target: https://serveliza.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/github/license/chivke/serveliza
        :target: https://www.gnu.org/licenses/gpl-3.0
        :alt: license badge

.. image:: https://img.shields.io/pypi/pyversions/serveliza
        :alt: Python versions

.. image:: https://pyup.io/repos/github/chivke/serveliza/shield.svg
        :target: https://pyup.io/repos/github/chivke/serveliza/
        :alt: Updates

.. image:: https://pyup.io/repos/github/chivke/serveliza/python-3-shield.svg
        :target: https://pyup.io/repos/github/chivke/serveliza/
        :alt: Python 3


|Intro|


Serveliza is an application to extract data of the Chilean Electoral Service (SERVEL) from different open sources.

A first step to democratize data is to make it accessible for free use.


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

Documentation
--------------

Full documentation in `readthedocs <https://serveliza.readthedocs.io>`_.

License
--------

GNU General Public License v3


.. |Intro| image:: https://github.com/chivke/serveliza/raw/master/images/serveliza_intro.gif
    :align: middle
    :alt: intro to cli
    :width: 80%

.. |Roll| image:: https://github.com/chivke/serveliza/raw/master/images/serveliza_roll.gif
    :align: middle
    :alt: Electoral roll example gif
    :width: 80%
