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


|Intro|


Serveliza is an application to extract data of the Chilean Electoral Service (SERVEL) from different open sources.

A first step to democratize data is to make it accessible for free use.

|Intro|

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

.. |Roll| image:: https://github.com/chivke/serveliza/raw/master/images/readme-roll.gif
    :align: middle
    :alt: Electoral roll example gif

.. |Intro| image:: https://github.com/chivke/serveliza/raw/master/images/serveliza_intro.gif
    :align: middle
    :alt: intro to cli
    :width: 80%