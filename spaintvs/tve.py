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

# Módulo para descargar todos los vídeos de la web de rtve.es ("A la carta" o no)
# Antes era el módulo de tvalacarta.py modificado para dar soporte a todos los vídeos

__author__="aabilio"
__date__ ="$10-oct-2012 11:35:37$"


import urllib
import urllib2

import Canal
import Utiles
import Descargar
import Error

import logging

url_validas = ["rtve.es"]

class TVE(Canal.Canal):
    '''
        Clase para manejar los vídeos de la RTVE (todos).
    '''
    
    URL_RTVE = "http://rtve.es"
    
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
    
    def __getSerieName(self, url):
        url = url.split("#/")[1]
        r=[n for n in url.split("/") 
           if not n.isdigit() and 
           n != "videos" and n!="todos"]
        return r[0] if len(r)==1 else None
    
    def __ClanTV(self, html, ID):
        self.info(u"[INFO] Vídeo de Clan")
        logging.error("entro en clan")
        buscar = self.__getSerieName(self.url)
        logging.error(buscar)
        if buscar is None:
            #html = Descargar.get(self.url)
            buscar = "/".join(self.url.split("/")[6:9])
            logging.error(buscar)
            if not buscar.startswith("videos") and not buscar.endswith("todos"):
                try:
                    serie = Utiles.recortar(self.url, "/videos/", "/todos/")
                    logging.error(serie)
                except: #http://www.rtve.es/infantil/videos-juegos/#/videos/suckers/todos/suckers-ventosas/1605449 ó */
                    Surl = self.url.split("/")
                    if Surl[-1] == "": buscar = Surl[-3]
                    if Surl[-1].isdigit(): buscar = Surl[-2]
                    else:
                        raise Error.GeneralPyspainTVsError(u"Error al encontrar la serie. Por favor reporta el error")
                else:
                    buscar = "/videos/"+serie+"/todos/"
                    logging.error(buscar)
            buscar = str(buscar)
        self.debug(u"Serie:", buscar)
        logging.error("final: "+ buscar)
        #Ir a la página de descripción de vídeos de Clan
        try:
            dataURL = "http://www.rtve.es/infantil/components/"+html.split(buscar)[0].split("<a rel=\"")[-1].split("\"")[0]+"/videos.xml.inc"
        except Exception, e:
            logging.error(e.__str__())
        self.debug(u"URL Clan data: "+dataURL)
        logging.error(dataURL)
        data = Descargar.get(dataURL).split("<video id=\""+str(ID))[1].split("</video>")[0]
        logging.error("tengo data")
        url = self.URL_RTVE+Utiles.recortar(data, "url=\"", "\"")
        logging.error(url)
        img = Utiles.recortar(data, "url_image=\"", "\"")
        logging.error(img)
        tit = Utiles.recortar(data, "<title>", "</title>")
        logging.error(tit)
        name = Utiles.recortar(data, "url_name=\"", "\"")+"."+url.split(".")[-1]
        logging.error(name)
        desc = Utiles.recortar(data, "<sinopsis>", "</sinopsis>").strip()
        logging.error(desc)
        if desc == "" or desc == " " or desc == ".":
            desc = u"Vídeo de Clan TV: ".encode('utf8') +  Utiles.recortar(data, "url_name=\"", "\"")
         
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url],
                        "url_img"   : img,
                        "filename"  : [name],
                        "tipo"      : "http",
                        "partes"    : 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit],
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
        #TODO: Cuida con las paginas que tiene más de un vídeo. De momento funciona porque es el primer video que aparece!
        
        # Primero: nos quedamos con le id dependiendo si el user metio la url con
        # una barra (/) final o no y si tiene extensión (no es alacarta)
        logging.error(self.url)
        videoID = self.url.split('/')[-1]
        if videoID == "":
            videoID = self.url.split('/')[-2]
        elif videoID.find(".shtml") != -1 or videoID.find(".html") != -1 or \
            videoID.find(".html") != -1:
            videoID = videoID.split('.')[0]
        
        self.debug(u"ID del vídeo en url = " + videoID)
        
        #if self.url.find("rtve.es/infantil/") != -1: self.url = self.url.replace("/#","") # Vídeos de Clan a veces falla con el ancla
        
        # Añadido para vídeos nuevos (periodo de prueba):
        sourceHTML = Descargar.getHtml(self.url).decode('string-escape')
        #sourceHTML = self.toUtf(sourceHTML)
        videoID_comp = None
        if sourceHTML.find("flashcontentId:\'videoplayer") != -1:
            videoID_comp = sourceHTML.split("flashcontentId:\'videoplayer")[1].split("\'")[0]
            if videoID_comp != videoID: videoID = videoID_comp
        if sourceHTML.find("<div id=\"video") != -1:
            videoID_comp = sourceHTML.split("<div id=\"video")[1].split("\"")[0]
            if videoID_comp != videoID and videoID_comp.isdigit(): videoID = videoID_comp
        ########################################################
        
        self.debug(u"ID del vídeo en HTML = " + videoID_comp if videoID_comp else "No ID en HTML")
        self.log(u"[INFO] ID del Vídeo :", videoID)
        
        if self.url.find("rtve.es/infantil/") != -1:
            return self.__ClanTV(sourceHTML, videoID)

        # -- Método 1 Octubre 2012:
        self.debug(u"Probando método de 1 de uno de Octubre de 2012")
        url = "http://www.rtve.es/ztnr/consumer/xl/video/alta/" + videoID + "_es_292525252525111"
        self.debug(url)
        
        user_agent="Mozilla"
        opener = urllib2.build_opener(NoRedirectHandler())
        urllib2.install_opener(opener)
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, None, headers)
        u = urllib2.urlopen(req)
        try:
            urlVideo = u.info().getheaders("Location")[0]
        except:
            raise Error.GeneralPyspainTVsError("No se encuentra Location")
        u.close()
        if urlVideo != "":
            url_video = urlVideo.replace("www.rtve.es", "media5.rtve.es")
            titulo = sourceHTML.split("<title>")[1].split("</")[0].replace("RTVE.es", "").replace("-", "").strip()
            filename = titulo + ".mp4"
            filename = Utiles.formatearNombre(filename)
            #sourceHTML = sourceHTML.split("<div id=\"video")[1].split("flashvars")[0] # Me quedo solo con la parte del vídeo principal
            url_img = sourceHTML.split("\"thumbnail\" content=\"")[1].split("\"")[0]
        else:
            raise Error.GeneralPyspainTVsError("No se pudo encontrar el enlace de descarga")
        # -- Método 1 Octubre 2012 FIN
        
        desc = None
        try: #obtener descripción del video
            desc = Utiles.recortar(sourceHTML, "<meta itemprop=\"description\" content=\"", "\"").strip()
        except:
            try:
                desc = Utiles.recortar(sourceHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
            except:
                try:
                    desc = Utiles.recortar(sourceHTML, "<meta name=\"description\" content=\"", "\"").strip()
                except:
                    desc = u"Vídeos de Televión Española"
                
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url_video],
                        "url_img"   : url_img,
                        "filename"  : [filename],
                        "tipo"      : "http",
                        "partes"    : 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [titulo],
                "descs": [desc] if desc is not None else None
                }

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
