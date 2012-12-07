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

import aes

url_validas = ["mitele.es"]

class MiTele(Canal.Canal):
    '''
        Clase para manejar los vídeos de Mi Tele
    '''
    
    #URL_TIME  = "http://www.mitele.es/media/clock.php"
    URL_TIME = "http://servicios.telecinco.es/tokenizer/clock.php"
    TOKENIZER = "/tokenizer/tk3.php"
    PASSWD = "xo85kT+QHz3fRMcHMXp9cA"
    URL_POST = "servicios.mitele.es"
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    def __getUrl2down(self, ID, startTime, endTime):
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
        AES = aes.AES() 
        tokenizer = self.TOKENIZER
        passwd = self.PASSWD
        server_time = Descargar.get(self.URL_TIME).strip()
        toEncode = server_time+";"+ID+";"+startTime+";"+endTime
        data = AES.encrypt(toEncode, passwd, 256)
        post_args = {
                    'hash' : data,
                    'id' : ID,
                    'startTime' : '0',
                    'endTime': '0'
                    }
        
        try:
            #data = Descargar.doPOST(self.URL_POST, tokenizer, post_args, doseq=True)
            data = Descargar.doPOST("linfox.es", "/pydowntv/mitele.php", post_args, doseq=True)
        except Exception, e:
            raise Error.GeneralPyspainTVsError("mitele.es: Error en Tokenizer: "+e.__str__())

        if data is None:
            return None
        else:
            self.debug("DATA:\n" + data)
            if data.find("<stream>") != -1: # FIXME: Este comandono funciona
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
                    url = data.split("<url><file>")[1].split("</file></url>")[0].replace("&amp;", "&")
                except IndexError:
                    url = data.split("<file geoblocked=\"true\">")[1].split("</file></url>")[0].replace("&amp;", "&")
            else:
                return None
            return url

    def getInfo(self):
        '''
            Devuelve toda la información asociada a la URL recibida, de la siguiente forma:
            {
             "exito"     : bool,  <-- True (si se han obtenido videos) (bool)
             "num_video" : int,   <-- Número de vídeos obtenidos (int)
             "mensaje"   : u"" ,  <-- Mensajes de la API (ej.: El vídeo no ha sido encontrado ["exito": False]) (unicode)
             "videos"    :  [{ (dict)
                            "url_video" : [],   <-- Url de descarga de vídeo (list)
                            "url_img"   : "",   <-- Url de la miniatura del video (str/unicode)
                            "filename"  : [],   <-- Nombre de las partes para guardar en disco (list)
                            "tipo"      : "",   <-- http, rtmp[e,..], mms, ... (str/unicode)
                            "partes"    : int,  <-- Número de partes que tiene el vídeo (int)
                            "rtmpd_cmd" : [],   <-- Comando rtmpdump (si tipo == rtmp) sino None (list)
                            "menco_cmd" : [],   <-- Comando mencoder (Si tipo == rtmp) sino None (list)
                            "url_publi" : "",   <-- Url del vídeo de publicidad asociado al vídeo (str/unicode)
                            "otros"     : [],   <-- Lista donde se pueden pasar cosas opcionales (list)
                            "mensaje"   : ""    <-- Mensajes de la API (str/unicode)
                            }], <-- Debe ser una lista de tamaño "num_videos" (list)
             "titulos"   : [u""] <-- Titulos de los videos (list)
            }
            
            Los valores que no se rellenen, deberán devolver None.
            La clave "exito" es obligatoria, sino se puede encontrar el vídeo se puede devolver directamente:
            {
            "exito": False,
            "mensaje": "No se pudo descargar el video"  
            }
            
            "videos" y "mesajes" deben ser listas de cadenas (si no son None)
            "url_video", "titulo", "rtmp_cmd", "menco_cmd" (de "videos") deben ser listas de cadenas (si no son None)
        '''
        
        tit_vid = None
        # Obtener HTML y XML:
        try:
            streamHTML = Descargar.getHtml(self.url)
            tit_vid = streamHTML.split("<title>")[1].split("<")[0]
            streamHTML = streamHTML.replace(" ", "")
            streamXML = Descargar.getHtml(streamHTML.split("{\"host\":\"")[1].split("\"")[0].replace("\/", "/"))
        except Exception, e:
            raise Error.GeneralPyspainTVsError("mitele.es: No se puede obenter enlaces: ", e)
        
        try:
            img = streamXML.split("<thumb><![CDATA[")[1].split("]")[0]
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
        url = self.__getUrl2down(ID, startTime, endTime)
        if url is None:
            raise Error.GeneralPyspainTVsError("mitele.es: No funciona el procedimiento.")
        
        # Obtener nombre:
        if type(url) == str:
            name = streamHTML.split("<title>")[1].split("<")[0] + "." + url.split(".")[-1].split("?")[0]
        else: # De momento: suponemos que son mp4.
            name = streamHTML.split("<title>")[1].split("<")[0] + ".mp4"
        if name:
            name = Utiles.formatearNombre(name)
        
        name = name.replace("VERPROGRAMAS", "").replace("Veronline", "")
        name = name.replace("VERSERIES", "").replace("Veronline", "")
        tit_vid = tit_vid.replace("VER PROGRAMAS", "").replace("Ver online", "")
        tit_vid = tit_vid.replace("VER SERIES", "").replace("Ver online", "")
            
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
                "titulos": [tit_vid] if tit_vid is not None else None
                }
        