from rebasehelper.output_tool import BaseOutputTool
from rebasehelper.exceptions import RebaseHelperError
from rebasehelper.logger import LoggerHelper, logger, logger_report
from rebasehelper.results_store import results_store
import json
import os

class JSONOutputTool(BaseOutputTool):

    """ JSON output tool. """

    PRINT = "json"

    @classmethod
    def match(cls, cmd=None):
        if cmd == cls.PRINT:
            return True
        else:
            return False

    @classmethod
    def run(cls, message, app):
        """
        Function is used for storing output dictionary into JSON structure
        JSON output file is stored into path
        :return:
        """
        path = cls.get_report_path(app)

        with open(path, 'w') as outputfile:
            json.dump(results_store.get_all(), outputfile, indent=4, sort_keys=True)
