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

import os
import six
import re

from rebasehelper.utils import ProcessHelper
from rebasehelper.output_tool import BaseOutputTool
from rebasehelper.results_store import results_store


class HTMLOutputTool(BaseOutputTool):
    """
    Html generator
    """
    NAME = 'html'
    PRINT = 'html'
    out = None

    @classmethod
    def match(cls, cmd=None):
        if cmd == cls.PRINT:
            return True
        else:
            return False

    @classmethod
    def get_name(cls):
        """
        Get name of the output_tool
        :return:
        """
        return cls.NAME

    @classmethod
    def setup(cls, app):
        """
        Function for creating file handle and loading needed scripts for bootstrap
        :param app: Application instance
        :return:
        """
        cls.out = open(os.path.join(app.results_dir, 'report.html'), 'w')

        cls.out.write('<html><meta http-equiv="content-type" content="text/html; charset=utf-8" />')
        cls.out.write('<title>Rebase Helper Results</title>')
        cls.out.write('<div class="container">')
        # Load jquery
        cls.out.write('<script\
          src="https://code.jquery.com/jquery-3.2.1.min.js"\
          integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="\
          crossorigin="anonymous"></script>')
        # Load bootstrap css
        cls.out.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" \
        integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">')
        # Load bootstrap javascript
        cls.out.write('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" \
        integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" \
        crossorigin="anonymous"></script>')

    @classmethod
    def print_logs(cls):
        """
        Wrapper method for printing all logs content to HTML
        :return:
        """
        if 'builds' not in results_store.get_all():
            return
        logs = results_store.get_all()['builds']

        for version in ['old', 'new']:
            if version in logs:
                cls.print_logs_section(logs[version], version)


    @classmethod
    def print_logs_section(cls, logs, ver):
        """
        Print either all new or all old logs
        :param logs: dictionary containing dictionary of logs
        :param ver: old/new version string
        :return:
        """
        cls.out.write('<hr><h3>%s version logs</h3>' % ver)
        cls.out.write('<ul class="nav nav-tabs" role="tablist">')
        for log in logs['logs']:
            if re.search('/SRPM/', log):
                cls.write_menu_tab(ver + '_srpm_' + os.path.splitext(os.path.basename(log))[0], active=True)
            else:
                cls.write_menu_tab(ver + '_' + os.path.splitext(os.path.basename(log))[0])
        cls.out.write('</ul>')

        cls.out.write('<div class="tab-content">')
        for log in logs['logs']:
            if re.search('/SRPM/', log):
                cls.write_file_content(log, ver + '_srpm_' + os.path.splitext(os.path.basename(log))[0], active=True)
            else:
                cls.write_file_content(log, ver + '_' + os.path.splitext(os.path.basename(log))[0])
        cls.out.write('</div>')


    @classmethod
    def print_checkers(cls):
        """
        Print checkers content to HTML
        :return:
        """
        if not 'checkers' in results_store.get_all():
            return

        cls.out.write('<h2>Checkers output</h2>')

        # Generate checker menu
        cls.out.write('<ul class="nav nav-tabs" role="tablist">')
        for key in results_store.get_all()['checkers']:
            cls.write_menu_tab(key)
        cls.out.write('</ul>')

        # Generate checker content
        cls.out.write('<div class="tab-content">')
        for checker, checker_dict in six.iteritems(results_store.get_all()['checkers']):
            for path in checker_dict:
                cls.write_file_content(path, checker)
        cls.out.write('</div>')

    @classmethod
    def write_menu_tab(cls, key, active=False):
        """
        Write single menu tab
        :param key: name for the tab
        :param active: set when the tab should have active class by default
        :return:
        """
        if active:
            cls.out.write(
                """
               <li class="active" role="presentation"><a href="#%s" aria-controls="%s" role="tab" data-toggle="tab">%s</a></li> 
                """ % (key, key, key))
        else:
            cls.out.write(
                """
               <li role="presentation"><a href="#%s" aria-controls="%s" role="tab" data-toggle="tab">%s</a></li> 
                """ % (key, key, key))

    @classmethod
    def write_file_content(cls, filename, key, active=False):
        """
        Print content of a file to HTML
        :param filename: name of a file that will be printed to HTML
        :param key: ID of HTML tag containing file content
        :param active: active is set when a tag should have active class by default
        :return:
        """
        with open(filename, 'r') as f:
            if active:
                cls.out.write('<div role="tabpanel" class="well tab-pane fade pre-scrollable active in" id="%s">' % key)
            else:
                cls.out.write('<div role="tabpanel" class="well tab-pane fade pre-scrollable" id="%s">' % key)
            for line in f.readlines():
                cls.out.write(line + '<br>')
            cls.out.write('</div>')

    @classmethod
    def print_patches(cls):
        """
        Print information about patches to the HTML
        :return:
        """

        cls.out.write('<h2>Changes in patches</h2>')
        cls.out.write('<div class="well">')

        for patches in ['inapplicable', 'modified', 'deleted']:
            cls.print_patches_section(patches)

        # End well div
        cls.out.write('</div>')

    @classmethod
    def print_patches_section(cls, key):
        """
        Print patches from the given group
        :param key: key for the patches dictionary
        :return:
        """
        patches = results_store.get_all()['patches']

        if key in patches:
            cls.out.write('<h3>%s patches</h3>' % key)
            for patch in patches[key]:
                cls.out.write('%s<br>' % patch)


    @classmethod
    def print_changes_patch(cls):
        """
        Print content of changes.patch to HTMl
        :return:
        """
        changes = results_store.get_changes_patch()['changes_patch']

        cls.out.write('<h2>Changes between old and new source patches</h2>')
        cls.out.write('<p>These changes are stored in <a href="%s">%s</a></p>' % (changes, changes))
        with open(changes, 'r') as file:
            cls.out.write('<div class="well pre-scrollable">')
            for line in file.readlines():
                cls.out.write('%s<br>' % line)
        cls.out.write('</div>')

    @classmethod
    def run(cls, log, app=None):
        """
        This function is a wrapper for the whole output_generator functionality
        :param message: Contains rebase error
        :param app: Application instance
        :return:
        """

        cls.setup(app)

        results = results_store.get_result_message()
        # Print result of the rebase
        if 'success' in results:
            cls.out.write(
                '<h1>Rebase to %s was <span style="color:green; font-weight:bold"><br>SUCCESSFULL</span></h1>'
                % app.conf.sources)
        else:
            cls.out.write(
                '<h1>Rebase to %s <span style="color:red; font-weight:bold"><br>FAILED</span></h1>' % app.conf.sources)

            # Print error message to the html
            try:
                cls.out.write('<div class="well">')
                cls.out.write(results['fail'])
                cls.out.write('</div>')

                cls.out.write('<h2>Last 20 lines of %s</h2>' % log)
                ProcessHelper.run_subprocess(['tail', log, '-n20'], output='error.log')
                with open('error.log', 'r') as f:
                    cls.out.write('<div class="well">')
                    for l in f.readlines():
                        cls.out.write('%s<br>' % l)
                    cls.out.write('</div>')
                os.unlink('error.log')

            except:
                # No particular log should be displayed
                pass

        try:
            # Generate directory structure page
            ProcessHelper.run_subprocess(['tree', app.results_dir, '-H', './'],
                                         output=os.path.join(app.results_dir, 'dir_struct.html'))
            cls.out.write('Please see the whole <a href="./dir_struct.html">Rebase Helper Results directory</a>\
            for manual file browsing.<br>')
        except:
            pass

        cls.print_changes_patch()

        cls.print_patches()

        cls.print_checkers()

        cls.print_logs()

        cls.out.write('<hr><p class="text-center">Please report problems or new ideas to \
        <a target="_blank" href="https://github.com/rebase-helper/rebase-helper/issues">\
        https://github.com/rebase-helper/rebase-helper/issues</a></p>')

        cls.out.write('</div>')
        cls.out.write('</html>')
