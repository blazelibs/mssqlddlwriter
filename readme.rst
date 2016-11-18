MSSQL DDL Writer
================

.. image:: https://ci.appveyor.com/api/projects/status/ssle091vl9l9x947?svg=true
    :target: https://ci.appveyor.com/project/level12/mssqlddlwriter

.. image:: https://codecov.io/gh/blazelibs/mssqlddlwriter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/blazelibs/mssqlddlwriter

This project facilitates the writing of Microsft SQL Server DDL out to files.

Example Usage
-------------

Usage is pretty simple::

    import mssqlddlwriter
    import sqlalchemy as sa

    engine = sa.create_engine('mssql://...')
    mypath = '../myproject/dbmirror'
    mssqlddlwriter(mypath, engine, print_names=True)

This will result in the DDL of the objects in the database getting written out
to files in `mypath`.

Running Tests
-------------

Running the tests requires a config file and a nose plugin. A template for the
config file is in `mssqlddlwriter/tests/tests.cfg.tpl`. Copy it to `tests.cfg`
in the same folder, and edit to have the necessary database connection to test.

The nose plugin is enabled by installing mssqlddlwriter in your environment with
the `develop_with_nose` command:

    python setup.py develop_with_nose

If the plugin is not enabled, you will encounter an error when running `nosetests`
saying that the engine is None.

The plugin enables a couple of options for nose:

 - `--msddl-section`: specifies the section of `tests.cfg` to use for tests
 - `--msddl-sa-url`: pass a database URL manually, bypassing the config file

Known Issues
-------------

Some detail on some objects is not currently captured.  Track issues here:

https://bitbucket.org/rsyring/mssqlddlwriter/issues

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

