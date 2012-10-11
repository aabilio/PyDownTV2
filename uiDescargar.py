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

# Módulo de ayuda al script principal para desscargar los vídeos

__author__="aabilio"
__date__ ="$10-oct-2012 20:57:46$"

import urllib
import subprocess
import sys

from pyaxel import pyaxel
from spaintvs.Utiles import salir, printt


class Descargar(object):
    ''' Clase que se encarga de descargar con urllib2 '''
    
    std_headers =   {
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
                        'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Accept': 'text/xml,application/xml,application/xhtml+xml,'
                        'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
                    'Accept-Language': 'en-us,en;q=0.5',
                    }

    def __init__(self, url=None, titulo=None, tipo=None, rtmpd_cmd=None, menco_cmd=None):
        self.__URL = url if url is not None else None
        self.__TITULO = titulo if titulo is not None else None
        self.__TIPO = self.__URL.split("://")[0] if tipo is None else tipo
        self.__COMANDO_RTMPD = rtmpd_cmd if rtmpd_cmd is not None else None
        self.__COMANDO_MENCO = menco_cmd if menco_cmd is not None else None
    
    def getURL(self):
        return self.__URL
    def setURL(self, url):
        self.__URL = url
    url = property(getURL, setURL)
    def getTITULO(self):
        return self.__TITULO
    def setTITULO(self, titulo):
        self.__TITULO = titulo
    titulo = property(getTITULO, setTITULO)
    
    def __getHTTP(self):
        if sys.platform == "win32": self.__descargaVideoWindows()
        else:
            printt(u"")
            printt(u"DESCARGAR:")
            printt(u"----------------------------------------------------------------")
            printt(u"[ URL DE DESCARGA FINAL ]", self.__URL)
            printt(u"[INFO] Presiona \"Ctrl + C\" para cancelar")
            printt(u"")
            options = {"output_file": self.__TITULO, "verbose": True, "max_speed": None, "num_connections": 4}
            pyaxel.download(self.__URL, options)
    
    def __getRTMP(self):
        command = "rtmpdump"
        if sys.platform == "win32":
            command += ".exe"
        
        printt(u"")
        printt(u"DESCARGAR:")
        printt(u"----------------------------------------------------------------")
        printt(u"[ URL DE DESCARGA FINAL ]", self.__URL)
        printt(u"[   DESTINO   ]", self.__TITULO)
        printt(u"\n[INFO] Presiona \"Ctrl + C\" para cancelar\n")
        
        # TODO: mejorar esto!
        args = self.__COMANDO_RTMPD.split() if self.__COMANDO_RTMPD is not None else self.__COMANDO_MENCO.split()
        
        try:
            printt(u"\nLanzando rtmpdump...\n")
            out = subprocess.call(args)
            if out == 0: # Descarga realizada con éxito
                printt(u"[OK] Descarga realizada con éxito")
            else:
                printt(u"[ERROR] Ha fallado la descarga")
        except OSError, e:
            printt(u"[!!!] ERROR. No se encuenta rtmpdump o mplayer:", e)
        except KeyboardInterrupt:
            salir(u"Bye!")
    
    def __getMMS(self):
        printt(u"")
        printt(u"DESCARGAR:")
        printt(u"----------------------------------------------------------------")
        printt(u"[ URL DE DESCARGA FINAL ]", self.__URL)
        printt(u"[   DESTINO   ]", self.__TITULO)
        
        
        if sys.platform == "win32":
            msg = '''Protocolo MMS aun no disponible en Windows.
            La URL FINAL DE DESCARGA que se muestra, es la localización final del archivo.
            Puedes descargar el archivo mediante esta URL a través de algún gestor de
            descargas que soporte la descarga a través del protocolo mms://
            '''
            printt(msg)
            return
        
        try:
            from pylibmms import core as libmmscore
        except ImportError, e:
            print e
            salir(u"[!!!] ERROR al importar libmms")
        
        printt(u"\n[INFO] Presiona \"Ctrl + C\" para cancelar\n")
        options = [self.__URL, self.__TITULO]
        libmmscore.run(options)

    
    def descargarVideo(self):
        print self.__TIPO
        if self.__TIPO == "http": self.__getHTTP()
        elif self.__TIPO == "rtmp" or self.__TIPO == "rtmpe": self.__getRTMP()
        elif self.__TIPO == "mms": self.__getMMS()
            
        
    def descargaVideoWindows(self, nombre=None):
        '''
            Procesa la descarga del vídeo llamanda a la función download de pyaxel para la mayoría de los
            vídeos en GNU/Linux y Mac OS X. Para sistemas win32, se llama a descargarVideoWindows() y tanto para
            GNU/Linux como para Mac OS X y Windows cuando el protocolo es mms:// se utiliza libmms (por ahora Windows no)
            y cuando el protocolo es rtmp:// se utiliza el binario rtmpdump que el user debe tener instalado.
        '''
        
        printt(u"")
        printt(u"DESCARGAR:")
        printt(u"----------------------------------------------------------------")

        printt(u"[ URL DE DESCARGA FINAL ]", self.__URL)
            
        printt(u"[INFO] Presiona \"Ctrl + C\" para cancelar")
        printt(u"")
        
        def estadodescarga(bloque, tamano_bloque, tamano_total):
            '''
                función reporthook que representa en pantalla información mientras
                se realiza la descarga
            '''
            # En Megas
            try:
                cant_descargada = ((bloque * tamano_bloque) / 1024.00) / 1024.00
                tamano_total = (tamano_total / 1024.00) / 1024.00
                porcentaje = cant_descargada / (tamano_total / 100.00)
                if porcentaje > 100.00:
                    porcentaje = 100.00
            except ZeroDivisionError:
                pass
                #print "[DEBUG] Error de divisiñon entre cero"
            # TODO: Agregar velocidad de descarga al progreso
            sys.stdout.write("\r[Descargando]: [ %.2f MiB / %.2f MiB ]\t\t[ %.1f%% ]" \
                            % (cant_descargada, tamano_total, porcentaje))
                            
        #######
        try:
            printt(u"[Destino]", self.__TITULO)
            urllib.urlretrieve(self.__URL, self.__TITULO, reporthook=estadodescarga)
            print ""
        except KeyboardInterrupt:
            salir("\nCiao!")
            