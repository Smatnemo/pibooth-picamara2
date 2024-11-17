=================
pibooth-picamera2
=================

|PythonVersions| |Downloads|

``pibooth-picamera2`` is a plugin for the `pibooth`_ application.

It integrates the picamera2 library and uses the raspberry camera v3 module. Pibooth currently only supports only the raspberry pi camera v2, 
ghoto and any webcam but not the v3. This is a plugin to allow support for picamera2 library and the camera v3 module that will not disrupt 
any flow of the app or change the original code.

Hardware
--------
- 1 Camera (Raspberry pi camera v3)

Software
--------
- picamera2 

Install
-------
::

     $ apt install picamera2

::

     $ pip3 install pibooth-picamera2 

.. _`pibooth`: https://pypi.org/project/pibooth 

.. |PythonVersions| image:: https://img.shields.io/badge/python-3.9+-red.svg
   :target: https://www.python.org/downloads 
   :alt: Python 3.9+

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth?color=purple
   :target: https://pypi.org/project/pibooth-picamera2
   :alt: PyPi downloads

