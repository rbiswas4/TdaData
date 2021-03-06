from setuptools import setup
import sys
import os
import re

PACKAGENAME = 'tdd'
packageDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          PACKAGENAME)

# Obtain the package version
versionFile = os.path.join(packageDir, 'version.py')
with open(versionFile, 'r') as f:
          s = f.read()
# Look up the string value assigned to __version__ in version.py using regexp
versionRegExp = re.compile("__VERSION__ = \"(.*?)\"")
# Assign to __version__
__version__ =  versionRegExp.findall(s)[0]
print(__version__)

# create requirements file
## Don't have this yet
# setupDir = os.path.join(packageDir, '..', 'setup')
# genRequirements = os.path.join(setupDir, 'generate_requirements.py')
# print(genRequirements)


setup(# package information
      name=PACKAGENAME,
      version=__version__,
      description='repo for handling Time Domain Astronomy Data',
      long_description=''' ''',
      # What code to include as packages
      packages=[PACKAGENAME],
      packagedir={PACKAGENAME: 'tdd'},
      # What data to include as packages
      include_package_data=True,
      install_requires=['astropy', 'simsurvey'],
      package_data={PACKAGENAME:['example_data/*.csv',
                                 'example_data/*.pkl']},
      )
