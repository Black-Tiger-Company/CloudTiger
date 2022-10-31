from collections import defaultdict
from pprint import pprint
import sys
from functools import reduce

import logging

_logger = logging.getLogger(__name__)


def getFromDict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)


def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value


f = lambda: defaultdict(f)


class ConfigParser(object):
    """
    docstring
    """
    def __init__(self):
        self.config_header = []
        self.section_dict = defaultdict(f)

    def parse_config(self, fields):  # Create a new section
        self.config_header.append(" ".join(fields))

    def parse_edit(self, line):  # Create a new header
        self.config_header.append(" ".join(line))

    def parse_set(self, line):  # Key and values
        key = line[0]
        values = line[1:]
        headers = self.config_header + [key]
        setInDict(self.section_dict, headers, values)

    def parse_next(self, line):  # Close the header
        self.config_header.pop()

    def parse_end(self, line):  # Close the section
        self.config_header.pop()

    def parse_file(self, path):
        with open(path, "r") as f:
            try:
                lines = [line.strip() for line in f.read().split('\n')]
                lines = [
                    #exemple: set member "DNS" "IMAP" "IMAPS" "SMTP" => ['set member','DNS','IMAP', ...]
                    list(filter(lambda y: y, list(map(lambda x: x.strip(), line.split("\"")))))
                    for line in lines
                ]
                for line in lines:
                    if not line: # if line empty
                        continue
                    line = [*line[0].split(" "), *line[1:]] # ['set member','DNS','IMAP', ...] => ['set', 'member','DNS','IMAP', ...]
                    if line[0] in ["end","next","set", "config", "edit"]:
                        method = line[0]
                        # fetch and call method
                        getattr(ConfigParser, "parse_" + method)(self, line[1:])
            except Exception as e:
                print(e)


        f.close()
        # _logger.info(self.section_dict)
        return self.section_dict
