import os
from setuptools import setup, find_packages

source_location = os.path.abspath(os.path.dirname(__file__))
def get_version():
    with open(os.path.join(source_location, "VERSION")) as version:
        return version.readline().strip()

setup(
    name="sqlalchemy-hana",
    version=get_version(),
    license="Apache License Version 2.0",
    url="https://github.com/SAP/sqlalchemy-hana/",
    author="Christoph Heer",
    author_email="christoph.heer@sap.com",
    description="SQLAlchemy dialect for SAP HANA",
    packages=find_packages(exclude=("test", "test.*",)),
    zip_safe=False,
    install_requires=[
        "sqlalchemy>=1.2.0"
    ],
    extras_require={
        "test": [
            "pytest>=2.5.2",
            "mock>=1.0.1"
        ],
        "pyhdb": [
            "pyhdb>=0.3.1"
        ]
    },
    classifiers=[ # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points = {
        "sqlalchemy.dialects": [
            "hana = sqlalchemy_hana.dialect:HANAHDBCLIDialect",
            "hana.hdbcli = sqlalchemy_hana.dialect:HANAHDBCLIDialect",
            "hana.pyhdb = sqlalchemy_hana.dialect:HANAPyHDBDialect"
        ]
     },
)
