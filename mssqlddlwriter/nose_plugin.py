import ConfigParser
import os

from nose.plugins import Plugin

import mssqlddlwriter.tests.helpers as th

_parser = ConfigParser.ConfigParser({
    'server': 'localhost',
    'username': 'sa',
    'password': '',
    'database': 'tempdb',
    'port': '1433',
    'ipaddress': '127.0.0.1',
    'instance': '',
})

class ConfigPlugin(Plugin):
    enabled = True
    config_section = ''

    def options(self, parser, env=os.environ):
        parser.add_option("--mdw-section",
                          type="string",
                          default=env.get('MDW_TEST_CONFIG', 'DEFAULT'),
                          help="The name of the section to use from tests.cfg"
                        )

        Plugin.options(self, parser, env=env)

    def configure(self, options, config):
        """Configure the plugin"""

        _parser.read(th.cfgpath)
        section = options.mdw_section

        if not _parser.has_section(section) and section != 'DEFAULT':
            raise ValueError('the tests.cfg file does not have section: %s' % section)

        th.config.server = _parser.get(section, 'server')
        th.config.user= _parser.get(section, 'username')
        th.config.password = _parser.get(section, 'password')
        th.config.database = _parser.get(section, 'database')
        th.config.port = _parser.get(section, 'port')
        th.config.ipaddress = _parser.get(section, 'ipaddress')
        th.config.instance = _parser.get(section, 'instance')
        th.config.orig_decimal_prec = decimal.getcontext().prec
