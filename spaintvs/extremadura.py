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

# Módulo para descargar todos los vídeos de la web Extremadura Televisión

__author__="aabilio"
__date__ ="$17-dic-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["canalextremadura.es"]

class CExtremadura(Canal.Canal):
    '''
        Clase para manejar los vídeos de Canal Extremadura
    '''
    
    URL_CANAL_EXTREMADURA = "http://canalextremadura.es"
    URL_ETV = "http://extremaduratv.canalextremadura.es/"
    
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
        
        if self.url.find("tv-a-la-carta/") != -1 or self.url.find("http://alacarta.canalextremadura.es/tv") != -1 \
                                                        or self.url.find("canalextremadura.es/alacarta/tv/") != -1:
            self.info(u"[INFO] TV a la carta")
            html = html2 = Descargar.get(self.url).decode('utf8').encode('utf8')
            html = html.replace(" ", "")
            if html.find("crea_video_hd(") != -1:
                urlFLV = html.split("crea_video_hd(\"")[1].split("\"")[0]
                streamFLV = Descargar.get(urlFLV)
                url = "http://" + streamFLV.split("http://")[1]
                ext = "." + url.split(".")[-1].split("?")[0]
            elif html.find("file:'") != -1:
                try:
                    url = html.split("\'file\':\'")[1].split("\'")[0] #Modo nomal nuevo
                except: #Modo normal antiguo
                    url = html.split("streamer:\'")[1].split("\'")[0] + html.split("file:\'")[1].split("\'")[0]
                ext = "." + url.split(".")[-1]
            elif html.split("if(isiPad)") != -1: #HTTP para iPad
                url = html.split("<video")[1].split(".mp4")[0].split("\"")[-1] + ".mp4"
                ext = ".mp4"
            elif html.find("rel=\"rtmp://") != -1: #RTMP en alacarta
                url = "rtmp://" + html.split("rel=\"rtmp://")[1].split("\"")[0].replace("#", "")
                url = url.split(".mp4")[0] + ".mp4"
                ext = ".mp4"
                name = html.split("<title>")[1].split("<")[0] + ext
                if name: name = Utiles.formatearNombre(name)
                
                try: img = self.URL_CANAL_EXTREMADURA + Utiles.recortar(html2, "poster=\"", "\"")
                except: img = None
                try: tit = Utiles.recortar(html2, "<title>", "</title>").replace("Canal Extremadura", "").replace("|","").strip()#.encode('utf8')
                except: tit = u"Vídeo de Canal Extremadura".encode('utf8')
                try: desc = Utiles.recortar(html2, "<div class=\"descripcion\">", "</div>").strip()#.ecnode('utf8')
                except: desc = u"Vídeo de Canal Extremadura".encode('utf8')
                else:
                    if type(desc) is str:
                        if desc == "": desc = u"Vídeo de Canal Extremadura".encode('utf8')
                    elif type(desc) is unicode:
                        if desc == u"": desc = u"Vídeo de Canal Extremadura".encode('utf8')
                
                rtmpd_cmd = u"rtmpdump -r "+url+" -o "+name
                
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
            else:
                raise Error.GeneralPyspainTVsError(u"No se encuentra el contenido audiovisual")
            name = html.split("<title>")[1].split("<")[0] + ext
        #TODO: Dar soporte a la radio, por ahora no    
#        elif self.url.find("radio-a-la-carta/") != -1 or self.url.find("http://alacarta.canalextremadura.es/radio") != -1 \
#                                                    or self.url.find("canalextremadura.es/alacarta/radio/") != -1:
#            self.info(u"[INFO] Radio A la Carta")
#            html = Descargar.get(self.url).replace(" ", "")
#            try: #Modo nuevo
#                url = html.split("<divclass=\"descargar\">")[1].split("<ahref=\"")[1].split("\"")[0]
#            except: #Modo antiguo
#                url = html.split("s1.addVariable(\'file\',\'")[1].split("\'")[0]
#            name = html.split("<title>")[1].split("<")[0] + ".mp3"
        
        else: #Modo normal nuevo con nueva url recibida
            try:
                self.info(u"[INFO] Modo Genérico")
                html = Descargar.get(self.url).replace(" ", "")
                url = html.split("\'file\':\'")[1].split("\'")[0] #Modo nomal nuevo
                ext = "." + url.split(".")[-1]
                name = html.split("<title>")[1].split("<")[0] + ext
            except:
                Error.GeneralPyspainTVsError(u"No se ha podido acceder a ningún contenido")
            
        if name:
            name = Utiles.formatearNombre(name)
        
        try: img = self.URL_CANAL_EXTREMADURA + Utiles.recortar(html2, "poster=\"", "\"")
        except: img = None
        try: tit = Utiles.recortar(html2, "<title>", "</title>").replace("Canal Extremadura", "").replace("|","").strip()#.encode('utf8')
        except: tit = u"Vídeo de Canal Extremadura".encode('utf8')
        try: desc = Utiles.recortar(html2, "<div class=\"descripcion\">", "</div>").strip()#.ecnode('utf8')
        except: desc = u"Vídeo de Canal Extremadura".encode('utf8')
        else:
            if type(desc) is str:
                if desc == "": desc = u"Vídeo de Canal Extremadura".encode('utf8')
            elif type(desc) is unicode:
                if desc == u"": desc = u"Vídeo de Canal Extremadura".encode('utf8')
        
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url],
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : "http",
                        "partes"    : 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit] if tit is not None else None,
                "descs": [desc] if desc is not None else None
                }




