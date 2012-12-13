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

# Módulo para la descargar de vídeos desde crtvg.es

__author__="aabilio"
__date__ ="$18-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
#import Error

url_validas = ["crtvg.es"]

class CRTVG(Canal.Canal):
    '''
        Clase para manejar los vídeos de la Televisión de Galiza
    '''
    
    URL_CRTVG = "http://www.crtvg.es/"
    
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
    #    - lanzar la excepción: raise Errors.GeneralPyspainTVsError("mensaje")

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
        
        # Diferenciar entre vídeos "á carta" y vídeos de "agalegainfo":
        streamHTML = Descargar.get(self.url).decode('string-escape')
        tit_vid = streamHTML.split("title: \"")[1].split("\"")[0]
        htmlBackup = streamHTML
        streamHTML = streamHTML.replace(" ", "").replace("\t", "").replace("\n", "")
        
        if self.url.find("a-carta") != -1:
            self.info(u"[INFO] Modo \"Á Carta\"")
        else:
            self.info(u"[INFO] Vídeo Normal (No \"Á Carta\")")
        
        rtmp = streamHTML.split("rtmp:{")[1]
        s = rtmp.split("url:\"")[1].split("\"")[0]
        r = rtmp.split("netConnectionUrl:\"")[1].split("\"")[0]
        a = r.split("/")[-1]
        video = rtmp.split("clip:{")[1]
        y = video.split("url:\"")[1].split("\"")[0]
        name = video.split("title:\"")[1].split("\"")[0] + "." + y.split(".")[-1]
        img = streamHTML.split("backgroundImage:\"url(")[1].split(")")[0]
        url = r
                
        if name:
            name = Utiles.formatearNombre(name)
        rtmpd_cmd = "rtmpdump -r "+url+" -y "+y+" -s "+s+" -a "+a+" -o "+name
        
        desc = None        
        try: #FIXME: Pillar más que solo el primer párrafo
            desc = Utiles.recortar(htmlBackup, "<p style=\"text-align: justify;\">", "</p>").strip()
        except:
            desc = tit_vid if tit_vid is not None else None
        
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenida correctamente",
                "videos":[{
                        "url_video" : [url],
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : "rtmp",
                        "partes"    : 1,
                        "rtmpd_cmd" : [rtmpd_cmd],
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit_vid] if tit_vid is not None else None,
                "descs": [desc] if desc is not None else None
                }
            
            
            
            
            
            