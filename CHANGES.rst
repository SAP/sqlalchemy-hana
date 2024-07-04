Changelog
=========

2.3.0
-----

Features
~~~~~~~~

- ``sqlalchemy_hana.errors`` will now raise a ``WriteInReadOnlyReplicationError`` error for error
  messages indicating a write statement in a read-only replication

2.2.0
-----

Features
~~~~~~~~

- Added basic JSON support (contributed by @Zahlii)
- ``sqlalchemy_hana.errors`` will now raise a ``DatabaseConnectNotPossibleError`` error for hdbcli
  error code ``1888``

2.1.0
-----

Features
~~~~~~~~
- Add error handling for SAP HANA Cloud region maintenance error
- Add additional caching to reflection methods (contributed by @Masterchen09)

Bugfixes
~~~~~~~~
- Fixed an issue causing ``get_table_oid`` to fails of the inspector
  was created based on an engine (contributed by @Masterchen09)

2.0.0
-----

Breaking Changes
~~~~~~~~~~~~~~~~
Reworked the ``sqlalchemy_hana.errors`` package so that it can be used inside a SQLAlchemy
``handle_error`` event hook. Therefore

- ``wrap_dbapi_error`` was removed
- ``wrap_hdbcli_error`` was removed
- ``HANAError`` now extends ``sqlalchemy.exc.DBAPIError``


1.4.0
-----

Features
~~~~~~~~
- Support ``Identity`` columns
- Support additional cases for ``StatementExecutionError``

1.3.0
-----

Features
~~~~~~~~
- Support ``InvalidObjectNameError`` in ``sqlalchemy_hana.errors``
- Add ``convert_dbapi_error`` to ``sqlalchemy_hana.errors``

Bugfixes
~~~~~~~~
- Fixed an issue causing the usage of ALPHANUM to result in an AttributeError

1.2.0
-----

Features
~~~~~~~~
- Support CREATE and DROP of views
- Add limited UPSERT support
- Add support for exception wrapping by replacing hdbcli errors with more detailed ones if possible

1.1.1
-----

Bugfixes
~~~~~~~~
- Fixed an issue causing the alembic dialect to render a ``RENAME`` table statement wrongly

1.1.0
-----

Features
~~~~~~~~
- The statement caching capabilities of SQLAlchemy are now supported
- Calculated/Computed columns are now officially supported
- The following SAP HANA types are now supported: ``SECONDDATE``, ``LONGDATE`` and ``ALPHANUM``
- The module ``sqlalchemy_hana.types`` defines now all SAP HANA native types
- All *camelcase* types of SQLAlchemy are now supported. If SAP HANA does not support it, a
  similar type is used automatically
- sqlalchemy-hana will now expose the version information of the connected SAP HANA instance,
  filling the dialect field ``server_version_info``

Bugfixes
~~~~~~~~
- During column reflection all types will expose their respective length, scale and precision

1.0.1
-----

Bugfixes
~~~~~~~~
- Version 1.0.0 states that ``is_distinct_from`` is supported, but the dialect specified
  ``supports_is_distinct_from=False``. The value was changed to ``True``
- Fixed an issue causing ``is_not_distinct_from`` to fail with an SQL syntax error
- Make sure that ``Text`` types are really rendered as ``UnicodeText``
- Removed misleading ``get_dbapi_type`` from ``Boolean``

1.0.0
-----

Breaking Changes
~~~~~~~~~~~~~~~~
- By default native booleans are used. If integer based columns should be used, specify
  ``use_native_boolean=False`` in ``create_engine``
- Columns of SQLAlchemy type String are now created with the SAP HANA SQL type NVARCHAR.
  The previously used SAP HANA SQL type VARCHAR has been only designed for 7-bit ASCII character data.
  Storing other non-ASCII characters in a different encoding like UTF-8 was sometimes possible but
  never intended or recommended
  It may cause unexpected behavior for certain database-side operations like sorting or failures
  with string functions
  With the introduction of SAP HANA Cloud, the SQL type VARCHAR is also only an alias for NVARCHAR.
- Columns of SQLAlchemy type Text are now created with the SAP HANA SQL type NCLOB instead of CLOB.
  Like the SAP HANA SQL type VARCHAR, CLOB was designed for 7-bit ASCII character data.
  This change also ensures consistency and compatibility with SAP HANA Cloud, where CLOB is just an
  alias for NCLOB
- Removed ``pyhdb`` support because  ``pyhdb`` is out of maintenance and the GitHub repository was
  archived.
  Please migrate to ``hdbcli`` as it also supports connections towards SAP HANA Cloud databases.
- Removed support for Python versions below version 3.8
- Removed support for SQLAlchemy below version 1.4
- Removed support for hdbcli below version 2.10
- Removed the hidden and outdated feature ``auto_convert_lobs``

Features
~~~~~~~~
- Official support for SQLAlchemy 1.4 and 2.0
- Official support for Python 3.11 and 3.12
- Support the SAP HANA datatype ``SMALLDECIMAL``
- Support native booleans (this is the new default)
- The ``sqlalchemy_hana`` package is fully typed and exports its types
- The Alembic dialect left the preview stage and is now included by default.
  Please install sqlalchemy-hana with the alembic requirement like ``pip install sqlchemy-hana[alembic]``.
  Supported is Alembic 1.12 onwards.
- Specified the SQLAlchemy statement caching support explicitly to false.
  Support might be added later (see #126)
- Support `regexp_match <https://docs.sqlalchemy.org/en/20/core/operators.html#string-matching>`_
  and `regexp_replace <https://docs.sqlalchemy.org/en/20/core/operators.html#string-alteration>`_
- Allow usage of ``is_distinct_from`` operator through a SAP HANA compatible expression
- Prefer dialect types in ``get_columns``
- Allow usage of additional options (e.g. ``nowait``) in ``with_for_update`` when using
  ``read=True``
- Added CI with linters and testing utilizing the SQLAlchemy and Alembic test suite

Bugfixes
~~~~~~~~
- Fixed a bug with SQLAlchemy's custom AUTOCOMIT isolation level. If the user changed the isolation
  level from AUTOCOMMIT to something else, the dialect didn't notified the underlying database
  connection and it stayed in autocommit mode while the user expected the typical transaction
  behavior and the defined isolation level.

0.5.0
-----
- Improved support for ''SELECT FOR UPDATE'' statements.

0.4.0
-----
- Support for inspection of table oid
- Support for table comments
- Support for setting and reflecting isolation level

0.3.0
-----
- **Backward incompatible change:** The ``hana://`` DBURI schema will now use ``hdbcli`` by default.
- Support of Python 3
- Support for check constraints
- Support for foreign key options and name
- Support for tenant specification in connect URL and automatic sql port discovery
- Support for autocommit
- Support for temporary tables

0.2.2
-----
- Support of named constraints
- Reflection is now able to detect named constraints
- Fixed reflection of view columns with newer SAP HANA versions
- Allow construction of more complex SELECT FOR UPDATE statements
- Fixed bug with table argument hana_table_type that could lead to
  invalid CREATE TABLE statements
- Replace standard reserved words with SAP HANA reserved words in
  ``HANAIdentifierPreparer``

0.2.1
-----
- Fix LOB handling with hdbcli driver

0.2.0
-----
- Added basic support for hdbcli driver
- Allow specification of table type via ``hana_table_type``

0.1.2
-----
- Cleanup of setup.py
- Release on PyPi

0.1.0
-----
- Added support for LOBs


0.0.1
-----
- Initial version
