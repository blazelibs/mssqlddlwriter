import ConfigParser
import os

from nose.plugins import Plugin
import sqlalchemy as sa

import mssqlddlwriter.tests.helpers as th

_parser = ConfigParser.ConfigParser({
    'sa_url': ''
})

class ConfigPlugin(Plugin):
    enabled = True

    def options(self, parser, env=os.environ):
        parser.add_option(
            "--msddl-section",
            type="string",
            default=env.get('MSDDL_TEST_CONFIG', 'DEFAULT'),
            help="The name of the section to use from tests.cfg"
        )
        parser.add_option(
            "--msddl-sa-url",
            type="string",
            default=env.get('MSDDL_SA_URL', None),
            help="An SQLAlchemy connection string URL"
        )

        Plugin.options(self, parser, env=env)

    def configure(self, options, config):
        """Configure the plugin"""

        if options.msddl_sa_url is None:
            _parser.read(th.cfgpath)
            section = options.msddl_section

            if not _parser.has_section(section) and section != 'DEFAULT':
                raise ValueError('the tests.cfg file does not have section: %s' % section)

            th.config.sa_url = _parser.get(section, 'sa_url')
        else:
            th.config.sa_url = options.msddl_sa_url

    def begin(self):
        th.engine = sa.create_engine(th.config.sa_url)
