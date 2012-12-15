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

# Módulo para descargar todos los vídeos de la web de Canal Sur

__author__="aabilio"
__date__ ="$15-dic-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["canalsur.es", "canalsuralacarta.es"]

class CanalSur(Canal.Canal):
    '''
        Clase para manejar los vídeos de Canal Sur
    '''
    
    URL_CANALSUR = "http://canalsur.es"
    URL_CANALSUR_ALACARTA = "http://canalsuralacarta.es"
    
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

    def __alacarta(self):
        self.info(u"[INFO] A la carta")
        xml = Descargar.get(Descargar.get(self.url).split("_url_xml_datos=")[1].split("\"")[0])
        if xml.find("0x") != -1: xml = xml.decode('iso-8859-1').encode('utf8')
        # Comprobar si varias partes:
        # Un "<url> tiene que haber, comprobar si hay más de uno:"
        if xml[xml.find("<url>")+1:].find("<url>") != -1:
            self.info(u"[INFO] Varios Vídeos")
            a = xml.split("<url>")
            url = [a[i].split("</url>")[0] for i in range(1,len(a)) if not a[i].split("</url>")[0].find("doubleclick") != -1]
            ext = "." + url[0].split(".")[-1]
            b = xml.split("<title><![CDATA[")
            name = [b[i].split("]]></title>")[0] + ext for i in range(2,len(b))]
            if type(name) == list:
                for i in name:
                    b = Utiles.formatearNombre(i)
                    name[name.index(i)] = b
            else: name = Utiles.formatearNombre(name)
            try: tit = Utiles.recortar(xml, "<title><![CDATA[", "]]></title>") #El de la primera parte
            except: tit = u"Vídeo de Canal Sur A la Carta".encode("utf8")
            try: img = xml.split("<picture>")[1].split("</picture>")[0].strip()
            except: img = None
            try: desc = xml.split("<description>")[1].split("<![CDATA[")[1].split("]]>")[0].strip()
            except: desc = u"Vídeo de Canal Sur A la Carta".encode("utf8")
            
            return {"exito" : True,
                    "num_videos" : 1,
                    "mensaje"   : u"URL obtenido correctamente",
                    "videos":[{
                            "url_video" : url,
                            "url_img"   : img if img is not None else None,
                            "filename"  : name,
                            "tipo"      : "http",
                            "partes"    : len(url),
                            "rtmpd_cmd" : None,
                            "menco_cmd" : None,
                            "url_publi" : None,
                            "otros"     : None,
                            "mensaje"   : None
                            }],
                    "titulos": [tit] if tit is not None else None,
                    "descs": [desc] if desc is not None else None
                    }
        else:
        # Si solo es una parte (compatiblidad con versiones ateriores):
            self.info(u"[INFO] Vídeo único")
            url = "http://ondemand" + xml.split("<url>http://ondemand")[1].split("<")[0]
            ext = "." + url.split(".")[-1]
            tit = xml.split("<title><![CDATA[")[1].split("]")[0]
            name = Utiles.formatearNombre(tit + ext)
            try: img = xml.split("<picture>")[1].split("</picture>")[0].strip()
            except: img = None
            try:
                desc = xml.split("<description>")[1].split("<![CDATA[")[1].split("]]>")[0].strip()
            except: desc = u"Vídeo de Canal Sur A la Carta".encode("utf8")
            
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
        
        
    def __modoNormal(self):
        self.info(u"[INFO] Vídeo Normal")
        html = Descargar.get(self.url).decode('iso-8859-1').encode('utf8')
        url = html.split("flashvars=\"file=")[1].split("&")[0]
        ext = "." + url.split(".")[-1]
        tit = html.split("<title>")[1].split("<")[0]
        name = tit + ext
        name = Utiles.formatearNombre(name)
        try:
            desc = html.split("<div class=\"bloqEntradillaEnNoticia\">")[1].split("<p>")[1].split("</p>")[0].strip().decode('string-escape')
        except:
            desc = u"Vídeo de Canal Sur".encode("utf8")
        try: img = self.URL_CANALSUR + Utiles.recortar(html, "image=", "\"")
        except: img = None
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
        
        if self.url.find("canalsuralacarta.es") != -1: # CSur a la carta:
            return self.__alacarta()
        elif self.url.find("canalsur.es/") != -1: # Vídeos normales
            return self.__modoNormal()
        else: # No debería de suceder nuca
            raise Error.GeneralPyspainTVsError(u"No se ha encontrado contenido audiovisual en la página")




