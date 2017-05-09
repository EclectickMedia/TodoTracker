import argparse
import os
import time
import io

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

version = 'V2.00.01'
versiondate = 'Tue May  9 03:01:10 2017'
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
        self.quiet = quiet
        self.log = io.StringIO()
        self.log.write('TODO MASTER (%s)'
                       '                  *Generated by github.com/'
                       'eclectickmedia/todotracker*\n--------\n' % time.ctime())

        self._search_path()
        if not self.quiet:
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
                    self._parse_file(path, file)

    def _parse_file(self, path, file):
        has_todo = False
        temp_log = io.StringIO()
        if os.access(os.path.join(path, file), os.F_OK):
            try:
                with open(os.path.join(path, file)) as infile:
                    for i, line in enumerate(infile):
                        if line.count('# TODO'):
                            temp_log.write('%s:%s' % (i, line))
                            has_todo = True
            except UnicodeDecodeError as e:
                pass

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

        return self.log


class main:
    def __init__(self, root):
        self.root = root
        self.path = None
        self.file_types = []
        self.exclude = {}

        path_and_types_frame = ttk.Frame()
        path_and_types_frame.pack()
        self.path_text = StringVar()
        self.path_text.set(os.getcwd())
        Button(path_and_types_frame, text='Select Search Path',
               command=lambda:
               self.path_text.set(filedialog.askdirectory())).grid(column=0,
                                                                   row=0)

        self.path_label = Label(path_and_types_frame,
                                textvariable=self.path_text)
        self.path_label.grid(column=1, row=0)
        Label(path_and_types_frame,
              text='File types, seperated by commas:').grid(row=1, column=0)
        self.types_entry = Entry(path_and_types_frame)
        self.types_entry.grid(row=1, column=1)

        exclude_frame = ttk.Frame()
        exclude_frame.pack()
        Label(exclude_frame, text='To exclude various files, file types, and '
                                  'paths, include each entry separated by '
                                  'commas.').grid(row=0, columnspan=2,
                                                  pady=(20, 10))

        Label(exclude_frame,
              text='Extensions to exclude, seperated by commas:').grid(row=1,
                                                                       column=0)
        self.extensions_input = Entry(exclude_frame)
        self.extensions_input.grid(row=1, column=1)

        Label(exclude_frame,
              text='File names to exclude, seperated by commas:').grid(row=2,
                                                                       column=0)
        self.files_input = Entry(exclude_frame)
        self.files_input.grid(row=2, column=1)

        Label(exclude_frame,
              text='Paths to exclude, seperated by commas:').grid(row=3,
                                                                  column=0)
        self.paths_input = Entry(exclude_frame)
        self.paths_input.grid(row=3, column=1)

        Button(root, text='Specify output folder and run search...',
               command=lambda:
               self._run_search(filedialog.askdirectory())).pack(pady=(20, 10))

    def _run_search(self, outpath):
        if self.types_entry.get() == '':
            raise RuntimeError('Must specify at least one file type')

        if self.extensions_input.get() == '':
            extensions = []
        else:
            extensions = list(self.extensions_input.get().split(','))

        if self.files_input == '':
            files = []
        else:
            files = list(self.files_input.get().split(','))

        if self.paths_input.get() == '':
            paths = []
        else:
            paths = list(self.paths_input.get().split(','))

        popup = Toplevel(root)

        Label(popup, text=Searcher(self.path_text.get(),
                                   list(self.types_entry.get().split(',')),
                                   extensions, files, paths,
                                   True).write_file(
            os.path.join(outpath, 'to.do')).getvalue(), justify=LEFT).pack()


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

    parser.add_argument('-c', '--cli', help='Use this flag to skip launching '
                                            'the applet. Use this flag in '
                                            'conjunction with other flags to '
                                            'enable CLI support.',
                        action='store_true')

    parsed = parser.parse_args()  # Parse the above specified arguments.

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

        if parsed.path is None:
            path = './'
        else:
            if os.access(parsed.path, os.F_OK):
                path = parsed.path
            else:
                raise RuntimeError('Could not access the path created.')

        Searcher(path, filetypes, exclude_extensions, exclude_files,
                 exclude_path, parsed.quiet)
    else:
        root = Tk()
        main(root)
        root.mainloop()
