API Reference
=============

This section exposes the documentation of the classes and functions that support serveliza. Your query will allow an understanding of  your logic for `programmatic use`_.

Electoral Roll
--------------

  |Roll|

* Main module: :mod:`serveliza.roll.roll`
* Auxiliary modules:
    * :mod:`serveliza.roll.adapters`
    * :mod:`serveliza.roll.parsers`
    * :mod:`serveliza.roll.memorizer`
    * :mod:`serveliza.roll.exporter`
    * :mod:`serveliza.roll.printer`

.. automodule:: serveliza.roll
    :members:

Main class
~~~~~~~~~~

.. automodule:: serveliza.roll.roll
    :members:
    :member-order: bysource

Roll adapters
~~~~~~~~~~~~~

.. automodule:: serveliza.roll.adapters
    :members:
    :member-order: bysource

Roll parsers
~~~~~~~~~~~~

.. automodule:: serveliza.roll.parsers
    :members:
    :member-order: bysource

Roll memorizer
~~~~~~~~~~~~~~

.. automodule:: serveliza.roll.memorizer
    :members:
    :member-order: bysource

Roll exporter
~~~~~~~~~~~~~

.. automodule:: serveliza.roll.exporter
    :members:
    :member-order: bysource

Roll printer
~~~~~~~~~~~~

.. automodule:: serveliza.roll.printer
    :members:
    :member-order: bysource


Mixins
------

* PDF processor mixin: :mod:`serveliza.mixins.pdf`
* Available PDF processors: :mod:`serveliza.mixins.pdf_processors`

.. automodule:: serveliza.mixins
    :members:

PDF processor mixin
~~~~~~~~~~~~~~~~~~~

.. automodule:: serveliza.mixins.pdf
    :members:
    :member-order: bysource

Available PDF processors
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: serveliza.mixins.pdf_processors
    :members:
    :member-order: bysource


.. |Roll| image:: https://github.com/chivke/serveliza/raw/master/images/serveliza_roll.gif
    :alt: Electoral roll example gif
    :width: 60%

.. _programmatic use: ./usage.html#programmatic-usage