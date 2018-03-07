#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, "pipenv", "__version__.py")) as f:
    exec(f.read(), about)

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

required = [
    'virtualenv',
    'pew>=0.1.26'
]

if sys.version_info < (2, 7):
    required.append('requests[security]')
    required.append('ordereddict')

# https://pypi.python.org/pypi/stdeb/0.8.5#quickstart-2-just-tell-me-the-fastest-way-to-make-a-deb

class DebCommand(Command):
    """Support for setup.py deb"""

    description = 'Build and publish the .deb package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'deb_dist'))

            # Remove concurrent27, at it causes issues with compilation.
            rmtree(os.path.join(here, 'pipenv', 'vendor', 'concurrent27'))
        except FileNotFoundError:
            pass
        self.status(u'Creating debian mainfest…')
        os.system('python setup.py --command-packages=stdeb.command sdist_dsc -z artful --package pipenv --depends python3-pew')

        self.status(u'Building .deb…')
        os.chdir('deb_dist/pipenv-{0}'.format(about['__version__']))
        os.system('dpkg-buildpackage -rfakeroot -uc -us')


class UploadCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except FileNotFoundError:
            pass

        self.status('Building Source distribution…')
        os.system('{0} setup.py sdist'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name='pipenv',
    version=about['__version__'],
    description='Python Development Workflow for Humans.',
    long_description=long_description,
    author='Kenneth Reitz',
    author_email='me@kennethreitz.org',
    url='https://github.com/pypa/pipenv',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': ['pipenv=pipenv:cli'],
    },
    install_requires=required,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    cmdclass={
        'upload': UploadCommand,
        'deb': DebCommand
    },
)
