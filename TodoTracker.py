import argparse
import os
import time
import io

import sys

version = 'V1.01.02'
versiondate = 'Wed Sep 21 05:06:28 2016'
buildname = 'TodoTracker'
versionstr = '%s %s (c) Eclectick Media Solutions, circa %s' % (buildname,
                                                                version,
                                                                versiondate)


class Searcher:
    def __init__(self, path, types, extensions=list(), files=list(),
                 epaths=list(), quiet=False):
        if not os.access(path, os.F_OK):
            raise OSError('Could not access search path')

        if type(types) is not list:
            raise ValueError('file types must be list')

        self.path = path
        self.types = types
        self.exclude = {
            'extensions': extensions,
            'files': files,
            'paths': epaths
        }
        self.log = io.StringIO()
        self.log.write('TODO MASTER (%s)'
                       '                  *Generated by github.com/'
                       'eclectickmedia/todotracker*\n--------\n' % time.ctime())

        self._search_path()
        if not quiet:
            print(self.log.getvalue())

    def _validate_path(self, path):
        for epath in self.exclude['paths']:
            if path.count(epath):
                return False

            return True

    def _validate_file(self, file):
            for efile in self.exclude['files']:
                if file.count(efile):
                    return False

            for ext in self.exclude['extensions']:
                if file.count(ext):
                    return False

            for t in self.types:
                if file.count(t):
                    return True

            else:  # no file type returned true
                return False

    def _search_path(self):
        for path, dirs, files in os.walk(self.path):
            if not self._validate_path(path):
                pass

            for file in files:
                if not self._validate_file(file):
                    pass
                else:
                    if self._parse_file(path, file):
                        pass

    def _parse_file(self, path, file):
        has_todo = False
        temp_log = io.StringIO()
        if os.access(os.path.join(path, file), os.F_OK):
            with open(os.path.join(path, file)) as infile:
                for i, line in enumerate(infile):
                    if line.count('# TODO'):
                        temp_log.write('%s:%s' % (i, line))
                        has_todo = True
            if has_todo:
                self.log.write('\n\n%s\n\n--------\n\n' % os.path.join(path,
                                                                       file))
                self.log.write(temp_log.getvalue())

            return has_todo

        else:
            raise RuntimeError('Could not open %s!' % os.path.join(path, file))

    def write_file(self, outpath):
        with open(outpath, 'w+') as outfile:
            outfile.write(self.log.getvalue())

        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A simple application to update TODO\'s from a path. '
                    'Requires the -p and -f flags.')

    parser.add_argument('-ee', '--exclude_extensions',
                        help='Any file extensions excluding the \'.\' to '
                             'exclude from the search, separated by commas..',
                        type=str)

    parser.add_argument('-ef', '--exclude_files',
                        help='Flag this option to exclude specific file names, '
                             'separated by by commas.', type=str)

    parser.add_argument('-ep', '--exclude_path',
                        help='You can flag this option to exclude specific '
                             'paths or folders. Include folder paths by '
                             'including strings like \"\'/path/to/fake/,/folder'
                             '/\'\". With this example, if the program comes '
                             'across the path \'/path/to/fake\' or '
                             '\'/folder\', it will just skip the search of the '
                             'path.', type=str)

    parser.add_argument('-f', '--filetypes',
                        help='The file extensions excluding the \'.\' to check '
                             'for, separated by commas.')

    parser.add_argument('-p', '--path',
                        help='The path to search for TODO lines.')

    parser.add_argument('-Q', '--quiet',
                        help='Do not output \'# TODO\' items as they are '
                             'found.', action='store_true')

    parser.add_argument('-v', '--version', help='Display version.',
                        action='store_true')

    parsed = parser.parse_args()  # Parse the above specified arguments.

    if parsed.version:
        print(versionstr)
        exit()

    if parsed.exclude_extensions is not None:
        exclude_extensions = list(parsed.exclude_extensions.split(','))
    else:
        exclude_extensions = []

    if parsed.exclude_files is not None:
        exclude_files = list(parsed.exclude_files.split(','))
    else:
        exclude_files = []

    if parsed.exclude_path is not None:
        exclude_path = list(parsed.exclude_path.split(','))
    else:
        exclude_path = []

    if parsed.filetypes is None:
        sys.stderr.write(
            'You must include file types to search! Use -h to view '
            'help.\n')
        raise RuntimeError('No filetypes specified.')
    else:
        filetypes = list(parsed.filetypes.split(','))

    if parsed.path is None:
        print(
            'Did not specify a path to iterate from, defaulting to the Current '
            'Working Directory')
        path = './'
    else:
        if os.access(parsed.path, os.F_OK):
            path = parsed.path
        else:
            raise RuntimeError('Could not access the path created.')

    Searcher(path, filetypes, exclude_extensions, exclude_files,
             exclude_path, parsed.quiet).write_file('to.do')
