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

# Módulo Radio Televisión Principado de Asturias

__author__="aabilio"
__date__ ="$10-dic-2012 19:21:30$"

import Canal
import Utiles
import Descargar
#import Error

url_validas = ["rtpa.es"]

class RTPA(Canal.Canal):
    '''
        Clase para manejar los vídeos de rtpa.es
    '''
    
    TOKEN = "http://servicios.rtpa.es/flumotion/player/tokenondemand_mp4.php?r=vod&v="
    TOKEN_ARCHIVO = "http://www.rtpa.es/vod_get_m3u_video.php?id="
    URL_RTPA = "http://rtpa.es/"
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
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
        
        try: #Tratar de quitar caracteres especiales de las urls que no lo necesitan
            self.url = self.url.split("video:")[0] + "video:_" + self.url.split("_")[1]
        except:
            pass
        
        streamHTML = htmlBackup = Descargar.getHtml(self.url).decode('iso-8859-1').encode('utf8') #rtpa codigicada en iso..
        streamHTML = streamHTML.replace("\n", "").replace("\t", "")
        
        partes = None
        #método 12/11/2012:
        if streamHTML.find("html5") != -1:
            partes = 1
            name = streamHTML.split("<div id=\"sobreElVideo\">")[1].split("<h3>")[1].split("</h3>")[0] + ".mp4"
            streamHTML = streamHTML.replace(" ", "")
            try:
                url = streamHTML.split("html5")[1].split("\'file\':\'")[1].split("\'")[0]
            except:
                url = streamHTML.split("html5")[0].split("\'file\':\'")[1].split("\'")[0]
        else:
            # Cuantas partes son:
            try: 
                partes = int(streamHTML.split("&partes=")[1].split("&")[0])
            except IndexError: # No existe "&partes"
                partes = 1
            
            if partes == 1:
                videoID = streamHTML.split("<param value=\"video1=")[1].split("&")[0]
                if videoID.find("http://") != -1:
                    url = videoID
                    name = streamHTML.split("data-text=\"")[1].split("\"")[0].strip() + "." + url.split(".")[-1]
                else:
                    # Probar entre TOKEN nuevo y antiguo por reproductor:
                    repro = streamHTML.split("<param value=\"player/")[1].split("\"")[0]
                    if repro == "reproductorVideoOnDemmand-mp4-rtpa.swf": # Antiguo
                        streamINFO = self.__descHTML(self.TOKEN_ARCHIVO + videoID)
                        url = "http://" + streamINFO.split("http://")[1]
                    else: # Reproductor nuevo: "reproductorVideoOnDemmand.swf"
                        streamINFO = self.__descHTML(self.TOKEN + videoID + "_1")
                        streamINFO = self.__descHTML(streamINFO.split("&url=")[1])
                        url = "http://" + streamINFO.split("http://")[1]
                    name = streamHTML.split("<div id=\"sobreElVideo\">")[1].split("<h3>")[1].split("</h3>")[0]
                    if name == "":
                        name = streamHTML.split("<title>")[1].split("</title>")[0] + ".mp4"
                    else: name + ".mp4"
            else:
                # Recordar que hay videos que ponen varias partes en las que realmente solo existe una:
                videoID = streamHTML.split("<param value=\"video1=")[1].split("&")[0]
                url = []
                name = []
                for i in range(1, partes+1):
                    streamINFO = self.__descHTML(self.TOKEN + videoID + "_" + str(i))
                    streamINFO = self.__descHTML(streamINFO.split("&url=")[1])
                    
                    tmp_url = "http://" + streamINFO.split("http://")[1]
                    tmp_name = streamHTML.split("<div id=\"sobreElVideo\">")[1].split("<h3>")[1].split("</h3>")[0] +"_part" + str(i)
                    if tmp_name == "":
                        tmp_name = streamHTML.split("<title>")[1].split("</title>")[0] + "_part" + str(i) + ".mp4"
                    else: tmp_name + ".mp4"
                    
                    if Descargar.isReachable(tmp_url):
                        url.append(tmp_url)
                        name.appen(tmp_name)
                        continue
                    else:
                        break
                    
        #FIXME: Gran fixme aquí, arreglat todo esto de desc y de tit_vid
        try: #imagen del vídeo
            img = self.URL_RTPA + Utiles.recortar(htmlBackup, "\'image\': \'", "\'")
        except:
            img = None
        
        desc = u""
        try: # Descripción del vídeo
            d = htmlBackup.split("<div class=\"overview\">")[1].split("<div>")[1].split("</div>")[0].strip()
        except:
            try:
                d = htmlBackup.split("<div class=\"overview\">")[1].split("<p>")[1].split("</p>")[0].strip()
            except:
                pass
        try: # desc coding
            desc = unicode(d).encode("utf8")
        except:
            desc = u"Vídeo de la web de Radio Televisión del Principado de Asturias".encode("utf8")
        if desc == u"": desc = u"Vídeo de la web de Radio Televisión del Principado de Asturias".encode("utf8")
        
        tit_vid = u""
        try: #Título del vídeo
            tit = htmlBackup.split("<div id=\"sobreElVideo\">")[1].split("<h3>")[1].split("</h3>")[0].strip()
        except:
            try:
                tit = htmlBackup.split("<div id=\"sobreElVideo\">")[1].split("<h4 class=\"")[1].split(">")[1].split("<")[0].strip()
            except:
                pass
        try: #titulo coding
            tit = Utiles.tituloFormat(tit)
            tit_vid = unicode(tit).encode("utf8")
        except:
            tit_vid = u"Vídeo de la web de Radio Televisión del Principado de Asturias".encode("utf8")
        if tit_vid == u"": tit_vid = u"Vídeo de la web de Radio Televisión del Principado de Asturias".encode("utf8")
        
        if type(name) == list:
            for i in name:
                b = Utiles.formatearNombre(i)
                name[name.index(i)] = b
        else:
            name = Utiles.formatearNombre(name)
        
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenida correctamente",
                "videos":[{
                        "url_video" : [url] if type(url) != list else url,
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : "http",
                        "partes"    : partes if partes is not None else 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit_vid] if tit_vid is not None else None,
                "descs": [desc] if desc is not None else None
                }
        