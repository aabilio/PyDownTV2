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

# Módulo para descargar todos los vídeos de la web de Radio Televisión de Castilla-La Mancha

__author__="aabilio"
__date__ ="$21-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["rtvcm.es"]

class RTVCM(Canal.Canal):
    '''
        Clase para manejar los vídeos de RTVCM
    '''
    
    URL_RTVCM = "http://rtvcm.es"
    
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
        
        html = self.gethtml().decode('iso-8859-1').encode('utf8').replace("ü", "u") #FIXME: Esta chapuza
        
        if html.find("showVideo(\'") == -1:
            raise Error.GeneralPyspainTVsError(u"No se han encontrado vídeos en la página")#Hay Vídeos?
        
        try:
            videos = [n.split("\'")[0] for n in html.split("showVideo(\'")[1:]]
            try: titulos = [n.split("\"")[0] for n in html.split("f4v\')\" title=\"")[1:]]
            except: titulos = u"Vídeo de Radio Televisión de Castilla-La Mancha".encode('utf8')*len(videos)
            desc = titulos
            try: names = [Utiles.formatearNombre(n+".mp4") for n in titulos]
            except: names = "VideosRTVCM.mp4"*len(videos)
            url = Utiles.recortar(html.split("clip:")[1], "url: \'", "\'")
            urls = [url+n for n in videos]
            try: img_b = Utiles.recortar(html.split("logo:")[1], "url: \'", "\'")
            except: img_b=None
            try: img = Utiles.recortar(html.split("<div class=\"centralContent\">")[1], "<img src=\"", "\"")
            except: img = img_b if img_b is not None else None
            
            rVideos = []
            for i in range(len(videos)):
                c = "rtmpdump -r '"+urls[i]+"' -o '"+names[i]+"'"
                temp = {
                "url_video" : [urls[i]],
                "url_img"   : img if img is not None else None,
                "filename"  : [names[i]] if names is not None else None,
                "tipo"      : "rtmp",
                "partes"    : 1,
                "rtmpd_cmd" : [c],
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
                rVideos.append(temp)
        except:
            raise Error.GeneralPyspainTVsError(u"No se han podido conseguir los enlaces")
        
        return {"exito" : True,
                "num_videos" : len(titulos),
                "mensaje"   : u"URL obtenido correctamente",
                "videos":rVideos,
                "titulos": titulos if titulos is not None else None,
                "descs": desc if desc is not None else None
                }




