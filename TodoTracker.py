#! /usr/bin/python3

import argparse
import os
import time
import io
from log import logger, searcher_handler, tests_handler
import re
import unittest
import sys

from tkinter import StringVar, Entry, Toplevel, LEFT, Tk
from tkinter import ttk
from tkinter import filedialog

version = 'V2.01.02.01'
versiondate = 'Mon Mar  5 12:12:39 2018'
buildname = 'TodoTracker'
versionstr = '%s %s (c) Eclectick Media Solutions, circa %s' % (buildname,
                                                                version,
                                                                versiondate)


################################################################################
#                                LOGIC FUNCS                                   #
#                                                                              #
#                 Implement file heirarchy searching logic.                    #
class Searcher:
    """ Implements file and line searching functionality.

        >>> from TodoTracker import Searcher
        >>> from os import path as paths, getcwd
        >>> searcher = Searcher(getcwd(), ['py'])  # set quiet=False for verbose
        >>> searcher.search_path()  # if verbose, output results
        >>> searcher_log = searcher.write_file(os.path.join(getcwd(), 'to.do'))
        >>> searcher_log.getvalue()  # outputs contents
    """
    def __init__(self, path, types, extensions=list(), files=list(),
                 epaths=list(), regex=r'(?!).*# TODO.*', quiet=False):
        """ Initializes all data, writes initial line of output file.

        `path` - The path to search from.
        `types` - A list of file extensions that are valid search targets.
        `extensions` - An optional list of file extensions to ignore.
        `files` - An optional list of file names to ignore.
        `epaths` An optional list of paths to ignore.
        `regex` - User supplied regex pattern to match against. (Passed to `re`)

        `initializes`:
            `self.exclude` - A `dict` with keys:
                'extensions' - The list supplied by `extensions`
                'files' - The list supplied by `files`
                'paths' - The list supplied by `epaths`
            `self.regex` - The result of `re.compile(regex)`
            `self.log` - An `io.StringIO` object used to store results.
        """
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
        self.regex = re.compile(regex)
        self.quiet = quiet
        self.log = io.StringIO()
        self.log.write('TODO MASTER (%s)'
                       '                  *Generated by github.com/'
                       'eclectickmedia/todotracker*\n--------\n' % time.ctime())

        # We have to use regex from the arguments to log the value of the regex
        logger.debug('%s %s %s %s %s %s' % (version, self.path, self.types,
                                            self.exclude, repr(regex),
                                            self.quiet))

    def _validate_file(self, file):
        """ Compares file against `self.exclude`, and returns False if any match
        is made. Returns True if `file` is found in `self.types`.
        """
        for efile in self.exclude['files']:
            if file.count(efile):
                logger.debug('%s in %s, False' % (efile, file))
                return False

        for ext in self.exclude['extensions']:
            if file.count(ext):
                logger.debug('%s in %s, False' % (ext, file))
                return False

        for t in self.types:
            if file.count(t):
                logger.debug('%s in %s, true' % (t, file))
                return True

        else:  # no file type returned true
            return False

    def __remove_dir(self, dirs):
        """ Remove directories from a list of directories if they match against
        `self.exclude['paths']`. Returns modified list of directories.
        """
        dirs_ = dirs[:]
        for d in dirs_:
            if self.exclude['paths'].count(d):
                dirs.remove(d)
                logger.debug('remove directory %s from %s' % (d, dirs_))

        logger.debug('final: %s', dirs)
        return dirs

    def search_path(self):
        """ Searches for matching files from `self.path` and appends matching lines
        to `self.log`.

        If not `self.quiet`, outputs `self.log` on completion.
        """
        logger.debug('start search %s' % self.path)
        for path, dirs, files in os.walk(self.path, topdown=True):
            self.__remove_dir(dirs)
            logger.debug('parse files in %s' % path)
            for file in files:
                logger.debug('validate and parse %s' %
                             os.path.join(path, file))
                if not self._validate_file(file):
                    pass
                else:
                    self._parse_file(path, file)

        if not self.quiet:
            print(self.log.getvalue())

    def _parse_file(self, path, file):
        """ Parse file located at `path` of `file`, appending matching lines to
        `self.log`. Returns True if file had any matching lines.
        """
        has_pattern = False
        temp_log = io.StringIO()
        if os.access(os.path.join(path, file), os.F_OK):
            try:
                with open(os.path.join(path, file)) as infile:
                    for i, line in enumerate(infile):
                        if self.regex.search(line):
                            temp_log.write('%s:%s' % (i, line))
                            logger.debug('%s:%s' % (i, line.strip('\n')))
                            has_pattern = True
            except UnicodeDecodeError:
                logger.debug('%s throws UnicodeDecodeError'
                             % os.path.join(path, file))

            if has_pattern:
                # Write file header
                self.log.write('\n\n%s\n\n--------\n\n' % os.path.join(path,
                                                                       file))
                logger.debug('wrote file header')
                self.log.write(temp_log.getvalue())
                logger.debug('wrote temp_log to self.log')
            else:
                logger.debug('no pattern in %s' % os.path.join(path, file))

            return has_pattern

        else:
            logger.debug('Could not open %s' % os.path.join(path, file))
            raise RuntimeError('Could not open %s!' % os.path.join(path, file))

    def write_file(self, outpath):
        """ Writes `self.log` to `outpath`, if `outpath` is valid path.

        `returns` - self.log
        """
        with open(outpath, 'w+') as outfile:
            outfile.write(self.log.getvalue())

        return self.log


