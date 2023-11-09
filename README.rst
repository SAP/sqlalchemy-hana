SQLAlchemy dialect for SAP HANA
===============================

.. image:: https://api.reuse.software/badge/github.com/SAP/sqlalchemy-hana
    :target: https://api.reuse.software/info/github.com/SAP/sqlalchemy-hana

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://github.com/SAP/sqlalchemy-hana/actions/workflows/nightly.yml/badge.svg?branch=main&event=schedule
    :target: https://github.com/SAP/sqlalchemy-hana/actions/workflows/nightly.yml

This dialect allows you to use the SAP HANA database with SQLAlchemy.
It uses ``hdbcli`` to connect to SAP HANA.
Please notice that sqlalchemy-hana isn't an official SAP product and isn't covered by SAP support.

Prerequisites
-------------
* Python 3.8+
* SQLAlchemy 1.4 or 2.x
* `hdbcli <https://help.sap.com/viewer/f1b440ded6144a54ada97ff95dac7adf/latest/en-US/f3b8fabf34324302b123297cdbe710f0.html>`_

Install
-------
Install from the Python Package Index:

.. code-block:: bash

    $ pip install sqlalchemy-hana

Getting started
---------------
If you do not have access to a SAP HANA server, you can also use the
`SAP HANA Express edition <https://www.sap.com/cmp/td/sap-hana-express-edition.html>`_.

After installation of sqlalchemy-hana, you can create a engine which connects to a SAP HANA
instance. This engine works like all other engines of SQLAlchemy.

.. code-block:: python

    from sqlalchemy import create_engine
    engine = create_engine('hana://username:password@example.de:30015')

Alternatively, you can use HDB User Store to avoid entering connection-related information manually
each time you want to establish a connection to an SAP HANA database:

.. code-block:: python

    from sqlalchemy import create_engine
    engine = create_engine('hana://userkey=my_user_store_key')

You can create your user key in the user store using the following command:

.. code-block::

	hdbuserstore SET <KEY> <host:port> <USERNAME> <PASSWORD>

In case of a tenant database, you may use:

.. code-block:: python

    from sqlalchemy import create_engine
    engine = engine = create_engine('hana://user:pass@host/tenant_db_name')

Usage
-----

Special CREATE TABLE argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sqlalchemy-hana provides a special argument called “hana_table_type” which can be used to
specify the type of table one wants to create with SAP HANA (i.e. ROW/COLUMN).
The default table type depends on your SAP HANA configuration and version.

.. code-block:: python

    t = Table('my_table', metadata, Column('id', Integer), hana_table_type = 'COLUMN')

Case Sensitivity
~~~~~~~~~~~~~~~~
In SAP HANA, all case insensitive identifiers are represented using uppercase text.
In SQLAlchemy on the other hand all lower case identifier names are considered to be case insensitive.
The sqlalchemy-hana dialect converts all case insensitive and case sensitive identifiers to the
right casing during schema level communication.
In the sqlalchemy-hana dialect, using an uppercase name on the SQLAlchemy side indicates a case
sensitive identifier, and SQLAlchemy will quote the name,which may cause case mismatches between
data received from SAP HANA.
Unless identifier names have been truly created as case sensitive (i.e. using quoted names),
all lowercase names should be used on the SQLAlchemy side.

Auto Increment Behavior
~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy Table objects which include integer primary keys are usually assumed to have
“auto incrementing” behavior, which means that primary key values can be automatically generated
upon INSERT.
Since SAP HANA has no auto-increment feature, SQLAlchemy relies upon sequences to automatically
generate primary key values.
These sequences must be explicitly specified to enable auto-incrementing behavior.

To create sequences, use the ``sqlalchemy.schema.Sequence`` object which is passed to a
``Column`` construct.

.. code-block:: python

    t = Table('my_table', metadata, Column('id', Integer, Sequence('id_seq'), primary key=True))

LIMIT/OFFSET Support
~~~~~~~~~~~~~~~~~~~~
SAP HANA supports both ``LIMIT`` and ``OFFSET``, but it only supports ``OFFSET`` in conjunction with
``LIMIT`` i.e. in the select statement the offset parameter cannot be set without the ``LIMIT``
clause, hence in sqlalchemy-hana if the user tries to use offset without limit, a limit of
``2147384648`` would be set, this has been done so that the users can smoothly use ``LIMIT`` or
``OFFSET`` as in other databases that do not have this limitation.
``2147384648`` was chosen, because it is the maximum number of records per result set.

RETURNING Support
~~~~~~~~~~~~~~~~~
Sqlalchemy-hana does not support ``RETURNING`` in the ``INSERT``, ``UPDATE`` and ``DELETE``
statements to retrieve result sets of matched rows from ``INSERT``, ``UPDATE`` and ``DELETE``
statements because newly generated primary key values are neither fetched nor returned automatically
in SAP HANA and SAP HANA does not support the syntax ``INSERT... RETURNING...``.

Reflection
~~~~~~~~~~
The sqlalchemy-hana dialect supports all reflection capabilities of SQLAlchemy.
The Inspector used for the SAP HANA database is an instance of ``HANAInspector`` and offers an
additional method which returns the OID (object id) for the given table name.

