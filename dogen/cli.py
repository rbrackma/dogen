# -*- coding: utf-8 -*-

import argparse
import logging
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dogen.generator import Generator
from dogen.version import version
from dogen.errors import Error
from dogen.plugin import Plugin

import dogen.plugins.dist_git
import dogen.plugins.cct
import dogen.plugins.rpm

class MyParser(argparse.ArgumentParser):

    def error(self, message):
        self.print_help()
        sys.stderr.write('\nError: %s\n' % message)
        sys.exit(2)

class CLI(object):

    def __init__(self):
        self.log = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.WARNING)
        requests.packages.urllib3.disable_warnings()

    def run(self):
        parser = MyParser(
            description='Dockerfile generator tool', formatter_class=argparse.RawDescriptionHelpFormatter)

        epilog = "List of available plugins:\n"

        plugins = Plugin.list()

        for plugin in plugins:
            key, description = plugin.info()
            epilog += "\n  * %s:\t%s" % (key, description)

        parser.epilog = epilog

        parser.add_argument(
            '-v', '--verbose', action='store_true', help='Verbose output')

        parser.add_argument(
            '--version', action='version', help='Show version and exit', version=version)

        parser.add_argument('--without-sources', '--ws', action='store_true', help='Do not process sources, only generate Dockerfile')
        parser.add_argument('--skip-ssl-verification', action='store_true', help='Should we skip SSL verification when retrieving data?')
        parser.add_argument('--scripts', help='Location of the scripts directory containing script packages.')
        parser.add_argument('--additional-script', action='append', help='Location of additional script (can be url). Can be specified multiple times.')
        parser.add_argument('--template', help='Path to custom template (can be url)')
        parser.add_argument('--plugin', action='append', help='Plugin to be enabled. Can be specified multiple times.')

        parser.add_argument('path', help="Path to yaml descriptor to process")
        parser.add_argument('output', help="Path to directory where generated files should be saved")

        args = parser.parse_args()

        if args.verbose:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

        if args.skip_ssl_verification:
            ssl_verify = False
        else:
            ssl_verify = None

        self.log.debug("Running version %s", version)

        enabled_plugins = []

        if args.plugin:
            for plugin in plugins:
                if plugin.info()[0] in args.plugin:
                    enabled_plugins.append(plugin)

        try:
            Generator(self.log, args.path, args.output, template=args.template, scripts=args.scripts, additional_scripts=args.additional_script, without_sources=args.without_sources, plugins=enabled_plugins, ssl_verify=ssl_verify).run()
        except KeyboardInterrupt as e:
            pass
        except Error as e:
            self.log.exception(e)
            sys.exit(1)


def run():
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    run()
