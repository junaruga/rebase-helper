# -*- coding: utf-8 -*-
#
# This tool helps you to rebase package to the latest version
# Copyright (C) 2013-2014 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# he Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Authors: Petr Hracek <phracek@redhat.com>
#          Tomas Hozza <thozza@redhat.com>
from __future__ import print_function

import os
import six
import pkg_resources

from rebasehelper.exceptions import RebaseHelperError
from rebasehelper.logger import LoggerHelper, logger, logger_report
from rebasehelper.results_store import results_store
from rebasehelper import settings
from colors import red, green, yellow


class BaseOutputTool(object):

    """
    Class used for testing and other future stuff, ...
    Each method should overwrite method like run_check
    """

    DEFAULT = False
    PRINT = 'name'

    def __init__(self, output_tool=None):
        if output_tool is None:
            raise TypeError("Expected argument 'tool' (pos 1) is missing")
        self._output_tool_name = output_tool
        self._tool = None

        for output in output_tools_runner.output_tools.values():
            if output.match(self._output_tool_name):
                self._tool = output

        if self._tool is None:
            raise NotImplementedError("Unsupported output tool")

    @classmethod
    def get_report_path(cls, app):
        return os.path.join(app.results_dir, 'report.' + cls.PRINT)

    @classmethod
    def match(cls, cmd=None, *args, **kwargs):
        """Checks if tool name matches the desired one."""
        raise NotImplementedError()

    @classmethod
    def print_cli_summary(cls, app):
        """
        Print report of the rebase

        :param app: Application instance
        """

        print(yellow("\nRebase helper finished\n"))

        cls.print_patches_cli()

        print(yellow('\nGenerated files:'))

        print("{0}:\n{1}".format('Debug log', app.debug_log_file))
        print("{0}:\n{1}".format('Old build logs and (S)RPMs', os.path.join(app.results_dir, 'old')))
        print("{0}:\n{1}".format('New build logs and (S)RPMs', os.path.join(app.results_dir, 'new')))
        print()
        print("{0}:\n{1}".format('Rebased sources', app.rebased_sources_dir))
        print("{0}:\n{1}".format('Patch containing changes', os.path.join(app.results_dir, 'changes.patch')))
        print()
        print("{0}:\n{1}".format('%s report' % cls.PRINT, os.path.join(app.results_dir, 'report.' + cls.PRINT)))

        result = results_store.get_result_message()
        if not app.conf.patch_only:
            if 'success' in result:
                print(green("\n%s" % result['success']))
            else:
                print(red("\n%s" % result['fail']))
        else:
            print("\nPatching to %s" % app.conf.sources, green("FINISHED"))


    @classmethod
    def print_patches_cli(cls):
        """
        Print info about patches
        :return:
        """
        patch_dict = {
            'inapplicable': 'red',
            'modified': 'green',
            'deleted': 'green'}

        for patch_type, color in six.iteritems(patch_dict):
            cls.print_patches_section_cli(patch_type, color)

    @classmethod
    def print_patches_section_cli(cls, patch_type, color):
        """
        Print info about one of the patches key section
        :param patch_type: string containing key for the patch_dict
        :param color: color used for the message printing
        :return:
        """
        patches = results_store.get_patches()
        if patch_type in patches:
            if color == 'red':
                print(red("%s patches:" % patch_type))
            else:
                print(green("%s patches:" % patch_type))
            for patch in patches[patch_type]:
                print(patch)

    @classmethod
    def run(cls):
        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        raise NotImplementedError()

    def print_information(self, path, results=results_store):
        """Build sources."""
        logger.debug("Printing information using '%s'", self._output_tool_name)
        return self._tool.print_summary(path, results)

    @staticmethod
    def get_supported_tools():
        """Returns list of supported output tools"""
        return output_tools_runner.output_tools.keys()

    @staticmethod
    def get_default_tool():
        """Returns default output tool"""
        default = [k for k, v in six.iteritems(output_tools_runner.output_tools) if v.DEFAULT]
        return default[0] if default else None


class OutputToolRunner(object):
    """
    Class representing the process of running various output generators.
    """

    output_tools = {}

    def __init__(self):
        """
        Constructor of OutputGeneratorRunner class.
        """
        for entrypoint in pkg_resources.iter_entry_points('rebasehelper.output_tools'):
            try:
                output_tool = entrypoint.load()
            except ImportError:
                # silently skip broken plugin
                continue
            try:
                self.output_tools[output_tool.PRINT] = output_tool
            except (AttributeError, NotImplementedError):
                # silently skip broken plugin
                continue

    @classmethod
    def run_output_tools(self, log=None, app=None):
        """
        Runs all spec hooks.

        :param log: Log that probably contains the important message
        :param app: Rebased spec file object
        """
        for name, output_tool in six.iteritems(self.output_tools):
            if output_tool.match(app.conf.outputtool):
                output_tool.run(log, app)
                output_tool.print_cli_summary(app)
                break

# Global instance of OutputGeneratorRunner. It is enough to load it once per application run.
output_tools_runner = OutputToolRunner()
#output_tools = output_tools_runner.output_tools
