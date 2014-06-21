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

# Se establece la Clase del objeto a3: que maneja los métodos para descargar
# los vídeos de la página de Antena 3 Televisón:

__author__="aabilio"
__date__ ="$12-oct-2012 11:03:38$"

import re
try: import simplejson as json
except: import json
from hashlib import md5 
from time import sleep
import xml.etree.ElementTree
import urllib2
import urllib
from cookielib import CookieJar

import Canal
import Descargar
import Utiles
import Error


url_validas = ["antena3.com", "lasexta.com", "lasextadeportes.com", "lasextanoticias.com", "atresplayer.com"]

class GrupoA3(Canal.Canal):
    '''
        Clase para manejar los vídeo del grupo Antena3
    '''
    
    URL_DE_ANTENA3  = "http://www.antena3.com/"
    URL_DE_LASEXTA = "http://www.lasexta.com/"
    URL_DE_DESCARGA = "http://desprogresiva.antena3.com/"
    URL_DE_DESCARGA_LA_SEXTA = "http://deslasexta.antena3.com/"
    URL_DE_F1 = "http://www.antena3.com/gestorf1/xml_visor/"
    URL_VISOR_F1 = "http://www.antena3.com/gestorf1/static_visor/"
    P = "http://aabilio.me/p/browse.php?f=norefer&u="

    URL_API_TIME = "http://servicios.atresplayer.com/api/admin/time"
    URL_EPISODE_INFO = "http://servicios.atresplayer.com/episode/get?episodePk="

    '''
        Clase para manejar los vídeos de la RTVE (todos).
    '''
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    # Métodos propios del canal, start the party!
    # Attributos disponibles:
    #    - self.url (url recibida)
    #    - self.opcs (diccionario de opciones) Ver Módulo Canal "_default_opcs" para opciones
    # Métodos disponibles de clase Canal:
    #    - self.log() para mostrar por pantalla (está disponible si self.opcs["log"] es True)
    #    - self.debug() mostrar información de debug (está disponible si self.opcs["debug"] es True)
    # Comunicación de errores con nivel de aplicación:
    #    - lanzar la excepción: raise Error.GeneralPyspainTVsError("mensaje")
    
    def __getUrlDescarga(self, xml):
        try:
            urlDeDescarga = Utiles.recortar(xml, "<urlHttpVideo><![CDATA[", "]]></urlHttpVideo>")
        except:
            urlDeDescarga = self.URL_DE_DESCARGA
        return urlDeDescarga

    def __modoSalonNuevo(self, streamXML):
        '''Nuevos vídeos con extensión .m4v'''
        self.log(u"[INFO] Modo Salón")
        self.log(u"[INFO] Nuevos vídeos en formato f4v")

        self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)

        # Soporte para una parte OFF (desde hace tiempo no se detecta un 000.mp4)
        #if streamXML.find("000.f4v"):
        #    url2down1 = self.URL_DE_DESCARGA + streamXML.split("<archivo><![CDATA[")[1].split("]")[0]
        #else:
        #    url2down1 = self.URL_DE_DESCARGA + \
        #        streamXML.split("<archivo><![CDATA[")[1].split("001.f4v]]></archivo>")[0] + "000.f4v"
        
        #if Descargar.isReachable(url2down1): # Vídeo en una parte
        #    url2down = url2down1
        #    name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + ".f4v"
        #else: # Vídeo en varias partes
        #self.info(u"[!!!]  No se puede encuentra el vídeo en un archivo (000.m4v)")
        self.info(u"[INFO] El vídeo consta de varias partes")
        parts = re.findall("\<archivo\>\<\!\[CDATA\[.*\.f4v\]\]\>\<\/archivo\>", streamXML)
        if parts:
            name1 = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0]
            url2down = []
            name = []
            for i in parts:
                url2down.append(self.URL_DE_DESCARGA + i.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0])
                name.append(name1 + "_" + i.split("]")[0].split("/")[-1])
        else:
            raise Error.GeneralPyspainTVsError("Grupo Antena 3. No se encuentra ninguna parte de contenido.")
        return [url2down,  name]
    
    def __modoSalon(self, streamHTML):
        #TODO: Poner cada Canal su URL, no solo a todos la de antena 3 ;)
        self.log(u"[INFO] Modo Salón")
        if streamHTML.find("so.addVariable(\"xml\"") != -1:
            streamXML = \
            Descargar.getHtml(self.URL_DE_ANTENA3 + streamHTML.split("so.addVariable(\"xml\",\"")[1].split("\"")[0])
        elif streamHTML.find("player_capitulo.xml='") != -1:
            streamXML = \
            Descargar.getHtml(self.URL_DE_ANTENA3 + streamHTML.split("player_capitulo.xml='")[1].split("'")[0])
        else:
            if streamHTML.find("<div class=\"premium\">") != -1: 
                raise Error.GeneralPyspainTVsError(u"PyDownTV no acepta la descarga de contenidos premium de las cadenas.")
            raise Error.GeneralPyspainTVsError(u"Grupo Antena 3. No se encuentra XML.")
        
        self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
        # Comprobar aquí si se puede descargar 000.mp4:
        if streamXML.find(".mp4") != -1:
            tipo = ".mp4"
            #url2down1 = self.URL_DE_DESCARGA + \
            #    streamXML.split("<archivo><![CDATA[")[1].split("001.mp4]]></archivo>")[0] + "000.mp4"
        elif streamXML.find(".flv") != -1:
            tipo = ".flv"
            #url2down1 = self.URL_DE_DESCARGA + \
            #    streamXML.split("<archivo><![CDATA[")[1].split("001.flv]]></archivo>")[0] + "000.flv"
        elif streamXML.find(".f4v") != -1:
            [url2down, name] = self.__modoSalonNuevo(streamXML)
            return [url2down, name]
        else:
            raise Error.GeneralPyspainTVsError("Grupo Antena 3. No se encuentra mp4, f4v ni flv")
        
        #if Descargar.isReachable(url2down1): # Vídeo completo en una parte
        #    url2down = url2down1
        #    name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + tipo
        #else: # Vídeo en varias partes
        #self.info(u"[!!!]  No se puede encuentra el vídeo en un archivo (000.mp4)")
        self.info(u"[INFO] El vídeo consta de varias partes")
        parts = re.findall("\<archivo\>\<\!\[CDATA\[.*"+tipo+"\]\]\>\<\/archivo\>", streamXML)
        if parts:
            name1 = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0]
            url2down = []
            name = []
            for i in parts:
                url2down.append(self.URL_DE_DESCARGA + i.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0])
                name.append(name1 + "_" + i.split("]")[0].split("/")[-1])
        else:
            raise Error.GeneralPyspainTVsError(u"Grupo Antena 3. No se encuentra niguna parte de contenido.")
        return [url2down,  name]
    
    def __modoNormalConURL(self,  streamHTML):
        url2down = streamHTML.split(".seoURL='")[1].split("'")[0]
        if not Descargar.isReachable(url2down): # A veces el vídeo de .seoURL da NOT FOUND!
            xmlURL = Utiles.recortar(streamHTML, ".xml=\'", "\'")
            streamXML = Descargar.getHtml(self.URL_DE_ANTENA3 + xmlURL)
            self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
            url2down =  self.URL_DE_DESCARGA + \
            streamXML.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0]
            name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + ".mp4"
            return [url2down, name]
        url2down = url2down.replace("deslasexta", "desprogresiva")
        try: # Parece que a veces aunque en el código aparezca el html, este no existe..
            name = Descargar.getHtml(self.URL_DE_ANTENA3 + streamHTML.split(".xml='")[1].split("'")[0]).split("<nombre><![CDATA[")[1].split("]]>")[0] + ".mp4"
        except:
            name = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip() + ".mp4" 
        return [url2down,  name]
    
    def __modoNormalUnaParte(self, streamHTML):
        xmlURL = streamHTML.split("A3Player.swf?xml=")[1].split("\"")[0]
        streamXML = Descargar.getHtml(xmlURL)
        self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
        url2down =  self.URL_DE_DESCARGA + \
        streamXML.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0]
        name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + ".mp4"
        return [url2down, name]
    
    def __modoNormalVariasPartes(self, streamHTML):
        url2down = []
        name = []
        # Delimitamos la parte del carrusel (funcionará para todos??)
        streamHTML = streamHTML.split("<a title=\"Video Anterior\"")[1].split("<a title=\"Video Siguiente\"")[0]
        partes = len(streamHTML.split("<img title="))-1
        streamPARTES = streamHTML.split("<img title=")[1:]
        self.log(u"[INFO] Número de partes:", str(partes))
        
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        video = {
                "url_video" : [],
                "url_img"   : None,
                "filename"  : [],
                "tipo"      : "http",
                "partes"    : 0,
                "rtmpd_cmd" : None,
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
        
        for i in streamPARTES:
            video = {
                "url_video" : [],
                "url_img"   : None,
                "filename"  : [],
                "tipo"      : "http",
                "partes"    : 0,
                "rtmpd_cmd" : None,
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
            ret["num_videos"] += 1
            ret["titulos"].append(i.split("\"")[1].split("\"")[0])
            ret["descs"].append(i.split("\"")[1].split("\"")[0])
            
            xmlURL = self.URL_DE_ANTENA3 + i.split("rel=\"/")[1].split("\"")[0]
            #print xmlURL
            streamXML = Descargar.getHtml(xmlURL)
            self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
            
            video["url_video"].append(self.URL_DE_DESCARGA + streamXML.split("<archivo><![CDATA[")[1].split("]")[0])
            video["url_img"] = self.URL_DE_ANTENA3+"clipping"+streamXML.split("<archivo><![CDATA[clipping")[1].split("]")[0]
            video["filename"].append(i.split("\"")[1].split("\"")[0] + '.mp4')
            video["partes"] = 1
            ret["videos"].append(video)
            
            #url2down.append(self.URL_DE_DESCARGA + streamXML.split("<archivo><![CDATA[")[1].split("]")[0])
            #ext = streamXML.split("<archivo><![CDATA[")[1].split("]")[0].split('.')[-1]
            #name.append(i.split("\"")[1].split("\"")[0] + '.' + ext)   
        
        return ret

    def normalNuevoMultiple(self, xmls):
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        cont = 0
        for xml_ in xmls:
            video = {
                    "url_video" : [],
                    "url_img"   : None,
                    "filename"  : [],
                    "tipo"      : "http",
                    "partes"    : 0,
                    "rtmpd_cmd" : None,
                    "menco_cmd" : None,
                    "url_publi" : None,
                    "otros"     : None,
                    "mensaje"   : None
                    }

            sxml = Descargar.get(xml_)  
            xmltree = xml.etree.ElementTree.fromstring(sxml)
            
            url_desc = xmltree.find('./media/asset/files/videoSource').text.encode('utf8')
            url_img = xmltree.find('./media/asset/files/background').text.encode('utf8')

            ret["num_videos"] += 1
            ret["titulos"].append(xmltree.find('./media/asset/info/art/name').text.encode('utf8'))
            ret["descs"].append(xmltree.find('./media/asset/info/art/description').text.encode('utf8'))
            
            video["url_video"].append(url_desc)
            video["url_img"] = url_img
            #print cont, ":", ret["titulos"][cont]
            video["filename"].append(Utiles.formatearNombre(ret["titulos"][cont])+".mp4")
            video["partes"] = 1
            ret["videos"].append(video)

            cont += 1

        return ret

    def normalMultiple(self, xmls):
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        cont = 0
        for xml in xmls:
            video = {
                    "url_video" : [],
                    "url_img"   : None,
                    "filename"  : [],
                    "tipo"      : "http",
                    "partes"    : 0,
                    "rtmpd_cmd" : None,
                    "menco_cmd" : None,
                    "url_publi" : None,
                    "otros"     : None,
                    "mensaje"   : None
                    }

            sxml = Descargar.get(xml)  
            url_desc = self.__getUrlDescarga(sxml)
            url_img = re.findall("<urlImg><!\[CDATA\[(.*)\]\]></urlImg>", sxml)[0]

            ret["num_videos"] += 1
            ret["titulos"].append(re.findall("<nombre><!\[CDATA\[(.*)\]\]></nombre>", sxml)[0])
            ret["descs"].append(re.findall("<descripcion><!\[CDATA\[(.*)\]\]></descripcion>", sxml)[0])
            
            video["url_video"].append(url_desc+re.findall("<archivo><!\[CDATA\[(.*\.mp4)\]\]></archivo>", sxml)[0])
            video["url_img"] = url_img+re.findall("<archivo><!\[CDATA\[(.*\.jpg)\]\]></archivo>", sxml)[0]
            #print cont, ":", ret["titulos"][cont]
            video["filename"].append(Utiles.formatearNombre(ret["titulos"][cont]))
            video["partes"] = 1
            ret["videos"].append(video)

            cont += 1

        return ret
    
    def __modoF1(self, streamHTML):#TODO: ¡¡¡Acabar esta función para devolver todos los videos y sus partes!!!
        '''
           <param value="_urlData=http://www.antena3.com/gestorf1/swf/player_hitos/xml/data.xml&_image=http://www.antena3.com/gestorf1/pictures/361/361/malasia-portada_crop1.png&_id_list=1405&_promo1=http://www.smartadserver.com/call/pubx/15272/241149/4654/S/&_promo2=http://www.smartadserver.com/call/pubx/15272/241148/4654/S/" name="flashVars">
        '''
        streamHTML = Descargar.getHtmlUtf8(self.url)
        # Qué vídeo:
        streamVids = streamHTML.split("<ul class=\"a3_gp_visor_menu\">")[1].split("</ul>")[0].replace("\t", "")
        streamVids = streamVids.split("<li>")[1:]
        
        desc = None        
        try:
            desc = Utiles.recortar(streamHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
        except:
            desc = None
        
        #self.debug(streamVids)
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        
        v = -1
        for i in streamVids: #todos los vídeos con todas sus partes
            video = {
                "url_video" : [],
                "url_img"   : None,
                "filename"  : [],
                "tipo"      : "http",
                "partes"    : 0,
                "rtmpd_cmd" : None,
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
            v+=1
            streamVid = streamVids[v]
            streamVidUrl = self.URL_DE_ANTENA3 + streamVid.split("href=\"")[1].split("\"")[0]
            self.debug(u"URL Video: " + streamVidUrl)
            streamHTML = Descargar.getHtml(streamVidUrl)
            
            #Partes
            id_list = streamHTML.split("_id_list=")[1].split("&")[0]
            listXMLurl = self.URL_DE_F1 + id_list + "_playlist.xml"
            self.debug(u"URL XML list: " + listXMLurl)
            listxml = Descargar.getHtml(listXMLurl)
            video["url_img"] = listxml.split("<picture>")[1].split("</picture>")[0].strip()
            listxml = listxml.split("<video>")[1:]
            #print listxml
            for b in listxml:
                video["partes"] += 1
                #video["mensaje"] = unicode(i.split(">")[1].split("<")[0].capitalize())
                endurl = b.split("<url>")[1].split("<")[0]
                #video["url_video"].append(endurl.replace(endurl.split("mp_")[0],"http://desprogresiva.antena3.com/"))
                video["url_video"].append(endurl.replace(endurl.split("mp_")[0],self.URL_DE_DESCARGA_LA_SEXTA))
                ext = "." + video["url_video"][-1].split(".")[-1]
                tit = b.split("<title>")[1].split("<")[0] + ext
                tit = Utiles.formatearNombre(tit)
                video["filename"].append(tit)
                
            ret["titulos"].append(unicode(i.split(">")[1].split("<")[0].capitalize()).encode('utf8'))
            ret["videos"].append(video)
            ret["num_videos"] += 1
            ret["descs"].append(unicode(desc).encode('utf8'))

        return ret

    def __get(self, url):
        p = "http://www.gmodules.com/ig/proxy?url="
        url = p+url
        self.debug(unicode(url))
        return Descargar.get(url)

    def __getQ(self, url):
        #q = self.__get(url)
        q = Descargar.get(url)
        self.debug(unicode(q))
        q = re.findall('BANDWIDTH=([0-9]*).*RESOLUTION=([0-9x]*)|BANDWIDTH=([0-9]*)', q)
        q = [filter(None, n) for n in q]
        qq = []
        for i in q:
            if len(i) < 2:
                i += ('',)
            if i[0] == "1973000":
                tmp = ("2225", i[1])
            else:
                tmp = (str((int(i[0])/100000)*100), i[1])
            qq.append(tmp)
        self.debug(unicode(qq))
        return qq

    def __getApiMobileUrl(self, episode):
        return Descargar.get("http://pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzE/%s" % (episode))
        #header = {"User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"}
        #return Descargar.getHtmlHeaders("http://www.pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzE/%s" % (episode), header=header)
    def __getApiMobileUrl2(self, episode):
        return Descargar.get("http://pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzM/%s" % (episode))
        #header = {"User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"}
        #return Descargar.getHtmlHeaders("http://www.pydowntv.com/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzM/%s" % (episode), header=header)

    def atresplayer_mobile_login(self, url, formdata):
        self.debug(u"Legeando en atresplayer") #Login
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [("User-Agent","Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"),("Referer", "http://www.atresplayer.com/")]
        data_encoded = urllib.urlencode(formdata)
        response = opener.open(url, data_encoded)
        self.debug(u"Comprobando login en atresplayer") #Check Login:
        opener.addheaders = [("Accept","application/json"),("User-Agent","Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"),("Referer", "http://www.atresplayer.com/")]
        response = opener.open("http://servicios.atresplayer.com/connected")
        content = json.loads(response.read())
        if content["connected"]:
            self.debug(u"Login correcto en atresplayer")
            return cj
        else: raise Error.GeneralPyspainTVsError(u"Usuario y/o contraseña incorrecta")

    def atresplayer_mobile(self):
        #stream = self.__get(self.url)
        stream = Descargar.get(self.url)
        episode = re.findall('episode="(.*)">', stream)[0]
        header = {"Accept":"application/json"}
        self.debug("http://servicios.atresplayer.com/episode/get?episodePk="+episode)
        j = json.loads(Descargar.getHtmlHeaders("http://servicios.atresplayer.com/episode/get?episodePk="+episode, header=header))

        if j['type'] == "FREE":
            url = Utiles.url_fix(self.__getApiMobileUrl2(episode))
            header = {"User-Agent":"Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J)"}
            data = json.loads(Descargar.getHtmlHeaders(url.replace("https://", "http://"), header=header))
            self.debug(u"DATA:\n%s" % data)
            try:
                url2down = data['resultObject']['es']
                if url2down is None: raise Error.GeneralPyspainTVsError(u"No se ha podido obtener el enlace del vídeo")
                #url2down = url.replace("https://", "http://")
            except:
                raise Error.GeneralPyspainTVsError(unicode(jj['resultDes']))
        else:
            if not self.opcs["a3user"] or not self.opcs["a3pass"]:
                raise Error.GeneralPyspainTVsError(u"No tienes permisos para acceder al contenido. Proporciona tu usuario y contraseña para volver a intentarlo (en la web: botón de opciones arriba a la izquierda).")
            cj = self.atresplayer_mobile_login("http://servicios.atresplayer.com/j_spring_security_check", {"j_username":self.opcs["a3user"],"j_password":self.opcs["a3pass"]})
            apiUrl = Utiles.url_fix(self.__getApiMobileUrl2(episode)).replace("https://","http://")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [("Accept","application/json"),("User-Agent","Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"),("Referer", "http://www.atresplayer.com/")]
            response = opener.open(apiUrl)
            content = json.loads(response.read())
            self.debug(u"CONTENT:\n%s" % content)
            url2down = content['resultObject']['es']
            if url2down is None: raise Error.GeneralPyspainTVsError(u"No se ha podido obtener el enlace del vídeo")
            if not url2down: raise Error.GeneralPyspainTVsError(unicode(content['resultDes']))

        # if j['type'] == "REGISTER":
        #     url = Utiles.url_fix(self.__getApiMobileUrl2(episode))
        #     #header = {"User-Agent":"Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J)"}
        #     #data = json.loads(Descargar.getHtmlHeaders(url.replace("https://", "http://"), header=header))
        #     try:
        #         #url2down = data['resultObject']['es']
        #         url2down = url.replace("https://", "http://")
        #     except:
        #         raise Error.GeneralPyspainTVsError(unicode(jj['resultDes']))
        # elif j['type'] == "FREE": # TEMP FIX
            
        # else:
        #     url = Utiles.url_fix(self.__getApiMobileUrl2(episode).replace("https://", "http://"))
        #     self.debug(unicode(url))
        #     #jj = json.loads(self.__get(Utiles.url_fix(url)))
        #     jj = json.loads(Descargar.get(Utiles.url_fix(url)))
        #     try:
        #         url2down = jj['resultObject']['es']
        #     except:
        #         raise Error.GeneralPyspainTVsError(unicode(jj['resultDes']))

        #     if url2down is None:
        #         raise Error.GeneralPyspainTVsError(u"[Atresplayer] No se han podido obtener enlaces para URL proporcionada")

            

        title = u"%s %s".encode('utf-8') % (j['titleSection'].encode('utf-8'), j['titleDetail'].encode('utf-8'))
        desc = unicode(j['seoDescription']).encode('utf-8')
        name = u"VideoAtresPlayer.mp4"
        img = j['urlImage'].replace(".jpg", "06.jpg")

        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url2down] if type(url2down) != list else url2down,
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if type(name) != list else name,
                        "tipo"      : "http",
                        "partes"    : 1 if type(url2down) != list else len(url2down),
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [title] if title is not None else None,
                "descs": [desc] if desc is not None else None
                }


    def atresplayer(self):
        getEpisodeUrl = "http://servicios.atresplayer.com/episode/get?episodePk="
        locationHTTP2down = "desprogresiva.antena3.com/"
        #locationHTTP2down = "tcdn.desprogresiva.antena3.com/"
        locationRTMP2down = "a3premiumtkfs.fplive.net/"
        locationQ = "deswowa3player.antena3.com/"

        # Get episode info
        streamHTML = Descargar.get(self.url)
        episode = re.findall('episode="(.*)">', streamHTML)[0]
        header = {"Accept":"application/json"}
        j = json.loads(Descargar.getHtmlHeaders("http://servicios.atresplayer.com/episode/get?episodePk="+episode, header=header))
        #j = json.loads(self.__get("http://servicios.atresplayer.com/episode/get?episodePk="+episode))
        wowzaPath = j['wowzaPath'].replace("//", "/")

        # Flags
        isGeo = j['geolocked']
        isRtmp = True if wowzaPath.find("a3player") != -1 else False

        hasOffline = True if j['offlineDownload'] else False
        hasHD = True if j['hd'] else False
        hasVO = True if j['vo'] else False
        hasDRM = True if j['drmEncrypted'] else False
        hasDrm = True if j['drm'] else False

        protocol = "rtmp" if isRtmp else "http"
        geo = "geo" if isGeo else ""
        sigra = "sigra" if j['sigra'] else "000"
        smil = "mp4" if j['sigra'] else "smil"
        playlist = sigra if j['sigra'] else "es"
        vsng = "vcg" if isGeo else "vsg"
        ext = "."+j['fileExtension'] if j.has_key('fileExtension') else ".mp4"
        assetsN = re.findall("a3player(.)\/", wowzaPath)[0] if isRtmp else re.findall("assets(.)\/", wowzaPath)[0]


        if isRtmp:
            if isGeo:
                wowzaPath = wowzaPath.replace("a3player%s/geo/" % assetsN, "assets%s/" % assetsN)
            else:
                wowzaPath = wowzaPath.replace("a3player%s/nogeo/" % assetsN, "assets%s/" % assetsN)
                wowzaPath = wowzaPath.replace("a3player%s/" % assetsN, "assets%s/" % assetsN)
            
            #rtmpd_cmd = "rtmpdump -r rtmp://%s%s%sa3premiumtk/%s/%s.mp4 -o %s" % (geo, locationRTMP2down, geo, wowzaPath, sigra, name)
            url2down = "http://%s%s%s%s%s" % (geo, locationHTTP2down, wowzaPath, sigra, ext)
            title = u"%s %s".encode('utf-8') % (j['titleSection'].encode('utf-8'), j['titleDetail'].encode('utf-8'))
            protocol = "http"
        else:
            # Obtener distintas calidades
            try:
                urlQ = "http://%s%s%s/_definst_/%s:%s%s.%s/playlist.m3u8" % (geo, locationQ, vsng, smil, wowzaPath, playlist, smil)
                Q = self.__getQ(urlQ)
            except:
                Q = [('600', '720x404'), ('900', '720x404'), ('1300', '720x404'), ('1500', '1280x720'), ('2225', '1280x720')]

            if len(Q) > 1:
                url2down = []
                title = []
                for q in Q:
                    w = "720" if not q[1] else q[1].split('x')[0]
                    ww = "720x404" if not q[1] else q[1]
                    k = q[0]
                    tmp = "http://%s%s%svideo_%s_%sk_es.mp4" % (geo, locationHTTP2down, wowzaPath, w, k) # TODO: include VO
                    url2down.append(tmp)
                    title.append(u"%s %s [%s (%sk)]".encode('utf-8') % (j['titleSection'].encode('utf-8'), j['titleDetail'].encode('utf-8'), ww.encode('utf-8'), k.encode('utf-8')))
            else:
                url2down = "http://%s%s%svideo_%s_%sk_es.mp4" % (geo, locationHTTP2down, wowzaPath, Q[1], Q[0]) # TODO: include VO
                title = u"%s %s [%s (%sk)]".encode('utf-8') % (j['titleSection'].encode('utf-8'), j['titleDetail'].encode('utf-8'), Q[i][1].encode('utf-8'), Q[i][0].encode('utf-8'))

        desc = [unicode(j['seoDescription']).encode('utf-8')]*len(url2down)
        name = u"VideoAtresPlayer.mp4"
        img = j['urlImage'].replace(".jpg", "06.jpg")

        url2down = [url2down] if type(url2down) is not list else url2down
        videos = []
        for i in range(len(url2down)):
            qString = None if isRtmp else u"RESOLUTION: %s // BANDWIDTH: %s" % (Q[i][1].encode('utf-8'), Q[i][0].encode('utf-8')) or None
            tmp = {
                    "url_video" : [url2down[i]],
                    "url_img"   : img if img is not None else None,
                    "filename"  : [name] if type(name) != list else name,
                    "tipo"      : protocol,
                    "partes"    : 1,
                    "rtmpd_cmd" : [rtmpd_cmd] if protocol == "rtmp" else None,
                    "menco_cmd" : None,
                    "url_publi" : None,
                    "otros"     : qString or None,
                    "mensaje"   : u"Puede que alguna calidad no esté disponible".encode('utf-8')
                    }
            videos.append(tmp)



        return {"exito" : True,
                "num_videos" : len(url2down),
                "mensaje"   : u"URL obtenido correctamente",
                "videos": videos,
                "titulos": [title] if type(title) != list  else title,
                "descs": [desc] if type(desc) != list  else title
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

        img = None
        # print "[+] Procesando descarga"
        streamHTML = Descargar.getHtml(self.url)
        if self.url.find("atresplayer.com/") != -1:
            return self.atresplayer_mobile()
        elif self.url.find(".com/videos/") != -1: # Modo Salón
            try:
                img = self.URL_DE_ANTENA3 + Utiles.qe(streamHTML).split("player_capitulo.poster=\'/")[1].split("\'")[0]
            except:
                if streamHTML.find("<div class=\"premium\">") != -1: 
                    raise Error.GeneralPyspainTVsError(u"PyDownTV no acepta la descarga de contenidos premium de las cadenas.")
            url2down, name = self.__modoSalon(streamHTML)
        else: # Otro vídeos (No modo salón)
            self.log(u"[INFO] Vídeo normal (no Modo Salón)")
            # EN PRUEBAS (nuevo modo normal) (17/05/2014)  #######################################
            xmls = re.findall(".*(http.*\/videosnuevosxml\/.*\.xml).*", streamHTML)
            if len(xmls) > 0:
                return self.normalNuevoMultiple(xmls)
            ######################################################################################
            # EN PRUEBAS (solo si hay varios vídeos...)! (23/04/2013) [RETROCOMPATIBLE]: #########
            xmls = re.findall("\.xml='(.*)'", streamHTML)
            if len(xmls) > 1:
                xmls = ["/".join(self.url.split("/")[:3])+i for i in xmls]
                return self.normalMultiple(xmls)

            #####################################################################################
            if streamHTML.find(".seoURL='") != -1: # Url directamente en HTML
                self.debug(u"Vídeo con SEO URL")
                img = self.URL_DE_ANTENA3 + streamHTML.split(".poster=\'/")[1].split("\'")[0]
                url2down, name = self.__modoNormalConURL(streamHTML)
            elif streamHTML.find("a3_gp_visor_player") != -1:
                self.log(u"[INFO] Vídeo de Fórmula 1")
                return self.__modoF1(streamHTML) # return directamente aquí (varios videos)
            else: # No está la url en el hmtl (buscar por varias partes)
                if streamHTML.find("<div class=\"visor\">") != -1: # Más de 1 parte # Quizas mejor "carrusel"?
                    return self.__modoNormalVariasPartes(streamHTML) # return directamente aquí (varios videos)
                    #url2down, name = self.__modoNormalVariasPartes(streamHTML)
                else: # Solo una parte
                    url2down, name = self.__modoNormalUnaParte(streamHTML)
        
        desc = None        
        try:
            desc = Utiles.recortar(streamHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
        except:
            try:
                desc = Utiles.recortar(streamHTML, "<meta name=\"description\" content=\"", "\" />").strip()
            except:   
                desc = None
        
        #if type(url2down) == list:
        #    for i in url2down:
        #        if i.find("geobloqueo") != -1:
        #            self.log(u"[!!!] El vídeo \"" + i + "\" no se puedo descargar (geobloqueado)")
        #            url2down.remove(i)
        #            # TODO: Borrar también su nombre correspondiente
        #        
        #    # Comprobar si todas las partes están geobloqueadas (no quedan elementos en la lista):
        #    if len(url2down) == 0:
        #        raise Error.GeneralPyspainTVsError("Grupo Antena 3. Todo el contenido Geobloqueado.")
        #else:
        #    if url2down.find("geobloqueo") != -1:
        #        raise Error.GeneralPyspainTVsError("Grupo Antena 3. Todo el contenido Geobloqueado.")
        if type(name) == list:
            try:
                tit_vid = name[0].split(".")[0]
                tit_vid = tit_vid.replace("_" + tit_vid.split("_")[1], "")
            except:
                try:
                    tit_vid = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip()
                except:
                    tit_vid = "Vídeo de Grupo Antena 3"
            for i in name:
                b = Utiles.formatearNombre(i)
                name[name.index(i)] = b
        else:
            try:
                tit_vid = name.split(".")[0].replace("_" + name.split("_")[1], "")
                tit_vid = tit_vid.replace("_" + tit_vid.split("_")[1], "")
            except:
                try:
                    tit_vid = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip()
                except:
                    tit_vid = "Vídeo de Grupo Antena 3"
            name = Utiles.formatearNombre(name)
        
        #try:
        #    tit_vid = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip()
        #except:
        #    tit_vid = "Vídeo de Grupo Antena 3"
        tit_vid = tit_vid.replace("TV VIDEOS ONLINE", "").strip()
        
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url2down] if type(url2down) != list else url2down,
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if type(name) != list else name,
                        "tipo"      : "http",
                        "partes"    : 1 if type(url2down) != list else len(url2down),
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit_vid] if tit_vid is not None else None,
                "descs": [desc] if desc is not None else None
                }

