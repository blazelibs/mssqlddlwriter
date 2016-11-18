from __future__ import absolute_import
from collections import OrderedDict
from os import path
import six


class Config(object):
    pass


config = Config()

cdir = path.dirname(__file__)
cfgpath = path.join(cdir, 'tests.cfg')
expdir = path.join(cdir, 'expected')
outdir = path.join(cdir, 'output')

# will get set to an SA engine by the nose plugin
engine = None


def clear_db():
    mapping = OrderedDict()
    mapping['P'] = 'drop procedure [%(name)s]'
    mapping['C'] = 'alter table [%(parent_name)s] drop constraint [%(name)s]'
    mapping[('FN', 'IF', 'TF')] = 'drop function [%(name)s]'
    mapping['V'] = 'drop view [%(name)s]'
    mapping['F'] = 'alter table [%(parent_name)s] drop constraint [%(name)s]'
    mapping['U'] = 'drop table [%(name)s]'
    delete_sql = []
    for type, drop_sql in six.iteritems(mapping):
        sql = 'select name, object_name( parent_object_id ) as parent_name '\
              'from sys.objects where type in (\'%s\')' % '", "'.join(type)
        res = engine.execute(sql)
        for row in res:
            delete_sql.append(drop_sql % dict(row))

    for sql in delete_sql:
        engine.execute(sql)


def run_file_sql(fname):
    full_path = path.join(cdir, fname)
    with open(full_path, 'r') as fh:
        sql_str = fh.read()
    _execute_sql_string(sql_str)


def _execute_sql_string(sql):
    try:
        for statement in sql.split('--statement-break'):
            statement.strip()
            if statement:
                engine.execute(statement)
    except Exception:
        raise
