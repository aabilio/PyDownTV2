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

# Mñodulo de ejemplo para la creación de un canal

__author__="nombre"
__date__ ="$xx-xxx-20xx xx:xx:xx$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["ejemplo.es", "ejemplo.com"]

class TVE(Canal.Canal):
    '''
        Clase para manejar los vídeos del canal XXXXX
    '''
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    # Métodos propios del canal:
    
    # Atributos disponibles:
    #    ** self.url (url recibida)
    #    ** self.opcs (diccionario de opciones) Ver Módulo Canal "_default_opcs" para opciones
    # Métodos disponibles de clase Canal:
    #    ** self.log() para mostrar por pantalla (está disponible si self.opcs["log"] es True)
    #    ** self.info() = log()
    #    ** self.debug() mostrar información de debug (está disponible si self.opcs["debug"] es True)
    
    # Comunicación de errores con nivel de aplicación:
    #    ** lanzar la excepción: raise Errors.GeneralPyspainTVsError("mensaje")
    
    # Funciones de Utiles:
    #    ** Utiles.formatearNombre("cadena") y Utiles.stringFormat("cadena") para quitar caracteres extraños
    
    # Funciones de Descargar:
    #    ** Descargar.getHtml(url, withHeader=False, utf8=False, header=std_headers)
    #        Recibe:
    #            - url (http://ejemplo.com/ruta/de/ejemplo)
    #            - withHeader (True or False)
    #            - utf8 (True or False)
    #            - header, de la forma:
    #            {
    #               'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
    #               'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
    #               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    #               'Accept': 'text/xml,application/xml,application/xhtml+xml,'
    #               'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    #               'Accept-Language': 'en-us,en;q=0.5',
    #            } <-- Esto se enviará en caso de omitir el header.
    #        Return:
    #            - Respuesta GET
    #    ** Descargar.isReachable(url)
    #        Recibe: 
    #            - url (http://ejemplo.com/ruta/de/ejemplo)
    #        Return:
    #            - True or False
    #         Comprueba si se puede acceder a una web
    #    ** Descargar.doPost(url, path, post_args, doseq=True, headers=None)
    #        Recibe:
    #            - url (http://ejemplo.com)
    #            - path (/ruta/de/ejemplo.php)
    #            - post_args (dicy, ej.: {"usuario":"antonio", "password":"pass"})
    #            - doseq (bool)
    #            - headers, de la forma:
    #            {
    #               'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
    #               'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
    #               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    #               'Accept': 'text/xml,application/xml,application/xhtml+xml,'
    #               'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    #               'Accept-Language': 'en-us,en;q=0.5',
    #            } <-- Esto se enviará en caso de omitir el header.
    #        Return:
    #            - Respuesta del POST



    def getInfo(self):
        '''
            Devuelve toda la información asociada a la URL recibida, de la siguiente forma:
            {
             "exito"     : bool,  <-- True (si se han obtenido videos) (bool)
             "num_video" : int,   <-- Número de vídeos obtenidos (int)
             "mensaje"   : u"" ,  <-- Mensajes de la API (ej.: El vídeo no ha sido encontrado ["exito": False]) (unicode)
             "videos"    :  [{ (dict)
                            "url_video" : [],   <-- Url de descarga de vídeo (list)
                            "url_img"   : "",   <-- Url de la miniatura del video (str/unicode)
                            "titulo"    : [],   <-- Título de las partes (list)
                            "tipo"      : "",   <-- http, rtmp[e,..], mms, ... (str/unicode)
                            "partes"    : int,  <-- Número de partes que tiene el vídeo (int)
                            "rtmpd_cmd" : [],   <-- Comando rtmpdump (si tipo == rtmp) sino None (list)
                            "menco_cmd" : [],   <-- Comando mencoder (Si tipo == rtmp) sino None (list)
                            "url_publi" : "",   <-- Url del vídeo de publicidad asociado al vídeo (str/unicode)
                            "otros"     : [],   <-- Lista donde se pueden pasar cosas opcionales (list)
                            "mensaje"   : ""    <-- Mensajes de la API (str/unicode)
                            }], <-- Debe ser una lista de tamaño "num_videos" (list)
             "titulos"   : [u""] <-- Titulos de los videos (list)
            }
            
            Los valores que no se rellenen, deberán devolver None.
            La clave "exito" es obligatoria, sino se puede encontrar el vídeo se puede devolver directamente:
            {
            "exito": False,
            "mensaje": "No se pudo descargar el video"  
            }
            
            "videos" y "mesajes" deben ser listas de cadenas (si no son None)
            "url_video", "titulo", "rtmp_cmd", "menco_cmd" (de "videos") deben ser listas de cadenas (si no son None)
        '''
        #Ejemplo:
        try:
            html = Descargar.getHtml(self.url)
            html.split("blabla")[0] # Buscar vídeo en html
        except Exception, e:
            raise Error.GeneralPyspainTVsError("No se encuentra la URL: "+e)
        url_video = "http://ejmeplo.com/ruta/de/ejemplo.mp4"
        url_img = "http://ejemplo.com/ruta/de/ejemplo.jpg"
        tit_vid = "título de ejemplo"
        titulo = Utiles.formatearNombre(tit_vid + ".mp4")
        
        ejemplo = {
                    "exito" : True,
                    "num_videos" : 1,
                    "mensaje"   : u"URL obtenida correctamente",
                    "videos":[{
                            "url_video" : [url_video],
                            "url_img"   : url_img if url_img is not None else None,
                            "titulo"    : [titulo] if titulo is not None else None,
                            "tipo"      : "http",
                            "partes"    : 1,
                            "rtmpd_cmd" : None,
                            "menco_cmd" : None,
                            "url_publi" : None,
                            "otros"     : None,
                            "mensaje"   : None
                            }],
                    "titulos": [tit_vid] if tit_vid is not None else None
                    }
        return ejemplo
