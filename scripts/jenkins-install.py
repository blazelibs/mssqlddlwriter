from __future__ import absolute_import
import os
from jenkinsutils import BuildHelper

package = 'MSSQLDDLWriter'
type = 'install'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# install package
bh.vecall('pip', 'install', "https://bitbucket.org/blazelibs/mssqlddlwriter/get/default.zip#egg=mssqlddlwriter")

# import module as our "test"
bh.vecall('python', '-c', 'import mssqlddlwriter')
