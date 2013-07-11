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

__author__="jaimeMF"
__date__ ="$11-jul-2013 14:00:00$"

import re
import xml.etree.ElementTree

import Canal
import Utiles
import Descargar

url_validas = ["replay.disneychannel.es"]

class DisneyChannel(Canal.Canal):

    URL_DISNEY_CHANNEL = "http://replay.disneychannel.es"
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)

    def getInfo(self):
        html = Descargar.get(self.url)

        m_xml_url = re.search(r"\.xml='(.+?)'", html)
        if m_xml_url is None:
            return {"exito": False, "mensaje": "No se encontró información del video"}

        xml_url = self.URL_DISNEY_CHANNEL + m_xml_url.group(1)
        chapter_xml = Descargar.get(xml_url)
        doc = xml.etree.ElementTree.fromstring(chapter_xml)

        base_http_url = doc.find("./url/urlHttpVideo").text
        video_info = doc.find("./multimedias/multimedia")
        img = self.URL_DISNEY_CHANNEL + video_info.find("./archivoMultimediaMaxi/archivo").text
        titulo = video_info.find("./nombre").text
        serie = video_info.find("./seccion").text
        desc = video_info.find("./descripcion").text

        parts_urls = []
        filenames = []
        parts = list(doc.findall("./multimedias/multimedia"))
        parts += list(doc.findall("./multimedias/relacionados"))
        for (i, part) in enumerate(parts, 1):
            part_url = base_http_url + video_info.find("./archivoMultimedia/archivo").text
            ext = part_url.rpartition('.')[2]
            filename = "%s-%s %s.%s" % (titulo, i, serie, ext)
            filename_clean = Utiles.formatearNombre(filename)
            parts_urls.append(part_url)
            filenames.append(filename_clean)

        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : parts_urls,
                        "url_img"   : img,
                        "filename"  : filenames,
                        "tipo"      : "http",
                        "partes"    : len(parts_urls),
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos":[titulo],
                "descs": [desc],
                }
