#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys 
from io import open 
import os.path as osp
from setuptools import setup, find_packages

HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE) # nopep8 : import shall be done after adding setup to paths

import pibooth_picamera2 as plugin 

with open(osp.join(HERE, 'docs', 'requirements.txt')) as fd:
    docs_require = fd.read().splitlines()

def main():
    setup(
        name=plugin.__name__,
        version=plugin.__version__,
        description=plugin.__doc__,
        long_description=open(osp.join(HERE, 'README.rst'), encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.9',
            'Natural Language :: English',
            'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        ],
        author="Tertese Moses",
        url="https://github.com/Smatnemo/pibooth-picamera2",
        download_url="https://github.com/Smatnemo/pibooth-picamera2/archive/{}.tar.gz".format(plugin.__version__),
        license="GPLv3",
        platforms=['unix','linux'],
        keywords=[
            'Raspberry Pi',
            'camera',
            'photobooth',
            'picamera2'
        ],
        py_modules=['pibooth_picamera2'],
        python_requires=">=3.9",
        install_requires=[
            'pibooth>=2.0.0',
            'picamera2>=0.3.18'
        ],
        zip_safe=False, # Don't install the lib as an .egg zipfile
        entry_points={'pibooth': ['pibooth_picamera2 = pibooth_picamera2']}
    )

if __name__ == "__main__":
    main()
