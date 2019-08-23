from setuptools import setup, find_packages
import os
import sys

setup(name='smartscope',
      version='0.1',
      description='Tools for automated high throughput imaging',
      url='https://github.com/yellenlab/SmartScope',
      author='Caleb Sanford',
      author_email='calebsanfo@gmail.com',
      packages=find_packages(),
      zip_safe=False)

path = os.getcwd()
with open(os.path.join(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'), 'SmartScope_v2.bat'), 'w+') as file:
      file.write(sys.executable + ' ' + os.path.join(path, 'smartscope/gui/tabapp.py'))