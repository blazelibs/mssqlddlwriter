MSSQL DDL Writer
================

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

Known Issues
-------------

Some detail on some objects is not currently captured.  Track issues here:

https://bitbucket.org/rsyring/mssqlddlwriter/issues

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

