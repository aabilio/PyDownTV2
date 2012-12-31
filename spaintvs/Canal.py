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

# Clase abstracta con atributos y métodos comunes a todos los canales

import Descargar
import Utiles
import Error
from dammit import UnicodeDammit
try: from google.appengine.api import urlfetch
except: pass

_default_opcs = {
                "log": True,
                "debug": False
                }

class Canal(object):
    '''
        Clase abstracta con vars. y métodos comunes a todos los canales
    '''
    
    default_opcs = _default_opcs

    def __init__(self, url="", opcs=None, url_validas=None, nombre_canal=None):
        '''
            Recibe la url de la televisión y las opciones para el módulo
        '''
        self.__OPCS = opcs if opcs is not None else self.default_opcs
        self.__URL_VALIDAS = url_validas
        self.__NOMBRE_CANAL = nombre_canal
        self.__URL = url
        if not self.__isUrlValida(): raise Error.BadURL("%s no pertenece a %s" % (self.__URL, self.__NOMBRE_CANAL))
        
    def getURL(self):
        '''
            Obtener la URL de televisión española
        '''
        return self.__URL
    def setURL(self, url):
        '''
            return la URL válida de TVE que se le pasa a la clase
        '''
        self.__URL = url
        if not self.__isUrlValida(): raise Error.BadURL("%s no pertenece a %s" % (self.__URL, self.__NOMBRE_CANAL))
    url = property(getURL, setURL)
    
    def getOPCS(self):
        '''
            Obtener la URL de televisión española
        '''
        return self.__OPCS
    opcs = property(getOPCS)
    
    def __isUrlValida(self):
        '''
            Comprueba si la URL recibida pertenece al canal
        '''
        for i in self.__URL_VALIDAS:
            if self.__URL.find(i) != -1: return True
        return False
        
    
    def log(self, *msg):
        if self.__OPCS.has_key("log"):
            if self.__OPCS["log"]: Utiles.printt(*msg)
    info = log
    
    def debug(self, *msg):
        if self.__OPCS.has_key("debug"):
            if self.__OPCS["debug"]: Utiles.printt(u"[DEBUG]", *msg)
    
    def pprint(self, *msg):
        from pprint import pprint
        pprint(" ".join(msg))
    
    def pprintDict(self, dicts):
        from pprint import pprint
        pprint(dicts)
    
    def detectCharset(self,html):
        return UnicodeDammit(html).original_enconding
    
    def toUtf(self, html):
        return UnicodeDammit(html).unicode_markup
    
    def gethtml(self):
        return Descargar.get(self.url)
    
    def geturlfetch(self, url_=None):
        url = self.url if url_ is None else url_
        try:
            if urlfetch:
                result = urlfetch.fetch(url, headers=Descargar.std_headers, deadline=60)
                return result.content
            else:
                return None
        except: return Descargar.get(url)
        
        
    
    
        
        
        
        
        