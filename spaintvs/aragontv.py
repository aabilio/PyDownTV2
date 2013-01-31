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

# Módulo para descargar todos los vídeos de Aragon TV

__author__="aabilio"
__date__ ="$15-dic-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["aragontelevision.es"]

class AragonTV(Canal.Canal):
    '''
        Clase para manejar los vídeos de Aragón Televisión
    '''
    
    URL_ARAGONTV = "http://aragontelevision.es"
    URL_ARAGONTV_ALACARTA = "http://alacarta.aragontelevision.es/"
    
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
    
        html = Descargar.get(self.url)
        try:
            name = Utiles.recortar(html, "<title>", "</title>")
            html2 = html.replace("%3A", ":").replace("%2F", "/").replace(" ", "").replace("\t", "")
            clip = html2.split("clip:")[1].split("url:\'")[1].split("\'")[0].replace("mp4:", "")
            server = html2.split("netConnectionUrl:\'")[1].split("\'")[0]
            url = server + clip
            name += "." + clip.split(".")[-1]
            img1 = html.split("logo:")[1].split("url:")[1].split("\'")[1].split("\'")[0]
            if img1.find("aragontelevision.es") != -1: img = img1
            else: img = self.URL_ARAGONTV_ALACARTA + img1#html.split("logo:")[1].split("url:")[1].split("\'")[1].split("\'")[0]
            
            try:
                desc = Utiles.recortar(html, "<span class=\"title\">Resumen del vídeo</span>", "</div>").strip().decode('string-escape')
            except:
                desc = u"Vídeo de Aragón Televisión".encode("utf8")
            else:
                if desc == u"" or desc == "":desc = u"Vídeo de Aragón Televisión".encode("utf8")
                
            try:
                tit = Utiles.recortar(html, "<title>", "</title>")
            except:
                tit = u"Vídeo de Aragón Televisón".encode("utf8")
                
            if name: name = Utiles.formatearNombre(name)
            rtmpd_cmd = "rtmpdump -r "+url+" -o "+name
        except:
            raise Error.GeneralPyspainTVsError(u"Error al recuperar el vídeo de Aragon TV")
    
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
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
                "titulos": [tit] if tit is not None else None,
                "descs": [desc] if desc is not None else None
                }




