SQLAlchemy dialect for SAP HANA
===============================

This dialect allows you to use the SAP HANA database with SQLAlchemy and `pyhdb <https://github.com/SAP/PyHDB>`_ driver.

The dialect is currently experimental and doesn't support all possible features in SQLAlchemy with SAP HANA.

The usage of the python database interface delivered by hdbclient, is currently not supported.

Prerequisites
-------------

At the moment the dialect only supports the pure Python database driver `pyhdb <https://github.com/SAP/PyHDB>`_. It's recommended to use pyhdb version 0.3.1 or above.

See the README of pyhdb about how you can install the driver.

Install
-------

Install from Python Package Index (coming soon):

.. code-block:: bash

    $ pip install sqlalchemy-hana

You can also install the latest version direct from a cloned git repository.

.. code-block:: bash

    $ git clone https://github.com/SAP/sqlalchemy-hana.git
    $ cd sqlalchemy-hana
    $ python setup.py install


Getting started
---------------

If you do not have access to a SAP HANA server, go to the `SAP HANA Developer Center <http://scn.sap.com/community/developer-center/hana>`_ and choose one of the options to `get your own trial SAP HANA Server <http://scn.sap.com/docs/DOC-31722>`_.

Now you can create a engine with the usage of the HANA dialect. This engine works like all other engines of SQLAlchemy.

.. code-block:: python

    from sqlalchemy import create_engine
    engine = create_engine('hana://username:password@example.de:30015')

Contribute
----------

If you found bugs or have other issues than you are welcome to create a GitHub Issue. If you have questions about usage or something similar please create a `Stack Overflow <http://stackoverflow.com/>`_ Question with tag `sqlalchemy <http://stackoverflow.com/questions/tagged/sqlalchemy>`_ and `hana <http://stackoverflow.com/questions/tagged/hana>`_.

