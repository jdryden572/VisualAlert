"""
setup.py

Brett Nelson and James Dryden
OSIsoft, LLC

July 2014

Setup script using py2exe to compile HueVisualAlert.py into a Windows 
Executable file. Requires py2exe ( http://py2exe.org ).

To run: enter "python setup.py py2exe" in command prompt in containing 
directory. Will output executable file and required libraries in directory
called "dist".

"""

from distutils.core import setup
import warnings
try:
	import py2exe
except:
	warnings.warn('py2exe must be installed. Try "pip install py2exe"')

setup(	console=['HueVisualAlert.py'], 
		data_files=[('.', ['config.json',])],
		options={
				"py2exe":{
						"bundle_files": 1
						}
				}
		)