.. code-block:: python

    from sqlalchemy import create_engine, inspect

    engine = create_engine("hana://username:password@example.de:30015")
    insp = inspect(engine)  # will be a HANAInspector
    print(insp.get_table_oid('my_table'))

Foreign Key Constraints
~~~~~~~~~~~~~~~~~~~~~~~
In SAP HANA the following ``UPDATE`` and ``DELETE`` foreign key referential actions are available:

* RESTRICT
* CASCADE
* SET NULL
* SET DEFAULT

The foreign key referential option ``NO ACTION`` does not exist in SAP HANA.
The default is ``RESTRICT``.

UNIQUE Constraints
~~~~~~~~~~~~~~~~~~
For each unique constraint an index is created in SAP HANA, this may lead to unexpected behavior
in programs using reflection.

Data types
~~~~~~~~~~
As with all SQLAlchemy dialects, all UPPERCASE types that are known to be valid with SAP HANA are
importable from the top level dialect, whether they originate from sqlalchemy types or from the
local dialect.

DateTime Compatibility
""""""""""""""""""""""
SAP HANA has no data type known as ``DATETIME``, it instead has the datatype ``TIMESTAMP``, which can
actually store the date and time value.
For this reason, the sqlalchemy-hana dialect provides a ``TIMESTAMP`` type which is a ```datetime``.

NUMERIC Compatibility
"""""""""""""""""""""
SAP HANA does not have a data type known as ``NUMERIC``, hence if a user has a column with data type
numeric while using sqlalchemy-hana, it is stored as ``DECIMAL`` data type instead.

TEXT datatype
"""""""""""""
SAP HANA only supports the datatype ``TEXT`` for column tables.
It is not a valid data type for row tables. Hence, one must mention ``hana_table_type="COLUMN"``

Regex
~~~~~
sqlalchemy-hana supports the ``regexp_match`` and ``regexp_replace``
functions provided by SQLAlchemy.

Bound Parameter Styles
~~~~~~~~~~~~~~~~~~~~~~
The default parameter style for the sqlalchemy-hana dialect is ``qmark``, where SQL is rendered
using the following style:

.. code-block:: sql

    WHERE my_column = ?

Boolean
~~~~~~~
By default, sqlalchemy-hana uses native boolean types.
However, older versions of sqlalchemy-hana used integer columns to represent these values leading
to a compatibility gap.
To *disable* native boolean support, add ``use_native_boolean=False`` to ``create_engine``.

Users are encouraged to switch to native booleans.
This can be e.g. done by using ``alembic``:

.. code-block:: python

    from sqlalchemy import false

    # assuming a table TAB with a tinyint column named valid
    def upgrade() -> None:
        op.add_column(Column("TAB", Column('valid_tmp', Boolean, server_default=false())))
        op.get_bind().execute("UPDATE TAB SET valid_tmp = TRUE WHERE valid = 1")
        op.drop_column("TAB", "valid")
        op.get_bind().execute("RENAME COLUMN TAB.valid_tmp to valid")
        # optionally, remove also the server default by using alter column

Alembic
-------
The sqlalchemy-hana dialect also contains a dialect for ``alembic``.
This dialect is active as soon as ``alembic`` is installed.
To ensure version compatibility, install sqlalchemy-hana as followed:

.. code-block:: bash

    $ pip install sqlalchemy-hana[alembic]

Cookbook
--------

IDENTITY Feature
~~~~~~~~~~~~~~~~
SAP HANA also comes with an option to have an ``IDENTITY`` column which can also be used to create
new primary key values for integer-based primary key columns.
Built-in support for rendering of ``IDENTITY`` is not available yet, however the following compilation
hook may be used to make use of
the IDENTITY feature.

.. code-block:: python

    from sqlalchemy.schema import CreateColumn
    from sqlalchemy.ext.compiler import compiles

    @compiles(CreateColumn, 'hana')
    def use_identity(element, compiler, **kw):
        text = compiler.visit_create_column(element, **kw)
        text = text.replace('NOT NULL', 'NOT NULL GENERATED BY DEFAULT AS IDENTITY')
        return text

    t = Table('t', meta, Column('id', Integer, primary_key=True), Column('data', String))

    t.create(engine)

Development Setup
-----------------
We recommend the usage of ``pyenv`` to install a proper 3.11 python version for development.

* ``pyenv install 3.11``
* ``python311 -m venv venv``
* ``source venv/bin/activate``
* ``pip install -U pip``
* ``pip install -e .[dev,test,alembic]``

To execute the tests, use ``pyenv``.
The linters and formatters can be executed using ``pre-commit``: ``pre-commit run -a``.

Testing
-------
**Pre-Submit**: Linters, formatters and reduced test matrix
**Post-Submit**: Linters and formatters
**Nightly**: Full test matrix

Release Actions
---------------
* Verify that the latest nighty run is after the latest commit; else trigger a run
* Update the version in the pyproject.toml
* Add an entry in the changelog
* Push a new tag like vX.X.X to trigger the release

Contribute
----------
If you found bugs or have other issues, you are welcome to create a GitHub Issue
