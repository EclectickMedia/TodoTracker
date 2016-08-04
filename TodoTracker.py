# This software is provided under the MIT Open Source Software License:
#
# Copyright (c) 2016, Ariana Giroux (Eclectick Media Solutions)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import argparse
import sys
import time

# TODO Include a readme for the application.

""" Preamble
This software is intended to be a low overhead, simple, and pythonic method of grepping for `# TOODO' tags out of a
softare. Intended for Python, this software will also be able to search any file that has non-binary encoding.

This software requires a path to start the search in, and a series of file extensions (without the preceeding `.')
delimited by commas. When given these paramaters, the software will walk (see os.walk()) through the directories
presented by the search and finds `# TODO' tags in your software, then outputs them to the screen in a standardized,
organized way, while discretely creating a `to.do' file as the results are found.

This software rose due to a need for a simple software that can quickly, and cost effectively search for `# TODO' tags
in private projects (for mor information, see github.com/eclectickmedia) and amass them to a single location, in as
easily digestible way as possible whilst still being accessible via a command line.
"""

""" Techincal Preamble
Due to repeatedly opening and closing any file containing the file extensions provided being system intensive, using
large directories can take some time to accomplish, i.e searching `/' on a *NIX operating system,
"""

version = 'V1.0'
versiondate = 'Thu Jul 28 13:31:11 2016'
buildname = 'TodoTracker'
versionstr = '%s %s (c) Eclectick Media Solutions, circa %s' % (buildname, version, versiondate)

""" Set up argument parsing. """
parser = argparse.ArgumentParser(description='A simple application to update TODO\'s from a path. Requires the -p and \
                                 -f flags.')

parser.add_argument('-ee', '--exclude_extensions', help='Any file extensions excluding the \'.\' to exclude from the \
                    search, separated by commas..', type=str)

parser.add_argument('-ef', '--exclude_files', help='Flag this option to exclude specific filenames, seperated by \
                    by commas.', type=str)

parser.add_argument('-ep', '--exclude_path', help='You can flag this option to exclude specific paths or folders. \
                    Include folder paths by including strings like \"\'/path/to/fake/,/folder/\'\". With this \
                    example, if the program comes across the path \'/path/to/fake\' or \'/folder\', it will just skip \
                    the search of the path.', type=str)

parser.add_argument('-f', '--filetypes', help='The file extensions excluding the \'.\' to check for, seperated by \
                    commas.')

parser.add_argument('-p', '--path', help='The path to search for TODO lines.')

parser.add_argument('-Q', '--quiet', help='Do not output \'# TODO\' items as they are found.', action='store_true')

parser.add_argument('-v', '--version', help='Display version.', action='store_true')

parsed = parser.parse_args()  # Parse the above specified arguments.

# Argument parsing
if parsed.version:
    print(versionstr)
    exit()

if parsed.exclude_extensions is not None:
    exclude_extensions = parsed.exclude_extensions.split(',')
else:
    exclude_extensions = ''

if parsed.exclude_files is not None:
    exclude_files = parsed.exclude_files.split(',')
else:
    exclude_files = ''

if parsed.exclude_path is not None:
    exclude_path = parsed.exclude_path.split(',')
else:
    exclude_path = ''

if parsed.filetypes is None:
    sys.stderr.write('You must include filetypes to search! Use -h to view help.\n')
    exit()

if parsed.path is None:
    sys.stderr.write('You must include a path to search! Use -h to view help.\n')
    exit()

# Main Loop
with open('to.do', 'w+') as tf:
    tf.write('TODOMASTER (%s)'
             '                  *Generated by github.com/eclectickmedia/todotracker*\n--------\n' % time.ctime())
    if not parsed.quiet:
        print('TODOMASTER\n--------\n')

    for path, dirs, files in os.walk(parsed.path):  # Pylint autolints this as to complex, but this is a standard action

        if exclude_path.count(path) > 0:
            print("Skipped %s" % exclude_path[exclude_path.index(path)])
        else:

            for file in files:
                if exclude_files.count(file) > 0:
                    print('Skipped %s' % file)

                elif exclude_extensions.count(file) > 0:
                    print('Skipped %s' % file)

                elif parsed.filetypes.split(',').count(file.split('.')[-1]) > 0 and not file.count('to.do') > 0:
                    print_file = False
                    output_queue = []

                    with open(os.path.join(path, file)) as f:

                        for i, line in enumerate(f):
                            if line.count('# TODO') > 0:
                                print_file = True
                                output_queue.append('%s:%s' % (i, line))

                    if print_file:
                        output_queue.insert(0, '\n\n%s\n--------\n' % file)
                        if not parsed.quiet:
                            print('\n\n%s\n--------' % file)

                        while len(output_queue) > 0:
                            line = output_queue.pop(0)
                            tf.write(line)
                            if not parsed.quiet:
                                print(line.split('\n')[0])
