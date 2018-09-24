import re
from os import walk


class FilePath(object):
    """
    Descriptor for simplifying file path operations
    """

    base_path = ""

    def __init__(self, relative_path : str, filename : str, base_path : str = None):
        self.relative_path = relative_path
        self.filename = filename
        if base_path:
            self.base_path = base_path

    def get_relative_file(self):
        return self.relative_path + self.filename

    def get_absolute_file(self):
        return self.base_path + self.relative_path + self.filename


def recursive_scanner(base_path: str, short_path: str):
    files = []
    f = []
    d = []
    for (dirpath, dirnames, filenames) in walk(base_path + short_path):
        f.extend(filenames)
        d.extend(dirnames)
        break

    for file in f:
        if (re.match('(.*).mid', file) != None):
            files = files + [FilePath(short_path, file)]

    for directory in d:
        files.extend(recursive_scanner(
            base_path, short_path + directory + "/"))

    return files