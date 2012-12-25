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

# Módulo para descargar todos los vídeos de la web de Giralda Televisión

__author__="aabilio"
__date__ ="$25-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["giraldatv.es"]

class GiraldaTV(Canal.Canal):
    '''
        Clase para manejar los vídeos de Giralda Televisión.
    '''
    
    URL_GIRALDATV = "http://giraldatv.es"
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    # Métodos propios del canal, start the party!
    # Attributos disponibles:
    #    - self.url (url recibida)
    #    - self.opcs (diccionario de opciones) Ver Módulo Canal "_default_opcs" para opciones
    # Métodos disponibles de clase Canal:
    #    - log() para mostrar por pantalla (está disponible si self.opcs["log"] es True)
    #    - self.debug() mostrar información de debug (está disponible si self.opcs["debug"] es True)
    # Comunicación de errores con nivel de aplicación:
    #    - lanzar la excepción: raise Error.GeneralPyspainTVsError("mensaje")

    def getInfo(self):
        '''
            Devuelve toda la información asociada a la URL recibida, de la siguiente forma:
            {
             "exito"     : bool,  <-- True (si se han obtenido videos)
             "num_video" : int,   <-- Número de vídeos obtenidos
             "mensaje"   : u"" ,  <-- Mensajes de la API (ej.: El vídeo no ha sido encontrado ["exito": False])
             "videos"    :  [{
                            "url_video" : [],   <-- Url de descarga de vídeo
                            "url_img"   : "",   <-- Url de la miniatura del video
                            "filename"  : [],   <-- Nombre de las partes para guardar en disco
                            "tipo"      : "",   <-- http, rtmp[e,..], mms, ...
                            "partes"    : int,  <-- Número de partes que tiene el vídeo
                            "rtmpd_cmd" : [],   <-- Comando rtmpdump (si tipo == rtmp) sino None
                            "menco_cmd" : [],   <-- Comando mencoder (Si tipo == rtmp) sino None
                            "url_publi" : "",   <-- Url del vídeo de publicidad asociado al vídeo
                            "otros"     : [],   <-- Lista donde se pueden pasar cosas opcionales
                            "mensaje"   : ""    <-- Mensajes de la API
                            }], <-- Debe ser una lista de tamaño "num_videos"
             "titulos"   : [u""], <-- Titulos de los videos
             "descs"     : [u""] <-- Descripción de cada vídeo
            }
            
            Los valores que no se rellenen, deberán devolver None.
            La clave "exito" es obligatoria, sino se puede encontrar el vídeo se puede devolver directamente:
            {
            "exito": False,
            "mensaje": "No se pudo descargar el video"  
            }
            
            "videos", "mesajes" y "descs" deben ser listas de cadenas (si no son None)
            "url_video", "filename", "rtmp_cmd", "menco_cmd" (de "videos") deben ser listas de cadenas (si no son None)
        '''
        try:
            html = self.gethtml()#.replace(" ", "")
        except Exception,e:
            try: # Para Google App Engine
                from google.appengine.api import urlfetch
                result = urlfetch.fetch(self.url, headers=Descargar.std_headers, deadline=30)
                html = result.content
            except Exception, b:
                try:
                    raise Error.GeneralPyspainTVsError(b)
                except:
                    raise Error.GeneralPyspainTVsError(u"La solicitud contiene demasiados vídeos. Se está trabajando para arreglar esto.")
        
        if html.find("contentArray[") != -1:
            self.info(u"[INFO] Se han detectado varios vídeos en la página")
            try:
                # Deleimitar los bloques de vídeos:
                videos = [n.split("',")[1:] for n in html.split("contentArray[")[1:]]
                
                titulos = [v[0].replace("'","").strip() for v in videos]
                urls = [v[2].replace("'","").strip() for v in videos]
                ext = "."+urls[0].split(".")[-1] 
                try: names = [Utiles.formatearNombre(v[0].replace("'","").strip()+ext) for v in videos]
                except: names = [u"VideoDeGiraldaTV.mov"]*len(urls)
                descs = [v[1].replace("'","").strip() for v in videos]
                imgs = [v[4].replace("'","").strip() for v in videos]
                
                rVideos = []
                for i in range(len(urls)):
                    temp = {
                    "url_video" : [urls[i]],
                    "url_img"   : imgs[i] if imgs[i] is not None else None,
                    "filename"  : [names[i]] if names is not None else None,
                    "tipo"      : "http",
                    "partes"    : 1,
                    "rtmpd_cmd" : None,
                    "menco_cmd" : None,
                    "url_publi" : None,
                    "otros"     : None,
                    "mensaje"   : None
                    }
                    rVideos.append(temp)
            except Exception, e:
                raise Error.GeneralPyspainTVsError(u"No se han podido obtener información sobre los vídeos.")
        else:
            raise Error.GeneralPyspainTVsError(u"No se han encontrado vídeos en la página.")
             
        return {"exito" : True,
                "num_videos" : len(titulos),
                "mensaje"   : u"URL obtenido correctamente",
                "videos": rVideos,
                "titulos": titulos if titulos is not None else None,
                "descs": descs if descs is not None else None
                }   


