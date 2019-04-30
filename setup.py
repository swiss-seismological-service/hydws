"""
setup.py for hydws
"""

import os
import sys
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 required.")


def get_version(filename):
    from re import findall
    with open(filename) as f:
        metadata = dict(findall("__([a-z]+)__ = '([^']+)'", f.read()))
    return metadata['version']


# ----------------------------------------------------------------------------
_name = 'hydws'
_description = 'REST webservice allowing access to hydraulic data.'
_authors = [
    'Daniel Armbruster',
    'Lukas Heiniger', ]
_authors_email = [
    'daniel.armbruster@sed.ethz.ch',
    'lukas.heiniger@sed.ethz.ch', ]

_install_requires = [
    'Flask>=1.0.2',
    'Flask-RESTful>=0.3.7',
    'Flask-SQLAlchemy>=2.3.2',
    'marshmallow>=3.0.0rc5',
    'webargs>=5.3.0', ]

_data_files = [
    ('', ['LICENSE'])]

_entry_points = {
    'console_scripts': [
        'hydws-test = hydws.server.app:main_test', ]}


# ----------------------------------------------------------------------------
setup(
    name=_name,
    version=get_version(os.path.join('hydws', '__init__.py')),
    author=' (ETHZ),'.join(_authors),
    author_email=', '.join(_authors_email),
    description=_description,
    license='GPLv3',
    keywords="seismology hydraulics service",
    url='https://gitlab.seismo.ethz.ch/armdanie/hydws',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        ('License :: OSI Approved :: GNU General Public License v3 or later '
         '(GPLv3+)'),
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering', ],
    platforms=['Linux', ],
    packages=find_packages(),
    data_files=_data_files,
    install_requires=_install_requires,
    entry_points=_entry_points,
    include_package_data=True,
    zip_safe=False,
)
