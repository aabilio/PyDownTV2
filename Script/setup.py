#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of PyDownTV2.
#
#    PyDownTV2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyDownTV2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyDownTV2.  If not, see <http://www.gnu.org/licenses/>.

# Archivo setup.py del proyecto PyDownTV2:

from ez_setup import use_setuptools
use_setuptools()

#from distutils.core import setup
from setuptools import setup


setup(name="PydownTV", 
    version="0.1.0",
    description="Descarga vídeos de las webs de TVs Españolas",
    author="Abilio Almeida Eiroa",
    author_email="aabilio@gmail.com",
    url="https://github.com/aabilio/PyDownTV2",
    license="GPL3",
    scripts=["pydowntv.py"], 
    packages = ["spaintvs",
                "pyaxel",
                "pylibmms", 
                "pyamf",
                "pyamf.adapters",
                "pyamf.flex",
                "pyamf.remoting",
                "pyamf.util"], 
    py_modules=["ez_setup", "uiDescargar", "uiUtiles"]
)
    
    