# UI
class main(ttk.Frame):
    def __init__(self, root):
        super(main, self).__init__(root)
        self.root = root
        self.path = None
        self.file_types = []
        self.exclude = {}

        # PATH AND TYPES
        path_and_types_frame = ttk.Frame(self)
        path_and_types_frame.pack()
        self.path_text = StringVar()
        self.path_text.set(os.getcwd())
        ttk.Button(path_and_types_frame, text='Select Search Path',
                   command=lambda:
                   self.path_text.set(filedialog.askdirectory())).grid(column=0,
                                                                       row=0)

        self.path_label = ttk.Label(path_and_types_frame,
                                    textvariable=self.path_text)
        self.path_label.grid(column=1, row=0)
        ttk.Label(path_and_types_frame,
                  text='File types, seperated by commas:').grid(row=1, column=0)
        self.types_entry = Entry(path_and_types_frame)
        self.types_entry.grid(row=1, column=1)

        # EXCLUDE
        exclude_frame = ttk.Frame(self)
        exclude_frame.pack()
        ttk.Label(exclude_frame, text='To exclude various files, file types, '
                  'and paths, include each entry separated by commas.'
                  ).grid(row=0, columnspan=2, pady=(20, 10))

        ttk.Label(exclude_frame,
                  text='Extensions to exclude, seperated by commas:'
                  ).grid(row=1, column=0)
        self.extensions_input = Entry(exclude_frame)
        self.extensions_input.grid(row=1, column=1)

        ttk.Label(exclude_frame,
                  text='File names to exclude, seperated by commas:'
                  ).grid(row=2, column=0)
        self.files_input = Entry(exclude_frame)
        self.files_input.grid(row=2, column=1)

        ttk.Label(exclude_frame,
                  text='Paths to exclude, seperated by commas:').grid(row=3,
                                                                      column=0)
        self.paths_input = Entry(exclude_frame)
        self.paths_input.grid(row=3, column=1)

        regex_frame = ttk.Frame(self)
        regex_frame.pack(pady=(20, 10))
        ttk.Label(regex_frame,
                  text='Specify Regex pattern').grid(row=0, column=0)
        ttk.Label(regex_frame,
                  text='(all \'\\\' characters must be '
                  'escaped by an extra \'\\\'):').grid(row=1, column=0)
        self.regex_input = Entry(regex_frame)
        self.regex_input.grid(row=0, rowspan=2, column=1)

        ttk.Button(self, text='Specify output folder and run search...',
                   command=lambda:
                   self._run_search(filedialog.askdirectory())
                   ).pack(pady=(20, 10))
        self.pack()

    def _run_search(self, outpath):
        if self.types_entry.get() == '':
            raise RuntimeError('Must specify at least one file type')

        if self.extensions_input.get() == '':
            extensions = []
        else:
            extensions = list(self.extensions_input.get().split(','))

        if self.files_input.get() == '':
            files = []
        else:
            files = list(self.files_input.get().split(','))

        if self.paths_input.get() == '':
            paths = []
        else:
            paths = list(self.paths_input.get().split(','))

        if self.regex_input.get() == '':
            regex = "(?i).*#.TODO.*"
        else:
            regex = self.regex_input.get()

        popup = Toplevel(root)

        searcher = Searcher(self.path_text.get(), list(
            self.types_entry.get().split(',')), extensions, files, paths, regex,
            True)
        searcher.search_path()
        searcher_log = searcher.write_file(os.path.join(outpath, 'to.do'))

        ttk.Label(popup, text=searcher_log.getvalue(), justify=LEFT).pack()


