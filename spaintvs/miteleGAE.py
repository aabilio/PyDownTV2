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

# Módulo MiTele

__author__="aabilio"
__date__ ="$17-oct-2012 19:21:30$"

import Canal
import Utiles
import Descargar
import Error

import xml.etree.ElementTree
import re

url_validas = ["mitele.es"]

class MiTele(Canal.Canal):
    '''
        Clase para manejar los vídeos de Mi Tele
    '''
    
    #URL_TIME  = "http://www.mitele.es/media/clock.php"
    URL_TIME = "http://servicios.telecinco.es/tokenizer/clock.php"
    #TOKENIZER = "/tokenizer/tk3.php"
    TOKENIZER = "/index.php"
    URL_POST = "token.mitele.es"
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    def __getUrl2down(self, ID, startTime, endTime, html):
        '''
            Tercer método implementado:
            
            TK3 - Pass de "M":
            ==================
            force_http -> 1
            hash -> encode(serverTime;id;startTime;endTime)
            id -> /url/url/url.mp4
            startTime -> 0
            endTime -> 0
        '''
        self.debug(u"Probando el que era el Método 3")
        tokenizer = self.TOKENIZER
        server_time = Descargar.get(self.URL_TIME).strip()
        toEncode = server_time+";"+ID+";"+startTime+";"+endTime
        data = Descargar.get("http://www.pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzI/%s" % (toEncode))
        post_args = {
                    'hash' : data,
                    'id' : ID.replace(" ",""),
                    'startTime' : '0',
                    'endTime': '0'
                    }
        self.debug(u"Token: %s" % post_args)
        
        try:
            #data = Descargar.doPOST(self.URL_POST, tokenizer, post_args, doseq=True)
            data = Descargar.doPOST("aabilio.hl161.dinaserver.com", "/pydowntv/mitele2.php", post_args, doseq=True)
        except Exception, e:
            raise Error.GeneralPyspainTVsError("mitele.es: Error en Tokenizer: "+e.__str__())

        if data is None:
            return None
        else:
            self.debug("DATA:\n" + data)
            if data.find("<stream>") != -1 or data.find("Contenido no reproducible") != -1: # FIXME: Este comandono funciona
                self.__mediasetSearch(html)
                
                #data = data.replace("&amp;", "&")
                #server = Utiles.recortar(data, "<stream>", "</stream>") + "/"
                #server = server.replace("rtmpe://", "http://")
                #server = server.replace("rtmpe://streaminggeo.mitele.es/","http://videosgeo.mitele.es") +"/"
                #play = Utiles.recortar(data, "mp4:", "</file>").replace("nvb", "vf").replace("nva","vu").replace("token", "h")
                #return server + Utiles.recortar(data, "mp4:", "</file>") + "&start=0"
                raise Error.GeneralPyspainTVsError("mitele.es: RTMP no soportado para el canal por ahora.")
                #R = data.split("<stream>")[1].split("</stream>")[0]
                #A = "\""+ "/".join(data.split("/")[4:]).split("</stream>")[0] +"\""
                #F = "\""+ "WIN 11,1,102,55" +"\""
                #W = "\""+ "http://static1.tele-cinco.net/comun/swf/playerMitele.swf" +"\""
                #P = "\""+ self._URL_recibida +"\""
                #Y = "\""+ "mp4:" + data.split("</file>")[0].split("mp4:")[1] +"\""
                #url = [R, "-a", A, "-f", F, "-W", W, "-p", P, "-y", Y]
            elif data.find("file") != -1:
                try:
                    url = data.split("<url><file>")[1].split("</file></url>")[0].replace("&amp;", "&").replace(" ", "")
                except IndexError:
                    url = data.split("<file geoblocked=\"true\">")[1].split("</file></url>")[0].replace("&amp;", "&").replace(" ", "")
            elif data.find("tokenizedUrl"):
                url = data.split('"tokenizedUrl":"')[1].split('"')[0].replace(" ", "").replace("\/", "/")
            else:
                return None
            return url

    def __mediasetSearch(self, html):
        mediasetchannel = re.findall('s.eVar3="(.*)"', html)[0]
        programa = re.findall('s.eVar7="(.*)"', html)[0]
        temporada = re.findall('s.eVar8=".* ([0-9].*)"', html)[0]
        capitulo = re.findall('s.eVar9=".* ([0-9].*)"', html)[0]
        
        if int(temporada)<10: temporada="0%s" % (temporada)
        if int(capitulo)<10: capitulo="0%s" % (capitulo)

        abuscar = urllib2.quote("%s T%sxC%s" % (programa, temporada, capitulo))
        search = "http://www.%s.es/buscador/?text=%s" % (mediasetchannel, abuscar)
        self.debug(u"Programa: %s" % programa)
        self.debug(u"Temporada: %s" % temporada)
        self.debug(u"Capitulo: %s" % capitulo)
        self.debug(u"Search... %s" % search)
        results = Descargar.get(search)
        self.debug(search)
        try:
            r=results.split('<h2 class="headline')[1].split('href="')[1].split('"')[0]
        except IndexError:
            raise Error.GeneralPyspainTVsError("mitele.es: RTMP no soportado para el canal por ahora.")
        mediasetLink = "http://www.%s.es%s" % (mediasetchannel, r)

        if mediasetchannel == "telecinco":
            from telecinco import Telecinco as newChannel
        elif mediasetchannel == "cuatro":
            from cuatro import Cuatro as newChannel
        else:
            raise Error.GeneralPyspainTVsError("mitele.es: RTMP no soportado para el canal por ahora.")
        channel = newChannel(mediasetLink)
        return channel.getInfo()

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
        
        tit_vid = None
        # Obtener HTML y XML:
        try:
            streamHTML = htmlBackup = Descargar.getHtml(self.url).decode('string-escape')
            html = streamHTML
            tit_vid = streamHTML.split("<title>")[1].split("<")[0]
            streamHTML = streamHTML.replace(" ", "")
            streamXML = Descargar.getHtml(streamHTML.split("{\"host\":\"")[1].split("\"")[0].replace("\/", "/"))
        except Exception, e:
            raise Error.GeneralPyspainTVsError("mitele.es: No se puede obenter enlaces: "+e.__str__())
        
        try:
            img = streamXML.split("<thumb><![CDATA[")[1].split("]")[0]
            if img.find("esArray") != -1 or img.find("esarray") != -1:
                img = html.split("class=\"videoEmbed\"")[1].split("<img src=\"")[1].split("\"")[0]
        except Exception, e:
            self.debug("No se puede obtener imagen: "+e.__str__())
            img = None
        try:
            publi = streamXML.split("<infoAds><url><![CDATA[")[1].split("]")[0]
            publi = publi if publi != "" else None
        except Exception, e:
            self.debug("No se puede obtener publi: "+e.__str__())
            publi = None
            
                                                                                               
        # Obtener ID y starTime, endTime:
        if streamXML.find("<rtmp") != -1:
            if streamXML.find("rtmp=\"false\"") != -1: # Igual que el normal
                    ID = (streamXML.split("<link start=")[1].split("</link>")[0]).split("\">")[1].split("<")[0]
            else:
                ID = streamXML.split("<rtmp")[1].split("<url><![CDATA[")[1].split("]")[0]
        else:
            # Mantengo este ID por compatibilidad:
            ID = (streamXML.split("<link start=")[1].split("</link>")[0]).split("\">")[1].split("<")[0]
        
        self.info(u"[INFO] ID: "+ID)

        startTime = '0' if streamXML.find("<link start=\"") == -1 else streamXML.split("<link start=\"")[1].split("\"")[0]
        endTime = '0' if streamXML.find("end=\"") == -1 else streamXML.split("end=\"")[1].split("\"")[0]
        self.debug(u"startTime: %s\n[DEBUG] endTime: %s" % (startTime, endTime))
        
        # Dejo el que era el método 3
        url = self.__getUrl2down(ID, startTime, endTime, htmlBackup)
        if url is None:
            raise Error.GeneralPyspainTVsError("mitele.es: No funciona el procedimiento.")
        
        # Obtener nombre:
        if type(url) == str:
            tit_vid = name = streamHTML.split("<title>")[1].split("<")[0] + "." + url.split(".")[-1].split("?")[0]
        else: # De momento: suponemos que son mp4.
            tit_vid = name = streamHTML.split("<title>")[1].split("<")[0] + ".mp4"
        
        try:
            xmltree = xml.etree.ElementTree.fromstring(streamXML)
            video_title = xmltree.find('./video/info/title').text.encode('utf8')
            video_sub_title = xmltree.find('./video/info/sub_title').text.encode('utf8')
            video_category = xmltree.find('./video/info/category').text.encode('utf8')
            video_sub_category = xmltree.find('./video/info/subcategory').text.encode('utf8')

            tit_vid = name = "%s (%s) - %s - %s" % (video_title, video_sub_title, video_category, video_sub_category)
        except:
            name = name.replace("VERPROGRAMAS", "").replace("Veronline", "")
            name = name.replace("VERSERIES", "").replace("Veronline", "")
            tit_vid = tit_vid.replace("VER PROGRAMAS", "").replace("Ver online", "")
            tit_vid = tit_vid.replace("VER SERIES", "").replace("Ver online", "").replace("|", "").strip()

        try:
            name = Utiles.formatearNombre(name + ".mp4")
        except:
            name = "Video_de_mitele.mp4"
        
        desc = None        
        try:
            desc = htmlBackup.split("<div class=\"Destacado-text\">")[1].split("<p class=\"text\">")[1].split("</p>")[0]
            #desc = Utiles.descriptionFormat(Utiles.recortar(htmlBackup, "\"post_content\":\"", "\"").strip())
        except:
            desc = tit_vid if tit_vid is not None else None
            
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenida correctamente",
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
                "titulos": [tit_vid] if tit_vid is not None else None,
                "descs": [desc] if desc is not None else None
                }
        