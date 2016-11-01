"""
Setup script for generating executable/app from pigeon

Usage:
    python setup.py py2app/py2exe
"""
import sys

if sys.platform == "darwin":
    # python setup.py py2app
    
    from setuptools import setup

    APP = ['pigeon.py']
    DATA_FILES = []
    OPTIONS = {'argv_emulation': False,
     'iconfile': 'pigeon.icns'}

    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
elif sys.platform == "win32":
    # python setup.py py2exe

    from distutils.core import setup
    import py2exe

    setup(
    	options = {'py2exe': {'compressed': True}},
       windows = [{'script': "pigeon.py"}],
       zipfile = None,
       )

