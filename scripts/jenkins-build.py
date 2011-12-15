import os
from jenkinsutils import BuildHelper

package = 'MSSQLDDLWriter'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create(delete_first=False)

## install package w/ setuptools develop command
bh.vecall('python', 'setup.py', '--quiet', 'develop_with_nose')

## install pymssql
#bh.vepycall('easy_install', 'http://pymssql.googlecode.com/files/pymssql-2.0.0b1_dev_20111018-py2.6-linux-x86_64.egg')

## run tests
bh.vepycall('nosetests', 'mssqlddlwriter', '--with-xunit', '-s')
