import os
from urllib.parse import urlparse

import nox

PIP_INDEX_URL = os.environ.get('NOX_PIP_INDEX_URL', None)


@nox.session(python=['2.7', '3.4', '3.6', '3.7'], reuse_venv=True)
@nox.parametrize('sqlalchemy', ['1.0', '1.1', '1.2', '1.3'])
@nox.parametrize('hana_driver', ['hdbcli', 'pyhdb'])
def test(session, sqlalchemy, hana_driver):
    if 'NOX_SAP_HANA_URI' not in os.environ:
        session.skip(
            "Environment variable NOX_SAP_HANA_URI must be defined. "
            "Example: NOX_SAP_HANA_URI=USERNAME:PASSWORD@sap-hana-host:PORT"
        )

    pip_env = {}
    if PIP_INDEX_URL:
        session.log('Use and trust custom index url from NOX_PIP_INDEX_URL')
        pip_env = {
            'PIP_INDEX_URL': PIP_INDEX_URL,
            'PIP_TRUSTED_HOST': urlparse(PIP_INDEX_URL).netloc
        }

    session.install('sqlalchemy~={}.0'.format(sqlalchemy))
    session.install(hana_driver, env=pip_env)
    session.install('.[test]')

    dburi = 'hana+' + hana_driver + '://' + os.environ['NOX_SAP_HANA_URI']
    session.run(
        'pytest',
        '--dburi', dburi,
        '--requirements', 'sqlalchemy_hana.requirements:Requirements',
        *session.posargs
    )
