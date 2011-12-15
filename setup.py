import sys, os
from setuptools import setup, find_packages
from setuptools.command.develop import develop as STDevelopCmd

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()
VERSION = open(os.path.join(cdir, 'mssqlddlwriter', 'version.txt')).read().strip()

class DevelopWithNoseCmd(STDevelopCmd):
    def run(self):
        # nose is required for testing
        self.distribution.install_requires.append('nose')
        # add in the nose plugin only when we are using the develop command
        self.distribution.entry_points['nose.plugins'] = ['mssqlddlwriter_config = mssqlddlwriter.nose_plugin:ConfigPlugin']
        STDevelopCmd.run(self)

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
        'SQLAlchemy',
        'BlazeUtils>=0.3.7',
    ],
    cmdclass = {
        'develop_with_nose': DevelopWithNoseCmd
    },
    # don't remove this, otherwise the customization above in DevelopCmd
    # will break.  You can safely add to it though, if needed.
    entry_points = {}
)
