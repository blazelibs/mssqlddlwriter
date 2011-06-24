from os import path
from shutil import rmtree

import sqlalchemy as sa
import sqlalchemy.schema as sasch
import sqlalchemy.sql as sasql
import sqlalchemy.orm as saorm

from mssqlddlwriter.utils import mkdirs, getversion

from sqlalchemy.ext.declarative import declarative_base

VERSION = getversion()

Base = declarative_base()
Session = saorm.sessionmaker()
ses = None
engine = None

_sysobjs_sql_parent = """
SELECT o.object_id, O.[name], O.type, create_date, modify_date
FROM sys.objects O
where O.type <> ('D', 'PK')
and parent_id = %s
ORDER BY name
"""

_sql_modules_sql = """
SELECT uses_ansi_nulls, uses_quoted_identifier, definition
FROM sys.sql_modules
where object_id = %s
"""

class SysSchema(Base):
    __tablename__ = 'schemas'
    __table_args__ = {'schema':'sys'}

    id = sa.Column('schema_id', sa.Integer, nullable=False, primary_key=True)
    name = sa.Column(sa.Unicode(128), nullable=False)

class SysObject(Base):
    __tablename__ = 'objects'
    __table_args__ = {'schema':'sys'}

    id = sa.Column('object_id', sa.Integer, nullable=False, primary_key=True)
    parent_object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False)
    parent = saorm.relation('SysObject', lazy=False, remote_side=[id])
    type = sa.Column(sa.String(2), nullable=False)
    name = sa.Column(sa.Unicode(128), nullable=False)
    create_date = sa.Column(sa.DateTime, nullable=False)
    modify_date = sa.Column(sa.DateTime, nullable=False)
    is_ms_shipped = sa.Column(sa.Integer, nullable=False)
    schema_id = sa.Column(sa.Integer, sa.ForeignKey('sys.schemas.schema_id'), nullable=False)
    schema = saorm.relation(SysSchema, lazy=False)

    def getwriter(self, dump_path):
        type = self.type.strip()
        args = (dump_path, self.id, self.name, self.type, self.create_date, self.modify_date, self)
        if type == 'U':
            return DbTable(*args)
        if type == 'V':
            return DbView(*args)
        if type == 'P':
            return DbStoredProcedure(*args)
        if type in ('FN', 'IF', 'TF'):
            return DbFunction(*args)
        if type == 'TR':
            return DbTrigger(*args)
        if type == 'UQ':
            return DbUniqueConstraint(*args)
        if type == 'C':
            return DbCheckConstraint(*args)
        raise ValueError('type "%s" not supported' % type)

class SysColumn(Base):
    __tablename__ = 'columns'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=False)
    column_id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=False)
    name = sa.Column(sa.Unicode(128), nullable=False)

class SysFileGroup(Base):
    __tablename__ = 'filegroups'
    __table_args__ = {'schema':'sys'}

    name = sa.Column(sa.Unicode(128), nullable=False, primary_key=True)
    data_space_id = sa.Column(sa.Integer, nullable=False)

class SysIndexColumn(Base):
    __tablename__ = 'index_columns'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.indexes.object_id'), sa.ForeignKey('sys.columns.object_id'), nullable=False, primary_key=True, autoincrement=False)
    index_id = sa.Column(sa.Integer, sa.ForeignKey('sys.indexes.index_id'), nullable=False, primary_key=True, autoincrement=False)
    index_column_id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=False)
    column_id = sa.Column(sa.Integer, sa.ForeignKey('sys.columns.column_id'), nullable=False)
    key_ordinal = sa.Column(sa.Integer, nullable=False)
    is_descending_key = sa.Column(sa.Integer, nullable=False)

    column = saorm.relationship(SysColumn, lazy=False, primaryjoin=sasql.and_(
                        SysColumn.object_id == object_id,
                        SysColumn.column_id == column_id
                    )
                )

class SysIndex(Base):
    __tablename__ = 'indexes'
    __table_args__ = {'schema':'sys'}

    parent_id = sa.Column('object_id', sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False, primary_key=True, autoincrement=False)
    index_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    name = sa.Column(sa.Unicode(128), nullable=False)
    type_desc = sa.Column(sa.Unicode(60), nullable=False)
    data_space_id = sa.Column(sa.Integer, sa.ForeignKey('sys.filegroups.data_space_id'), nullable=False)
    is_primary_key = sa.Column(sa.Integer, nullable=False)
    is_unique_constraint = sa.Column(sa.Integer, nullable=False)

    parent = saorm.relation(SysObject, lazy=False)
    data_space = saorm.relation(SysFileGroup, lazy=False)
    columns = saorm.relation(SysIndexColumn, lazy=False, order_by=SysIndexColumn.key_ordinal,
                    primaryjoin=sasql.and_(
                        SysIndexColumn.object_id == parent_id,
                        SysIndexColumn.index_id == index_id
                    )
                )

    def getwriter(self, dump_path):
        return DbIndex(dump_path, None, self.name, '', None, None, self)

