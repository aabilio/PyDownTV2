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
import urllib2

url_validas = ["mitele.es"]

class MiTele(Canal.Canal):
    '''
        Clase para manejar los vídeos de Mi Tele
    '''
    
    #URL_TIME  = "http://www.mitele.es/media/clock.php"
    #URL_TIME = "http://servicios.telecinco.es/tokenizer/clock.php"
    URL_TIME = "http://token.mitele.es/clock.php"
    
    #TOKENIZER = "/tokenizer/tk3.php"
    TOKENIZER = "/"
    
    #URL_POST = "token.mitele.es"
    URL_POST = "servicios.telecinco.es/tokenizer/tkjs.php"
    
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
        header = {
            "Referer": "http://www.mitele.es/series-online/aida/temporada-10/capitulo-219/",
            "Accept": "*/*",
            "Accept-Language": "es,en;q=0.8",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
            "Host": "token.mitele.es"
        }
        server_time = Descargar.get(self.URL_TIME).strip()

        toEncode = (server_time+";"+ID+";"+startTime+";"+endTime).replace(" ", "")
        self.debug("[DEBUG] server_time: %s" % server_time)
        self.debug(u"[DEBUG] toEncode: %s" % toEncode)
        self.debug(u"[DEBUG] Util URL: http://www.pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzI/%s" % (toEncode))

        data = Descargar.get("http://www.pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzI/%s" % (toEncode))
        
        # Datos actuales para el get
        get_args = data+"&id="+ID.replace(" ","")+"&startTime=0&endTime=0";
        # Datos antiguos para el POST
        post_args = {
                    'hash' : data,
                    'id' : ID.replace(" ",""),
                    'startTime' : '0',
                    'endTime': '0'
                    }

        self.debug(u"Token: %s" % post_args)
        
        try:
            header = {
                "Referer": "http://static1.tele-cinco.net/comun/swf/playerMitele.swf",
                "Accept": "*/*",
                "Origin": "http://static1.tele-cinco.net",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36", 
                "Accept-Language": "de,en;q=0.7,en-us;q=0.3", 
                "Content-type": "application/x-www-form-urlencoded",
                "Cookie": "s_cc=true;s_fid=7B0AC1148C6D6D16-0521A69344CCF613;s_ppv="+self.url+",49,49,1186;s_sq=[[B]];"
            }
            # Método antiguo, ahora utilizamos GET (guardamos POST para descubrir enlaces de mitele)
            #data = Descargar.doPOST("pydowntv.pydowntv.com", "/pydowntv/mitele2.php", post_args, doseq=True)
            
            # Devuelve enlaces de Telecinco
            #data = Descargar.get("http://token.mitele.es?hash="+get_args, withHeader=True, header=header)
            data = Descargar.get("http://pydowntv.pydowntv.com/pydowntv/mitele3.php?url=%s&referer=%s" % (urllib2.quote("http://token.mitele.es?hash="+get_args), urllib2.quote(self.url)))

        except Exception, e:
            raise Error.GeneralPyspainTVsError("mitele.es: Error en Tokenizer: "+e.__str__())

        if data is None:
            return None
        else:
            self.debug("[DEBUG] DATA:\n" + data)
            if data.find("<stream>") != -1 or data.find("Contenido no reproducible") != -1:
                #self.__mediasetSearch(html) # DEPRECATED

                newData = Descargar.get("http://www.pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzI/%s?method=a" % (toEncode))
                #rtmpinfo = Descargar.doPOST(self.URL_POST, tokenizer, {'hash':newData}, doseq=True)
                rtmpinfo = Descargar.doPOST("pydowntv.pydowntv.com", "/pydowntv/mitele2.php", {'hash':newData}, doseq=True)
                self.debug("NEW DATA:\n" + rtmpinfo)

                rtmpinfo = rtmpinfo.replace("&amp;", "&")
                rtmp_r   = "\""+ re.findall("\<stream\>(.*?)\<\/stream\>",rtmpinfo)[0]+"/" +"\""
                rtmp_y   = "\""+ re.findall("\<file.*>(.*?)\<\/file\>",rtmpinfo)[0] +"\""
                rtmp_a   = "\""+ rtmp_r.split("/")[-2] + "?" + rtmp_y.split("?")[1] #+"\""
                rtmp_u   = "\""+ rtmp_y.split("?")[1] #+"\""
                rtmp_s   = "\""+ 'http://static1.tele-cinco.net/comun/swf/playerMitele.swf' +"\""

                url = [rtmp_r, "-y", rtmp_y, "-a", rtmp_a, "-u", rtmp_u, "-s", rtmp_s]
            elif data.find("file") != -1:
                try:
                    url = data.split("<url><file>")[1].split("</file></url>")[0].replace("&amp;", "&").replace(" ", "")
                except IndexError:
                    url = data.split("<file geoblocked=\"true\">")[1].split("</file></url>")[0].replace("&amp;", "&").replace(" ", "")
            elif data.find("tokenizedUrl") != -1:
                url = data.split('"tokenizedUrl":"')[1].split('"')[0].replace(" ", "").replace("\/", "/")
            else:
                print "no entiendo lo que pone"
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

        if type(url) is list: # Comando RTMP
            _type = "rtmp"
            rtmpd_cmd = "rtmpdump -r " + " ".join(url) + " -o \"" + name + "\""
            url = "rtmp"+rtmpd_cmd.split("rtmp")[2].split('"')[0]
        else:
            rtmpd_cmd = None
            _type = "http"
            
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenida correctamente",
                "videos":[{
                        "url_video" : [url],
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : _type,
                        "partes"    : 1,
                        "rtmpd_cmd" : [rtmpd_cmd] if rtmpd_cmd is not None else None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit_vid.replace("'","")] if tit_vid is not None else None,
                "descs": [desc] if desc is not None else None
                }
        