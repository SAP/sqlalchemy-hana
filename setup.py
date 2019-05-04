# Copyright 2015 SAP SE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

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
        "sqlalchemy>=1.0.0"
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
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