class SysForeignKey(Base):
    __tablename__ = 'foreign_keys'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    parent_object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False)
    name = sa.Column(sa.Unicode(128), nullable=False)
    delete_referential_action_desc = sa.Column(sa.Unicode(60), nullable=False)
    update_referential_action_desc = sa.Column(sa.Unicode(60), nullable=False)

    def ondelete(self):
        desc = self.delete_referential_action_desc
        if desc == 'NO_ACTION':
            return None
        return desc.replace('_', ' ')

    def onupdate(self):
        desc = self.update_referential_action_desc
        if desc == 'NO_ACTION':
            return None
        return desc.replace('_', ' ')

class SysCheckConstraint(Base):
    __tablename__ = 'check_constraints'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    parent_object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False)
    name = sa.Column(sa.Unicode(128), nullable=False)
    definition = sa.Column(sa.Text, nullable=False)

    parent = saorm.relation(SysObject, lazy=False)

class ObjWriter(object):
    def __init__(self, dump_path, oid, name, type, createts, modts, so):
        self.dump_path = dump_path
        self.oid = oid
        self.name = name
        self.type = type.strip()
        self.createts = createts
        self.modts = modts
        self.definition = None
        self.ansi_nulls = None
        self.quoted_ident = None
        self.so = so

        self.type_path = path.join(dump_path, self.folder_name)
        self.file_path = path.join(self.type_path, '%s.sql' % self.name)

        self.populate()

    def populate(self):
        res = engine.execute(_sql_modules_sql, [self.oid])
        if not res:
            return
        row = res.fetchone()
        if not row:
            return
        self.definition = row['definition']
        self.ansi_nulls = bool(row['uses_ansi_nulls'])
        self.quoted_ident = bool(row['uses_quoted_identifier'])

    def ddl(self):
        return self.definition or ''

    def file_output(self):
        output = []
        output.append('-- created: %s' % self.createts)
        output.append('-- last updated: %s' % self.modts)
        if self.ansi_nulls:
            output.append('--statement-break')
            output.append('SET ANSI_NULLS ON')
        if self.quoted_ident:
            output.append('--statement-break')
            output.append('SET QUOTED_IDENTIFIER ON')
        output.append('')
        output.append('--statement-break')
        output.append(self.ddl().replace('\r\n', '\n').strip())
        return '\n'.join(output)

    def write(self):
        with open(self.file_path, 'wb') as fp:
            fp.write( self.file_output() )

class DbTable(ObjWriter):
    folder_name = 'tables'

    def ddl(self):
        output_ddl = []
        t = sa.Table(self.name, Base.metadata, autoload=True, autoload_with=engine, schema=self.so.schema.name)

        # SA doesn't currently pick up foreign key ON DELETE/UPDATE, so we have
        # to patch those values in
        for c in t.constraints:
            if isinstance(c, sasch.ForeignKeyConstraint):
                sysfk = ses.query(SysForeignKey).filter_by(parent_object_id = self.oid, name=c.name).one()
                c.ondelete = sysfk.ondelete()
                c.onupdate = sysfk.onupdate()
        table_ddl = str(sasch.CreateTable(t).compile(engine)).strip()
        output_ddl.append(table_ddl)
        uc_ddl = self.uc_ddl().strip()
        if uc_ddl:
            output_ddl.append(uc_ddl)
        cc_ddl = self.cc_ddl().strip()
        if cc_ddl:
            output_ddl.append(cc_ddl)
        idx_ddl = self.idx_ddl().strip()
        if idx_ddl:
            output_ddl.append(idx_ddl)
        return '\n\n'.join(output_ddl)

    def write(self):
        ObjWriter.write(self)
        self.trigger_ddl()

    def uc_ddl(self):
        uc_ddl = []
        res = ses.query(SysObject).filter(
            sasql.and_(
                SysObject.parent_object_id == self.oid,
                SysObject.type == u'UQ'
            )
        ).order_by(SysObject.name).all()

        for obj in res:
            uc_ddl.append('--statement-break')
            uc_ddl.append(obj.getwriter(self.dump_path).ddl())

        return '\n'.join(uc_ddl)

    def cc_ddl(self):
        cc_ddl = []
        res = ses.query(SysObject).filter(
            sasql.and_(
                SysObject.parent_object_id == self.oid,
                SysObject.type == u'C'
            )
        ).order_by(SysObject.name).all()


        for obj in res:
            cc_ddl.append('--statement-break')
            cc_ddl.append(obj.getwriter(self.dump_path).ddl())

        return '\n'.join(cc_ddl)

    def idx_ddl(self):
        idx_ddl = []
        res = ses.query(SysIndex).filter(
            sasql.and_(
                SysIndex.parent_id == self.oid,
                SysIndex.is_primary_key == 0,
                SysIndex.is_unique_constraint == 0,
            )
        ).order_by(SysIndex.index_id).all()


        for obj in res:
            idx_ddl.append('--statement-break')
            idx_ddl.append(obj.getwriter(self.dump_path).ddl())

        return '\n'.join(idx_ddl)

    def trigger_ddl(self):
        trigger_sql = []
        res = ses.query(SysObject).filter(
            sasql.and_(
                SysObject.parent_object_id == self.oid,
                SysObject.type == u'TR'
            )
        ).order_by(SysObject.name).all()
        for obj in res:
            twr = obj.getwriter(self.dump_path)
            twr.write()

