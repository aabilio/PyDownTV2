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

import xml.etree.ElementTree

from base64 import b64decode as decode
import re

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
        logging.debug("entro en clan")
        buscar = self.__getSerieName(self.url)
        logging.debug(buscar)
        if buscar is None:
            #html = Descargar.get(self.url)
            buscar = "/".join(self.url.split("/")[6:9])
            logging.debug(buscar)
            if not buscar.startswith("videos") and not buscar.endswith("todos"):
                try:
                    serie = Utiles.recortar(self.url, "/videos/", "/todos/")
                    logging.debug(serie)
                except: #http://www.rtve.es/infantil/videos-juegos/#/videos/suckers/todos/suckers-ventosas/1605449 ó */
                    Surl = self.url.split("/")
                    if Surl[-1] == "": buscar = Surl[-3]
                    if Surl[-1].isdigit(): buscar = Surl[-2]
                    else:
                        raise Error.GeneralPyspainTVsError(u"Error al encontrar la serie. Por favor reporta el error")
                else:
                    buscar = "/videos/"+serie+"/todos/"
                    logging.debug(buscar)
            buscar = str(buscar)
        self.debug(u"Serie:", buscar)
        logging.debug("final: "+ buscar)
        #Ir a la página de descripción de vídeos de Clan
        try:
            dataURL = "http://www.rtve.es/infantil/components/"+html.split(buscar)[0].split("<a rel=\"")[-1].split("\"")[0]+"/videos.xml.inc"
        except Exception, e:
            logging.debug(e.__str__())
        self.debug(u"URL Clan data: "+dataURL)
        logging.debug(dataURL)
        data = Descargar.get(dataURL).split("<video id=\""+str(ID))[1].split("</video>")[0]
        logging.debug("tengo data")
        url = self.URL_RTVE+Utiles.recortar(data, "url=\"", "\"")
        logging.debug(url)
        img = Utiles.recortar(data, "url_image=\"", "\"")
        logging.debug(img)
        tit = Utiles.recortar(data, "<title>", "</title>")
        logging.debug(tit)
        name = Utiles.recortar(data, "url_name=\"", "\"")+"."+url.split(".")[-1]
        logging.debug(name)
        desc = Utiles.recortar(data, "<sinopsis>", "</sinopsis>").strip()
        logging.debug(desc)
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
    
    def getID(self, url):
        IDs = [i for i in url.split("/") if i.isdigit() and len(i)>5]
        return IDs[0] if IDs else None
        
    
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
        logging.debug(self.url)
        
        videoID = self.url.split('/')[-1]
        if videoID == "":
            videoID = self.url.split('/')[-2]
        elif videoID.find(".shtml") != -1 or videoID.find(".html") != -1 or \
            videoID.find(".html") != -1:
            videoID = videoID.split('.')[0]
        
        if not videoID.isdigit(): videoID = self.getID(self.url)
            
        try: self.debug(u"ID del vídeo en url = " + videoID)
        except: pass
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
        
        if videoID is None: raise Error.GeneralPyspainTVsError(u"No se encuentra el ID del vídeo")
        
        if self.url.find("rtve.es/infantil/") != -1:
            return self.__ClanTV(sourceHTML, videoID)

        # -- Método 24 Mayo 2013
        self.debug(u"Probando método de 24 de uno de Mayo de 2013")
        try: manager = re.findall('data-idManager="(.*?)"', sourceHTML)[0]
        except:
            try: manager = re.findall('idManager="(.*?)"', sourceHTML)[0]
            except: manager = "default"

        # # Nuevo método (22/02/14) , dejo el actual que todavía funciona
        # if sourceHTML.find("themadvideo.com/player/js/MadVideo.js.php") != -1:
            
        #     themadvideo_id = re.findall('<iframe.*id\=\"visor(.*)\"' , sourceHTML)[0]
        #     xmldata = Descargar.get("http://studio.themadvideo.com/api/videos/%s/player_data" % themadvideo_id).decode('utf8')
        #     xmltree = xml.etree.ElementTree.fromstring(xmldata)

        #     urlVideo = xmltree.find('./Layout/VideoPlayer/Data/src').text
        #     url_img = xmltree.find('./Layout/VideoPlayer/Data/Keyframe').text
        #     titulo = xmltree.find('.').attrib['title']
        #     try: name = Utiles.formatearNombre(titulo) + ".mp4"
        #     except: name = "VideoRtve.mp4"
        #     desc = None
        
        tipo = "videos"
        url = "http://www.rtve.es/ztnr/movil/thumbnail/%s/%s/%s.png" % (manager, tipo, videoID)

        self.debug(u"Probando url:", url)
        try:
            tmp_ = decode(Descargar.getHtmlHeaders(url, {"Referer": "http://www.rtve.es"}))
            tmp = re.findall(".*tEXt(.*)#[\x00]*([0-9]*).*", tmp_)[0]
            tmp = [n for n in tmp]
            cyphertext = tmp[0]
            key = tmp[1]
            tmp = tmp = [0 for n in range(500)]

            # Créditos para: http://sgcg.es/articulos/2012/09/11/nuevos-cambios-en-el-mecanismo-para-descargar-contenido-multimedia-de-rtve-es-2/
            intermediate_cyphertext = ""
            increment = 1
            text_index = 0
            while text_index < len(cyphertext):
                text_index = text_index + increment
                try: intermediate_cyphertext = intermediate_cyphertext + cyphertext[text_index-1]
                except: pass
                increment = increment + 1
                if increment == 5: increment = 1

            plaintext = ""
            key_index = 0
            increment = 4
            while key_index < len(key):
                key_index = key_index + 1
                text_index = int(key[key_index-1]) * 10
                key_index = key_index + increment
                try: text_index = text_index + int(key[key_index-1])
                except: pass
                text_index = text_index + 1
                increment = increment + 1
                if increment == 5: increment = 1
                plaintext = plaintext + intermediate_cyphertext[text_index-1]
                #try: plaintext = plaintext + intermediate_cyphertext[text_index-1]
                #except: pass
            urlVideo = plaintext
        except:
            ads  = "6037182945"
            str1 = "51%s-" % videoID
            inverted_str1 = str1[::-1]
            s = "".join([ads[int(n)] for n in inverted_str1[1:]])
            url  = "http://ztnr.rtve.es/ztnr/pub/%s/%s/%s/%s/%s" % (s[0],s[1],s[2],s[3],s)
            self.debug(u"Probando url:", url)
            xmldata = Descargar.doPOST("pydowntv.com", "/utils/cnR2ZV9yYW5kb21fNA/", {"encrypted":Descargar.get(url),"new":"ok"})
            try:
                self.debug(xmldata.replace(xmldata[xmldata.find("</quality>")+10:],""))
                xmltree = xml.etree.ElementTree.fromstring(xmldata.replace(xmldata[xmldata.find("</quality>")+10:],""))
                for node in xmltree.findall("./preset"):
                    if node.attrib.get('type') == "Alta":
                        for url in node.findall("./response/url"):
                            if url.attrib.get('provider') == "AKAMAI_STR-1030":
                                urlVideo = url.text
            except:
                urlVideo = re.findall("<url.*>(.*)</url>", xmldata)[0]



        
        if urlVideo != "":
            if not urlVideo.endswith(".mp4"): urlVideo = urlVideo.replace(urlVideo.split(".mp4")[1], "")
            url_video = urlVideo.replace("www.rtve.es", "media5.rtve.es").replace("iphonelive","mvod").replace("NGVA", "ngva").replace("GLESP","ngva").replace("mvodt.lvlt.rtve","mvod.lvlt.rtve").replace("resorces", "resources")
            
            titulo = sourceHTML.split("<title>")[1].split("</")[0].replace("RTVE.es", "").replace("-", "").strip()
            filename = titulo + ".mp4"
            filename = Utiles.formatearNombre(filename)

            try: url_img = sourceHTML.split("\"thumbnail\" content=\"")[1].split("\"")[0]
            except:
                try: url_img = re.findall('<link.*rel\=\"image_src\".*href\=\"(.*)\"' , sourceHTML)[0]
                except: url_img = re.findall('<meta.*name\=\"RTVE\.thumb_video\".*content\=\"(.*)\"',sourceHTML)[0]
        else:
            raise Error.GeneralPyspainTVsError("No se pudo encontrar el enlace de descarga")

        #TEMP FIX:
        #url_video = url_video.replace(url_video.split(".")[1], url_video.split(".")[1][:3])

        # -- Método 24 Mayo 2013 FIN
        
        desc = None
        try: #obtener descripción del video
            desc = Utiles.recortar(sourceHTML, "<meta name=\"description\" content=\"", "\"").strip()
        except:
            try:
                desc = Utiles.recortar(sourceHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
            except:
                try:
                   desc = Utiles.recortar(sourceHTML, "<meta itemprop=\"description\" content=\"", "\"").strip()
                except:
                    desc = u"Vídeos de Televión Española"
        
        # Comprobar si existe calidad FLV
        url_flv = url_video.replace("mp4", "flv")
        if Descargar.isReachableHead(url_flv):
            msgCalidad = u'''Este vídeo dispone de dos calidades. 
            Para los vídeos de RTVE, la mejor suele ser la que se presenta en formato FLV. 
            En los vídeos con más tiempo puede que el audio al principio no esté bien sincronizado 
            con el audio. Este problema será menos grave en el formato FLV llegándose incluso a 
            sincronizar totalmente pasados unos segundos.'''.encode('utf8')

            return {"exito" : True,
                    "num_videos" : 2,
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
                            "otros"     : "MP4",
                            "mensaje"   : msgCalidad
                            },
                            {
                            "url_video" : [url_flv],
                            "url_img"   : url_img,
                            "filename"  : [filename.replace(".mp4", ".flv")],
                            "tipo"      : "http",
                            "partes"    : 1,
                            "rtmpd_cmd" : None,
                            "menco_cmd" : None,
                            "url_publi" : None,
                            "otros"     : "FLV",
                            "mensaje"   : msgCalidad
                            }],
                    "titulos": [titulo,titulo],
                    "descs": [desc, desc]
                    }
        else:
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