################################################################################
#                                   TESTS                                      #
#                                                                              #
#                       Add tests and helper function.                         #
def logMe(func):
    """ Enables tests logging for one function. Intended for use with
    unittest.TestCase test_ cases. """
    def wrapper(self):
        logger.disabled = False
        logger.removeHandler(searcher_handler)
        logger.addHandler(tests_handler)
        logger.info('%s' % func.__name__)
        func(self)
        logger.removeHandler(tests_handler)
        logger.addHandler(searcher_handler)
    return wrapper


class SearcherTest(unittest.TestCase):
    """ Tests functionality of Searcher class.

    Uses the data file 'tests/sample_data.test'.
    Creates the data file 'tests/out.do' (for `test_write_file`, cleans after
    use).
    """
    # TODO test `search_path` skips directories properly
    def setUp(self):
        logger.disabled = True

    def tearDown(self):
        logger.disabled = False

    def test_init(self):
        searcher = Searcher('logs', ['test'], ['test1', 'test2'],
                            files=['test'], epaths=['test1', 'test2', 'test3'],
                            regex='test', quiet=True)

        # Path validation
        self.assertEqual('logs', searcher.path)
        self.assertEqual(4, len(searcher.path))
        self.assertEqual(str, type(searcher.path))

        # Types validation
        self.assertEqual(['test'], searcher.types)
        self.assertEqual(1, len(searcher.types))
        self.assertEqual(list, type(searcher.types))

        # Exclude Extensions validation
        self.assertEqual(['test1', 'test2'], searcher.exclude['extensions'])
        self.assertEqual(2, len(searcher.exclude['extensions']))
        self.assertEqual(list, type(searcher.exclude['extensions']))

        # Exclude Files validation
        self.assertEqual(['test'], searcher.exclude['files'])
        self.assertEqual(1, len(searcher.exclude['files']))
        self.assertEqual(list, type(searcher.exclude['files']))

        # Exclude Paths validation
        self.assertEqual(['test1', 'test2', 'test3'],
                         searcher.exclude['paths'])
        self.assertEqual(3, len(searcher.exclude['paths']))
        self.assertEqual(list, type(searcher.exclude['files']))

        # Exclude validation
        self.assertEqual(3, len(searcher.exclude))
        self.assertEqual(dict, type(searcher.exclude))
        categories = ['extensions', 'files', 'paths']
        for key in searcher.exclude:  # check for keys that aren't correct
            if not categories.count(key):
                self.fail('Not all keys were present in searcher.exclude!')

        # Regex validation
        self.assertEqual(re.compile('test'), searcher.regex)
        self.assertEqual('test', searcher.regex.pattern)

        # Log validation
        self.assertEqual(type(io.StringIO()), type(searcher.log))
        self.assertTrue(searcher.log.getvalue().count('TODO MASTER'))

    def test__validate_file_succeeds(self):
        searcher = Searcher('tests', ['test'])
        self.assertTrue(searcher._validate_file(
            os.path.join('tests', 'sample_data.test')))

    def test__validate_file_fails_on_excluded_file(self):
        searcher = Searcher('tests', ['html'], files=['test'])
        self.assertFalse(searcher._validate_file(
            os.path.join('tests', 'sample_data.test')))

    def test__validate_file_fails_on_excluded_extension(self):
        searcher = Searcher('tests', ['html'], extensions=['test'])
        self.assertFalse(searcher._validate_file(
            os.path.join('tests', 'sample_data.test')))

    def test__validate_file_fails_on_no_file_matches(self):
        searcher = Searcher('tests', ['wont match'])
        self.assertFalse(searcher._validate_file(
            os.path.join('tests', 'sample_data.test')))

    def test__parse_file_finds_tag(self):
        searcher = Searcher('tests', ['test'], regex='^ *#.*TODO.*$')
        self.assertTrue(searcher._parse_file('tests', 'sample_data.test'))
        self.assertTrue(searcher.log.getvalue().count('0:# TODO'))
        self.assertTrue(searcher.log.getvalue().count('sample_data.test') == 1)

    def test__parse_file_with_complex_regex_finds_tag(self):
        searcher = Searcher('tests', ['test'],
                            regex='^ *#.*TODO.*$|^ *//.*TODO.*$')
        self.assertTrue(searcher._parse_file('tests', 'sample_data.test'))
        self.assertTrue(searcher.log.getvalue().count('1:// TODO'))
        self.assertTrue(searcher.log.getvalue().count('sample_data.test') == 1)

    def test__parse_file_doesnt_find_tag(self):
        searcher = Searcher('tests', ['test'],
                            regex='^$')
        self.assertFalse(searcher._parse_file('tests', 'sample_data.test'))
        self.assertFalse(searcher.log.getvalue().count('0:# TODO'))
        self.assertFalse(searcher.log.getvalue().count('1:// TODO'))
        self.assertTrue(searcher.log.getvalue().count('sample_data.test') < 1)

    def test__parse_file_raises_runtime_error(self):
        searcher = Searcher('tests', ['test'],
                            regex='^$')
        with self.assertRaises(RuntimeError):
            searcher._parse_file('a', 'b')

    @logMe
    def test_search_path_collects_data_when_present(self):
        searcher = Searcher('tests', ['test'], quiet=True,
                            regex="^# TODO.*$|^// TODO.*$")
        searcher.search_path()
        self.assertTrue(searcher.log.getvalue().count("0:# TODO"))
        self.assertTrue(searcher.log.getvalue().count("1:// TODO"))
        self.assertTrue(searcher.log.getvalue().count("sample_data.test") == 1)

    @logMe
    def test_search_path_no_data_present(self):
        searcher = Searcher('tests', ['test'], quiet=True,
                            regex="^$")
        searcher.search_path()
        self.assertFalse(searcher.log.getvalue().count("0:# TODO"))
        self.assertFalse(searcher.log.getvalue().count("1:// TODO"))
        self.assertFalse(searcher.log.getvalue().count("sample_data.test") == 1)

    @logMe
    def test_write_file(self):
        searcher = Searcher('tests', ['test'],
                            regex="^.*#.*TODO.*$|^.*//.*TODO.*$", quiet=True)
        searcher.search_path()
        searcher_log = searcher.write_file('tests/out.do')
        self.assertEqual(searcher.log.getvalue(), searcher_log.getvalue())

        with open('tests/out.do') as out_file:
            self.assertEqual(out_file.read(), searcher_log.getvalue())

        os.remove('tests/out.do')  # clean up tests directory, avoid
        # contamination