class DbView(ObjWriter):
    folder_name = 'views'

class DbStoredProcedure(ObjWriter):
    folder_name = 'sps'

class DbFunction(ObjWriter):
    folder_name = 'functions'

class DbTrigger(ObjWriter):
    folder_name = 'tables'

    def write(self):
        self.file_path = path.join(self.type_path, '%s_trg_%s.sql' % (self.so.parent.name, self.name))
        ObjWriter.write(self)

class IndexMixin(object):

    def index_ending_ddl(self, idx):
        col_ddl = []
        for c in idx.columns:
            col_ddl.append('[%s] %s' % (c.column.name, 'DESC' if c.is_descending_key else 'ASC'))
        return '(%s) ON [%s]' % (', '.join(col_ddl), idx.data_space.name)

class DbIndex(ObjWriter, IndexMixin):
    folder_name = ''

    def ddl(self):
        return 'CREATE %s INDEX [%s] ON [%s].[%s] %s' % (
                self.so.type_desc,
                self.name,
                self.so.parent.schema.name,
                self.so.parent.name,
                self.index_ending_ddl(self.so)
            )

class DbConstraintBase(ObjWriter):

    def alter_table_ddl(self):
        ddl = []
        ddl.append('ALTER TABLE')
        ddl.append('[%s].[%s]' % (self.so.parent.schema.name, self.so.parent.name))
        ddl.append('ADD CONSTRAINT [%s]' % self.name)
        return ' '.join(ddl)

class DbUniqueConstraint(DbConstraintBase, IndexMixin):
    folder_name = ''

    def ddl(self):
        idx = ses.query(SysIndex).filter_by(parent_id=self.so.parent.id, name=self.name).one()
        return '%s UNIQUE %s' % (self.alter_table_ddl(), self.index_ending_ddl(idx))

class DbCheckConstraint(DbConstraintBase):
    folder_name = ''

    def ddl(self):
        cc = ses.query(SysCheckConstraint).filter_by(parent_object_id=self.so.parent.id, name=self.name).one()
        return '%s CHECK (%s)' % (self.alter_table_ddl(), cc.definition)

_write_dirs = (
    'tables',
    'views',
    'sps',
    'functions'
)

def write(dump_path, given_engine, print_names=True):
    global ses
    global engine

    engine = given_engine
    if engine.dialect.name != 'mssql':
        raise Exception('ERROR: not connected to MSSQL database')

    Base.metadata.bind = engine
    Session.configure(bind=engine)
    ses = Session()

    # delete files that are there and recreate the folders
    for d in _write_dirs:
        target = path.join(dump_path, d)
        if path.isdir(target):
            rmtree(target)
        mkdirs(target)

    # create new files
    res = ses.query(SysObject).filter(
        sasql.and_(
            SysObject.type.in_(('U', 'V', 'P', 'FN', 'IF', 'TF')),
            SysObject.is_ms_shipped == 0,
        )).order_by(SysObject.name).all()

    for obj in res:
        wr = obj.getwriter(dump_path)
        if print_names:
            print obj.name
        wr.write()
