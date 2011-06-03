import sys, os
from setuptools import setup, find_packages

from mssqlddlwriter import VERSION

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

setup(
    name='MSSQLDDLWriter',
    version=VERSION,
    description="writes MSSQL DDL to files",
    long_description=README + '\n\n' + CHANGELOG,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
    ],
    author='Randy Syring',
    author_email='rsyring@gmail.com',
    url='',
    license='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'SQLAlchemy'
    ],
)