if __name__ == '__main__':
    ############################################################################
    #                            ARGPARSE CONFIG                               #
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

    parser.add_argument('-oP', '--output_path',
                        help='The path to which the software should output a '
                        'to.do master file.', default='./', type=str)

    parser.add_argument('-p', '--path',
                        help='The path to search for TODO lines.')

    parser.add_argument('-Q', '--quiet',
                        help='Do not output \'# TODO\' items as they are '
                             'found.', action='store_true')

    parser.add_argument('-v', '--version', help='Display version.',
                        action='store_true')

    parser.add_argument('-r', '--regex', help='The  Unix standard Regular '
                        'Expression to search with. Defaults to '
                        '\"r\'(?i).*# TODO.*\'\". Due to the way Python '
                        'handles Regex, you must escape all \'\\\' characters '
                        'with an extra \'\\\'; such that including the literal '
                        'representation of a Regex reserved character (i.e '
                        '\'.\') would require an extra \'\\\' (i.e \'\\\\.\')',
                        default=r'(?i).*# TODO.*', type=str)

    parser.add_argument('-c', '--cli', help='Use this flag to skip launching '
                                            'the applet. Use this flag in '
                                            'conjunction with other flags to '
                                            'enable CLI support.',
                        action='store_true')

    parsed = parser.parse_args()  # Parse the above specified arguments.

    ############################################################################
    #                            ARGV VALIDATION                               #
    if parsed.version:
        print(versionstr)
        exit()

    if parsed.cli:
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

        if parsed.output_path is './':
            output_path = os.path.expanduser('.')
        else:
            output_path = parsed.output_path

        if parsed.path is None:
            path = os.path.expanduser('.')
        else:
            if os.access(parsed.path, os.F_OK):
                path = parsed.path
            else:
                raise RuntimeError('Could not access the path created.')

        searcher = Searcher(path, filetypes, exclude_extensions, exclude_files,
                            exclude_path, parsed.regex, parsed.quiet)
        searcher.search_path()
        searcher_log = searcher.write_file(os.path.join(output_path, 'to.do'))

    ############################################################################
    #                                   UI                                     #
    else:
        root = Tk()
        main(root)
        root.mainloop()
