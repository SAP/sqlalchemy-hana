SQLAlchemy dialect for SAP HANA
===============================

.. image:: https://api.reuse.software/badge/github.com/SAP/sqlalchemy-hana
   :target: https://api.reuse.software/info/github.com/SAP/sqlalchemy-hana

This dialect allows you to use the SAP HANA database with SQLAlchemy.
It can use the supported SAP HANA Python Driver `hdbcli` (supported since SAP HANA SPS 2) or the
open-source pure Python client `PyHDB`. Please notice that sqlalchemy-hana isn't an official SAP
product and isn't covered by SAP support.

Prerequisites
-------------

Python 2.7 or Python 3.X with installed SAP HANA DBAPI implementation.

SAP HANA Python Driver see `SAP HANA Client Interface Programming Reference <https://help.sap.com/viewer/0eec0d68141541d1b07893a39944924e/2.0.02/en-US/39eca89d94ca464ca52385ad50fc7dea.html>`_ or the install section of `PyHDB <https://github.com/SAP/PyHDB>`_.

Install
-------

Install from Python Package Index:

.. code-block:: bash

    $ pip install sqlalchemy-hana

You can also install the latest version direct from a cloned git repository.

.. code-block:: bash

    $ git clone https://github.com/SAP/sqlalchemy-hana.git
    $ cd sqlalchemy-hana
    $ python setup.py install


Getting started
---------------

If you do not have access to a SAP HANA server, you can also use the `SAP HANA Express edition <https://www.sap.com/cmp/td/sap-hana-express-edition.html>`_.

After installation of sqlalchemy-hana, you can create a engine which connects to a SAP HANA
instance. This engine works like all other engines of SQLAlchemy.

.. code-block:: python

    from sqlalchemy import create_engine
    engine = create_engine('hana://username:password@example.de:30015')

Alternatively, you can use HDB User Store to avoid entering connection-related information manually each time you want to establish a connection to an SAP HANA database:

.. code-block:: python

    from sqlalchemy import create_engine
    engine = create_engine('hana://userkey=my_user_store_key')

You can create your user key in the user store using the following command:

.. code-block:: 

	hdbuserstore SET <KEY> <host:port> <USERNAME> <PASSWORD>

By default the ``hana://`` schema will use hdbcli (from the SAP HANA Client) as underlying database driver.
To use PyHDB as driver use ``hana+pyhdb://`` as schema in your DBURI.

In case of a tenant database, you may use:

.. code-block:: python

    from sqlalchemy import create_engine
    engine = engine = create_engine('hana://user:pass@host/tenant_db_name')

Contribute
----------

If you found bugs or have other issues, you are welcome to create a GitHub Issue. If you have questions about usage or something similar please create a `Stack Overflow <http://stackoverflow.com/>`_ Question with tag `sqlalchemy <http://stackoverflow.com/questions/tagged/sqlalchemy>`_ and `hana <http://stackoverflow.com/questions/tagged/hana>`_.

License
-------

Copyright (c) 2015-2021 SAP SE or an SAP affiliate company and sqlalchemy-hana contributors.  Please see our `LICENSE file <https://github.com/SAP/sqlalchemy-hana/blob/master/LICENSE>`__ for copyright and license information. Detailed information including third-party components and their licensing/copyright information is available `via the REUSE tool <https://api.reuse.software/info/github.com/SAP/sqlalchemy-hana>`__.
