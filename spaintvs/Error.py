#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of spaintvs.
#
#    spaintvs is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    spaintvs is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with spaintvs.  If not, see <http://www.gnu.org/licenses/>.

# Excepciones de pyspaintvs

__author__="aabilio"
__date__ ="$16-oct-2012 11:35:37$"

class GeneralPyspainTVsError(Exception):
    def __init__(self, msg=None):
        self.__msg = msg if msg is not None else "Error general al obtener el enlace de descarga"
    def __str__(self):
        return self.__msg
    
class BadURL(Exception): # Solo para uso internno de spaintvs
    def __init__(self, msg=None):
        self.__msg = msg if msg is not None else "La Url recibida no se corresponde con el canal"
        raise GeneralPyspainTVsError(self.__msg) # A nivel de usuario solo utilizar GeneralPyspainTVsError()
    def __str__(self):
        return self.__msg
