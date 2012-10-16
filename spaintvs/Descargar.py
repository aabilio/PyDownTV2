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

# Módulo para realizar las peticiones a las televisiones de la librería

__author__="aabilio"
__date__ ="$09-oct-2012 20:57:46$"

#import sys
import urllib
import urllib2
import httplib
#import time
import codecs
#import os

std_headers =  {
               'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
               'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
               'Accept': 'text/xml,application/xml,application/xhtml+xml,'
               'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
               'Accept-Language': 'en-us,en;q=0.5',
               }

class ErrorDescarga(Exception):
    '''
        Manejar errores futuros del módulo Descargar
    '''
    def __init__(self, text, msg = None, line = None):
        self.__text = text
        self.__msg = msg if msg is not None else None
        self.__line = str(line) if line is not None else "Unknow line"
    def __str__(self):
        return self.__msg if self.__msg is not None else "Error general en el módulo de descarga"
    

def getHtmlHeaders(url, header=std_headers):
    '''
        Recibe:
            - url (http://ejemplo.com/ruta/de/ejemplo)
            - header (opcional), de la siguiente forma:
            {
               'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
               'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
               'Accept': 'text/xml,application/xml,application/xhtml+xml,'
               'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
               'Accept-Language': 'en-us,en;q=0.5',
            } <-- Esto se enviará en caso de omitir el header.
        Return:
            - stream html
    '''
    try:
        request = urllib2.Request(url, None, header)
        f = urllib2.urlopen(request)
        stream = f.read()
        f.close()
        return stream
    except Exception, e:
        raise ErrorDescarga(e)
        #TODO: error

def getHtmlUtf8(url): # Sobre todo para descargar VERSION
    '''
        Recibe:
            - url (http://ejemplo.com/ruta/de/ejemplo)
        Return:
            - stream html codificado en utf-8
    '''
    try:
        f = urllib2.urlopen(url)
        Reader = codecs.getreader("utf-8")
        fh = Reader(f)
        stream = fh.read()
        return stream
    except Exception, e:
        raise ErrorDescarga(e)
        #TODO: Error
    
def getHtml_(url):
    '''
        Recibe:
            - url (http://ejemplo.com/ruta/de/ejemplo)
        Return:
            - stream html
    '''
    try:
        f = urllib2.urlopen(url)
        stream = f.read()
        f.close()
        return stream
    except Exception, e:
        raise ErrorDescarga(e)
        #TODO:
        # - Imprimir error
        # - Salir??
    else:
        pass

def getHtml(url, withHeader=False, utf8=False, header=std_headers):
    '''
        Recibe:
            - url (http://ejemplo.com/ruta/de/ejemplo)
            - withHeader (True or False)
            - utf8 (True or False)
            - header, de la forma:
            {
               'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
               'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
               'Accept': 'text/xml,application/xml,application/xhtml+xml,'
               'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
               'Accept-Language': 'en-us,en;q=0.5',
            } <-- Esto se enviará en caso de omitir el header.
        Return:
            - stream html de una web
    '''
    if url.find("http://") == -1: url = "http://" + url
    if withHeader: return getHtmlHeaders(url, header)
    elif utf8: return getHtmlUtf8(url)
    else: return getHtml_(url)

def isReachable(url): # Retro compatibilidad con módulo de TVE
    '''
        Recibe: 
            - url (http://ejemplo.com/ruta/de/ejemplo)
        Comprueba si se puede acceder a una web (True or False)
    '''
    try:
        f = urllib2.urlopen(url)
        f.read()
        f.close()
        return True
    except Exception:
        return False
    

def doPOST(url, path, post_args, doseq=True, headers=None):
    Post = urllib.urlencode(post_args, doseq=True)
    headers = {
                "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)", 
                "Host": "servicios.mitele.es", 
                #"Accept-Encoding": "gzip", 
                "Accept-Charset": "ISO-8859-1,UTF-8;q=0.7,*;q=0.7", 
                "Referer": "http://static1.tele-cinco.net/comun/swf/playerMitele.swf",
                "Connection": "close", 
                "Accept-Language": "de,en;q=0.7,en-us;q=0.3", 
                "Content-type": "application/x-www-form-urlencoded"
                } if headers is None else headers
    conn = httplib.HTTPConnection(url, 80)
    conn.request("POST", path, Post, headers) 
    #conn.set_tunnel("80.58.250.68", 80, headers) # Opcional por si hace falta proxy español
    response = conn.getresponse()
    
    #print response.status, response.reason
    if response.status == 404: #NOT FOUND
        data = None
    elif response.status == 400: #BAD REQUEST
        data = None
    else:
        data = response.read()
    conn.close()
    
    return data
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    