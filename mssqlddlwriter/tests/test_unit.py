from __future__ import absolute_import
from itertools import count
from os import path
import six

from nose.tools import eq_

import mssqlddlwriter as msddl
import mssqlddlwriter.tests.helpers as h


class TestOutput(object):

    @classmethod
    def setup_class(cls):
        h.clear_db()
        h.run_file_sql('ddl.sql')
        # want windows line endings
        h.run_file_sql('ddl_wle.sql')
        msddl.write(h.outdir, h.engine, print_names=False)

    def assert_files_equal(self, dir, file):
        expf = path.join(h.expdir, dir, file)
        outf = path.join(h.outdir, dir, file)
        with open(expf, 'r') as expfh:
            exp_lines = expfh.readlines()
        with open(outf, 'r') as outfh:
            contents = outfh.read()
            assert '\r\n' not in contents
            out_lines = contents.split('\n')

        # check date stamps
        assert out_lines[0].startswith('-- created:')
        assert out_lines[1].startswith('-- last updated:')

        # compare line by line
        for num, exp, out in six.moves.zip_longest(count(), exp_lines, out_lines):
            # without this, izip_longest runs forever because of count()
            if num > len(exp_lines) and num > len(out_lines):
                break

            # beginning & ending whitespace differences are ok
            exp = exp.strip() if exp else ''
            out = out.strip() if out else ''

            # skip first two lines which are date stamps
            if num < 2:
                continue
            eq_(exp, out, 'line %s: "%s" != "%s"' % (num + 1, exp, out))

    def test_users(self):
        self.assert_files_equal('tables', 'Users.sql')
        self.assert_files_equal('tables', 'Users_trg_tUsersUpdate.sql')

    def test_line_endings(self):
        self.assert_files_equal('views', 'vUsersList.sql')
