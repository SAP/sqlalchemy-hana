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

# configuration used when running tests via nose

from sqlalchemy.dialects import registry

registry.register("hana", "sqlalchemy_hana.dialect", "HANADialect")

from sqlalchemy.testing import runner


# use this in setup.py 'test_suite':
# test_suite="run_tests.setup_py_test"
def setup_py_test():
    runner.setup_py_test()

if __name__ == '__main__':
    runner.main()
