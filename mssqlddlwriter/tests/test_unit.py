import mssqlddlwriter as msddl
import mssqlddlwriter.tests.helpers as h


class TestOutput(object):

    @classmethod
    def setup_class(cls):
        h.clear_db()
        h.run_file_sql('ddl.sql')
        #msddl.write(h.outdir, h.engine)

    def test_index(self):
        assert True
