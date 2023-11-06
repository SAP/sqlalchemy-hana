Changelog
=========

1.0.0
-----

Breaking Changes
~~~~~~~~~~~~~~~~
- By default native booleans are used. If integer based columns should be used, specify
  ``use_native_boolean=False`` in the dburi
- Columns of SQLAlchemy type String are now created with the HANA SQL type NVARCHAR.
  The previously used HANA SQL type VARCHAR has been only designed for 7-bit ASCII character data.
  Storing other non-ASCII characters in a different encoding like UTF-8 was sometimes possible but
  never intended or recommended
  It may cause unexpected behavior for certain database-side operations like sorting or failures
  with string functions
  With the introduction of SAP HANA Cloud, the SQL type VARCHAR is also only an alias for NVARCHAR.
- Columns of SQLAlchemy type Text are now created with the HANA SQL type NCLOB instead of CLOB.
  Like the HANA SQL type VARCHAR, CLOB was designed for 7-bit ASCII character data.
  This change also ensures consistency and compatibility with SAP HANA Cloud, where CLOB is just an
  alias for NCLOB
- Removed ``pyhdb`` support because  ``pyhdb`` is out of maintenance and the GitHub repository was
  archived. Please migrate to ``hdbcli``
- Removed support for python versions below version 3.8
- Removed support for SQLAlchemy below version 1.4
- Removed support for hdbcli below version 2.10

Features
~~~~~~~~
- Official support for SQLAlchemy 1.4 and 2.0
- Official support for Python 3.11 and 3.12
- Added CI with linters and testing utilizing the SQLAchemy and alembic test suite
- Support the SAP HANA datatype ``SMALLDECIMAL``
- Support native booleans (this is the new default)
- sqlalchemy-hana is fully typed and exports its types
- The alembic dialect left the preview stage and is now included by default
- Specified the caching support explicitly (the value might change in the future)
- Support ``regexp_match`` and ``regexp_replace``
- Allow usage of "is_distinct_from" operator through a SAP HANA compatible expression
- Prefer dialect types in ``get_columns``

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
