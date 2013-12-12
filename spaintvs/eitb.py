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

# Módulo para descargar todos los vídeos de la web de Euskal Irrati Telebista

__author__="aabilio"
__date__ ="$19-dic-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

from pyamf import remoting
import httplib

import re

url_validas = ["eitb.tv", "eitb.com"]

class EITB(Canal.Canal):
    '''
        Clase para manejar los vídeos de Euskal Irrati Telebista.
    '''
    
    URL_EITB = "http://eitb.tv"
    URL_EITB_JSON = "http://www.eitb.tv/es/get/multimedia/video_json/id/"
    
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

    
    def build_amf_request(self, const, playerID, videoID, publisherID):
        env = remoting.Envelope(amfVersion=3)
        env.bodies.append(
            (
                "/1", 
                remoting.Request(
                    target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", 
                    body=[const, playerID, videoID, publisherID],
                    envelope=env
                )
            )
        )
        return env
    
    def get_data(self, publisherID, playerID, const, videoID, playerKey):
        conn = httplib.HTTPConnection("c.brightcove.com")
        envelope = self.build_amf_request(const, playerID, videoID, publisherID)
        #conn.request("POST", "/services/messagebroker/amf?playerKey=AQ~~,AAAAF8Q-iyk~,FDoJSqZe3TSVeJrw8hVEauWQtrf-1uI7", str(remoting.encode(envelope).read()),{'content-type': 'application/x-amf'})
        conn.request("POST", "/services/messagebroker/amf?playerKey="+playerKey, str(remoting.encode(envelope).read()),{'content-type': 'application/x-amf'})
        response = conn.getresponse().read()
        response = remoting.decode(response).bodies[0][1].body

        return response
    
    
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

        if self.url.find("eitb.com/") != -1:
            raise Error.GeneralPyspainTVsError(u".com de EITB no está de momento soportado por pydowntv")
        
        #TODO: Incluír este soporte para mp3
        if self.url.find("audios/") != -1 or self.url.find("audioak/") != -1:
            raise Error.GeneralPyspainTVsError(u"Audios aún no soportados. Lo estarán dentro de poco ;)")
            self.info(u"[INFO] Audio")
            name = html.split("<title>")[1].split("<")[0]
            streamMP3 = html.split("<a id=\"descargaMp3\"")[1].split(">")[0]
            url = self.URL_EITB + streamMP3.split("href=\"")[1].split("\"")[0]
            name += ".mp3"
            
        elif self.url.find("videos/") != -1 or self.url.find("bideoak/") != -1 or self.url.find("video/") != -1 or self.url.find("bideoa/") != -1:
            if html.find("<a id=\"descargaMp4\"") != -1:
                name = html.split("<title>")[1].split("<")[0]
                streamMP4 = html.split("<a id=\"descargaMp4\"")[1].split(">")[0]
                url = self.URL_EITB + streamMP4.split("href=\"")[1].split("\"")[0]
            else:
                #streamHTML = self.__descHTML(self._URL_recibida)
                name = self.url.split("/")[-1]
                playerID = html.split("<param name=\"playerID\" value=\"")[1].split("\"")[0]
                playerKey = html.split("<param name=\"playerKey\" value=\"")[1].split("\"")[0]
                const = "9f8617ac59091bcfd501ae5188e4762ffddb9925"
                publisherID = "102076681001"
                videoID = self.url.split("/")[-1]
                if not videoID.isdigit():
                    videoID = [n for n in self.url.split("/") if n.isdigit() and len(n)>5][1]

                try:
                    rtmpdata = self.get_data(publisherID, playerID, const, videoID, playerKey)#['renditions']
                    videos_data = rtmpdata['renditions']
                except:
                    raise Error.GeneralPyspainTVsError(u"Parece que e vídeo no está disponible en la web")
                
                try: img = rtmpdata['videoStillURL']
                except: img = None
                
                desc = None
                try: desc1 = rtmpdata['longDescription'].encode('utf8') if rtmpdata['longDescription'] is not None else None
                except: desc1=None
                try: desc2 = rtmpdata['shortDescription'].encode('utf8') if rtmpdata['shortDescription'] is not None else None
                except: desc2=None
                try: desc3 = rtmpdata['customFields']['longdescription_c'].encode('utf8') if rtmpdata['customFields']['longdescription_c'] is not None else None
                except: desc3=None
                try: desc4 = rtmpdata['customFields']['shortdescription_c'].encode('utf8') if rtmpdata['customFields']['shortdescription_c'] is not None else None
                except: desc4=None
                try:
                    if desc1 is not None and desc1 != "" and desc1 != ".": desc = desc1
                    elif desc2 is not None and desc2 != "" and desc2 != ".": desc = desc2
                    elif desc3 is not None and desc3 != "" and desc3 != ".": desc = desc3
                    elif desc4 is not None and desc4 != "" and desc4 != ".": desc = desc4
                except: desc = u"Vídeo de Euskal Irrati Telebista".encode('utf8')
                else:
                    if desc is None or desc == "": desc = u"Vídeo de Euskal Irrati Telebista".encode('utf8')
                tit = None     
                try: tit = rtmpdata['displayName'].encode('utf8')
                except: tit = u"Vídeo de Euskal Irrati Telebista".encode('utf8')
                else:
                    if type(tit) is unicode:
                        if tit == u"": tit = u"Vídeo de Euskal Irrati Telebista".encode('utf8')
                    elif type(tit) is str:
                        if tit == "": tit = u"Vídeo de Euskal Irrati Telebista".encode('utf8')
                    if tit is None: tit = u"Vídeo de Euskal Irrati Telebista".encode('utf8')                
                try:
                    name = Utiles.formatearNombre(str(rtmpdata['displayName'].encode('utf8'))+".mp4")
                except:
                    name = "VideoEITB.mp4" #TODO: mejorar el filename

                # Devolver 3 vídeos, de las distintas calidades
                videos = []
                num_videos = 0
                for vid in videos_data:
                    num_videos += 1            
                    #montar comando
                    url = str(vid['defaultURL'])
                    #tcurl = url.replace("/&mp4:"+url.split("/&mp4:")[1].split(".mp4")[0]+".mp4", "")
                    pageurl = self.url
                    typem = "rtmp"
                    if url.find("edgefcs.net") != -1: #NUEVO edgefcs de AKAMAI (thanks to http://blog.tvalacarta.info/)
                        app = "ondemand?"+ url.split(".mp4?")[1]+"&videoId="+videoID+"&lineUpId=&pubId="+publisherID+"&playerId="+playerID
                        playpath = "mp4:"+url.split("mp4:")[1]+"&videoId="+videoID
                        swfurl = "http://admin.brightcove.com/viewer/us20121213.1025/federatedVideoUI/BrightcovePlayer.swf?uid=1355746343102"
                        rtmpd_cmd = "rtmpdump --rtmp '"+url+"' --app='"+app+"' --swfUrl='"+swfurl+"' --playpath='"+playpath+"' --pageUrl='"+pageurl+"' -o '"+name+"'"
                        msg = u"Nuevos comandos gracias a Jesús de <a href=\"http://blog.tvalacarta.info/\">TV a Carta</a>".encode('utf8')
                        #Convertir a HTTP, paso intermedio (thanks @denobis)
                        try: change = re.findall("rtmp://.*\&mp4:", url)[0]
                        except: change = "#####"
                        url = url.replace(change, "http://brightcove04.brightcove.com/")
                        if url.startswith("http://"): typem = "http"
                    else: #Antiguo: brightcove, hay más?
                        app = url.split("/&")[0].split(".net/")[1]  +"?videoId="+videoID+"&lineUpId=&pubId="+publisherID+"&playerId="+playerID
                        playpath = "mp4:"+url.split("mp4:")[1].split(".mp4")[0]+".mp4"+"?videoId="+videoID+"&lineUpId=&pubId="+publisherID+"&playerId="+playerID
                        swfurl = "http://admin.brightcove.com/viewer/us20121218.1107/federatedVideoUI/BrightcovePlayer.swf?uid=1355158765470"
                        C1 = "B:0"
                        C2 = "S:" + "&".join(url.split("&")[1:])
                        rtmpd_cmd = "rtmpdump --rtmp '"+url+"' --app='"+app+"' --swfUrl='"+swfurl+"' --playpath='"+playpath+"' --pageUrl='"+pageurl+"' -C '"+C1+"' -C '"+C2+"' -o '"+name+"'"
                        msg = None
                    ##END: montar comando
                    size = str(vid['frameWidth'])+"x"+str(vid['frameHeight'])
                    
                    temp = {
                            "url_video" : [url],
                            "url_img"   : img if img is not None else None,
                            "filename"  : [name] if name is not None else None,
                            "tipo"      : typem,
                            "partes"    : 1,
                            "rtmpd_cmd" : [rtmpd_cmd],
                            "menco_cmd" : None,
                            "url_publi" : None,
                            "otros"     : size,
                            "mensaje"   : msg
                            }
                    videos.append(temp)
                    
        else:
            raise Error.GeneralPyspainTVsError(u"No se reconoce el tipo de contenido")
        
        
        if name:
            name = Utiles.formatearNombre(name)
            
        return {"exito" : True,
                "num_videos" : num_videos,
                "mensaje"   : u"URLs obtenidas correctamente",
                "videos": videos,
                "titulos": [tit]*num_videos if tit is not None else None,
                "descs": [desc]*num_videos if desc is not None else None
                }




