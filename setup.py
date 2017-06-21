"""
First tries to load py2exe and configure for windows installation. Upon failure,
defaults to py2app (MacOSx)

py2app usage:
    python setup.py py2app
py2exe usage:
    python setup.py install
"""

try:

    from distutils.core import setup
    import py2exe  # used by py2app
    import sys
    import TodoTracker

    sys.argv.append('py2exe')

    setup(
        name='TodoTracker',
        version=TodoTracker.version,
        author='Ariana Giroux',
        author_email='ariana.giroux@gmail.com',
        url='https://github.com/EclectickMedia/TodoTracker',
        description='A simple todo tracking software.',
        long_description='A todo tracking software that searches regular text '
                         'files (like .py or .sh) files for the text `# TODO`, '
                         'and outputs the contents of any line found to a '
                         'single file.',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.5'
        ],
        # PY2EXE SETTINGS
        options={'py2exe': {'bundle_files': 1, 'compressed': True}},
        windows=[{'script': "TodoTracker.py"}],
        zipfile=None,
    )

except ImportError:
    from setuptools import setup
    import TodoTracker

    APP = ['TodoTracker.py']
    DATA_FILES = ['logs']
    OPTIONS = {}

    setup(
        name='TodoTracker',
        version=TodoTracker.version,
        author='Ariana Giroux',
        author_email='ariana.giroux@gmail.com',
        url='https://github.com/EclectickMedia/TodoTracker',
        description='A simple todo tracking software.',
        long_description='A todo tracking software that searches regular text '
                         'files (like .py or .sh) files for the text `# TODO`, '
                         'and outputs the contents of any line found to a '
                         'single file.',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.5'
        ],
        # PY2APP SETTINGS
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
