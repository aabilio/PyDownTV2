# -*- coding: utf-8 -*-
"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""


from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import render_template, flash, url_for, redirect, Response, json, request, g
from settings import DOS_IPS as dosIPs
from application import utils

#from models import ExampleModel
#from decorators import login_required, admin_required
#from forms import ExampleForm

from models import RegistroDescargas, RegistroDescargasAPI

import re

from spaintvs import *
from spaintvs import miteleGAE
from spaintvs import Descargar

URL_CHECK_COUNTRY = "http://api.hostip.info/get_json.php?ip="

_default_opcs = {
                "log": False,
                "debug": False
                }

# Mensajes de API:
TVnoSoportada =     {
                    "exito": False,
                    "mensaje": "Canal no soportado"
                    }

URLmalFormada   =   {
                    "exito": False,
                    "mensaje": "URL incorrecta" 
                    }

ErrorDesconocido =  {
                    "exito": False,
                    "mensaje": "Error desconocido"
                    }

class Canales(object):
# Cuando implemento el mismo método que el script, la respuesta JSON no funciona bien
# No tengo ni idea por qué.. pero pasa, así que lo dejo de esta manera
    '''
        Contiene los métodos para identificar a qué TV pertenece la url que
        introdujo el usuario.
    '''
    def __init__(self, url=None):
        '''Recibe la url'''
        self._url = url
    
    def isTVE(self):
        '''return True si la URL pertenece a Televisión Española'''
        if self._url.find("rtve.es") != -1: return True
    
    def isGrupoAntena3(self):
        '''return True si la URL pertenece al Grupo de Antena 3'''
        urls = ["antena3.com", "lasexta.com", "lasextadeportes.com", "lasextanoticias.com", "atresplayer.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    def isCuatro(self):
        '''return True si la URL pertenece al Grupo de Cuatro'''
        urls = ["cuatro.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isTelecinco(self):
        '''return True si la URL pertenece al Grupo de Telecinco'''
        urls = ["telecinco.es", "divinity.es", "mitelekids.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isMitele(self):
        '''return True si la URL pertenece al Grupo de Telecinco (MiTele)'''
        urls = ["mitele.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isCRTVG(self):
        '''return True si la URL pertenece a Televisión de Galiza'''
        urls = ["crtvg.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isRTPA(self):
        '''return True si la URL pertenece a rtpa.es'''
        urls = ["rtpa.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isAragonTV(self):
        '''return True si la URL pertenece a Aragon TV'''
        urls = ["aragontelevision.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isCanalSur(self):
        '''return True si la URL pertenece a Canal Sur'''
        urls = ["canalsur.es", "canalsuralacarta.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isCanalExtremadura(self):
        '''return True si la URL pertenece a Canal Extremadura'''
        urls = ["canalextremadura.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isMTV(self):
        '''return True si la URL pertenece a MTV'''
        urls = ["mtv.es", "mtv.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isTelemadrid(self):
        '''return True si la URL pertenece a Telemadrid'''
        urls = ["telemadrid.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isEITB(self):
        '''return True si la URL pertenece a EITB'''
        urls = ["eitb.tv", "eitb.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isRTVCYL(self):
        '''return True si la URL pertenece a Televisión de Castilla y León'''
        urls = ["rtvcyl.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isRTVCM(self):
        '''return True si la URL pertenece a Televisión de Castilla-La Mancha'''
        urls = ["rtvcm.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isTV3(self):
        '''return True si la URL pertenece a Televisió de Catalunya'''
        urls = ["tv3.cat", "3cat24.cat", "324.cat", "3xl.cat", "catradio.cat", "esport3.cat", "8tv.cat"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isGiraldaTV(self):
        '''return True si la URL pertenece a Giralda Televisón'''
        urls = ["giraldatv.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isRTVV(self):
        '''return True si la URL pertenece a Radiotelevisión Valenciana'''
        urls = ["rtvv.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isIntereconomia(self):
        '''return True si la URL pertenece a Intereconomia'''
        urls = ["intereconomia.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isHistoria(self):
        '''return True si la URL pertenece a Canal Historia'''
        urls = ["historia.adnstream.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isPlus(self):
        '''return True si la URL pertenece a Canal Plus'''
        urls = ["canalplus.es", "plus.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isVtelevision(self):
        '''return True si la URL pertenece a Canal Plus'''
        urls = ["vtelevision.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isRiasBaixas(self):
        '''return True si la URL pertenece a Canal Plus'''
        urls = ["canalriasbaixas.com"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isABC(self):
        '''return True si la URL pertenece a Canal Plus'''
        urls = ["abc.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isDisneChannel(self):
        '''return True si la URL pertenece a Disney Channel (Replay)'''
        urls = ["replay.disneychannel.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

        
    
def qCanal(url, opcs):
    '''
        Comprueba utlizando la clase Canales de que servicio ha recibido la url
        y devuelve el objeto según el servicio que del cual se haya pasado la
        url
    '''
    # Descomentar return según se vañan añadiendo
    canal = Canales(url)
    if canal.isTVE(): return tve.TVE(url, opcs)
    elif canal.isGrupoAntena3(): return grupo_a3.GrupoA3(url, opcs)
    elif canal.isCuatro(): return cuatro.Cuatro(url, opcs)
    elif canal.isTelecinco(): return telecinco.Telecinco(url, opcs)
    elif canal.isMitele(): return miteleGAE.MiTele(url, opcs)
    elif canal.isCRTVG(): return crtvg.CRTVG(url, opcs)
    elif canal.isRTPA(): return rtpa.RTPA(url, opcs)
    elif canal.isAragonTV(): return aragontv.AragonTV(url, opcs)
    elif canal.isCanalSur(): return canalsur.CanalSur(url, opcs)
    elif canal.isCanalExtremadura(): return extremadura.CExtremadura(url, opcs)
    elif canal.isMTV(): return mtv.MTV(url, opcs)
    elif canal.isTelemadrid(): return telemadrid.Telemadrid(url, opcs)
    elif canal.isEITB(): return eitb.EITB(url, opcs)
    elif canal.isRTVCYL(): return rtvcyl.RTVCYL(url, opcs)
    elif canal.isRTVCM(): return rtvcm.RTVCM(url, opcs)
    elif canal.isTV3(): return tv3.TV3(url, opcs)
    elif canal.isGiraldaTV(): return giraldatv.GiraldaTV(url, opcs)
    elif canal.isRTVV(): return rtvv.RTVV(url, opcs)
    elif canal.isIntereconomia(): return intereconomia.Intereconomia(url, opcs)
    elif canal.isHistoria(): return historia.Historia(url, opcs)
    elif canal.isPlus(): return plus.Plus(url, opcs)
    elif canal.isVtelevision(): return vtelevision.V(url, opcs)
    elif canal.isRiasBaixas(): return riasbaixas.RiasBaixas(url, opcs)
    elif canal.isABC(): return abc.ABC(url, opcs)
    elif canal.isDisneChannel(): return disneychannel.DisneyChannel(url, opcs)
    else: return None

def compURL(url):
    '''
        Compara de forma muy básica si la cadena que se le pasa como parámetro es una URL válida
    '''
    p = re.compile('^(https?)://([-a-z0-9\.]+)(?:(/[^\s]+)(?:\?((?:\w+=[-a-z0-9/%:,._]+)?(?:&\w+=[-a-zA-Z0-9/%:,._]+)*)?)?)?$', re.IGNORECASE)
    m = p.match(url)
    if m:
        return True
    else:
        # Caso especial para RTVV:
        if url.startswith("#"): return True
        return False

## ----------------------------------------------------------------------------------------
## ----------------------------------------------------------------------------------------
## ----------------------------------------------------------------------------------------


## Vistas a partir de aquí:

def home(urlOrig=None):
    opcs = _default_opcs
    
    # Medida temporal:
    if request.remote_addr in dosIPs:
        return '''Hemos detectado un posible abuso del servicio. Para más información ponte en contacto con aabilio@pydowntv.com''', 404
    
    # Obtener los últimos vídeos descargados:
    #try:
    #    last = RegistroDescargas.gql("order by date DESC LIMIT 4")
    #except:
    #    last = None
    last=None

    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['url']
            except:
                return render_template('index.html', last=last)
        else:
            urlOrig = request.form['urlOrig']
    
    if urlOrig == u'' or urlOrig == u"Introduce AQUÍ la URL del vídeo a descargar...":
        flash(u"Parece que no has introducido ninguna url")
        return redirect(url_for('home'))
    
    a3user = request.cookies.get('a3user', None)
    a3pass = request.cookies.get('a3pass', None)
    opcs["a3user"] = a3user if a3user is not None else None
    opcs["a3pass"] = a3pass if a3pass is not None else None
    #return a3user+ " - " +a3pass
    
    ## CASOS ESPECIALES URL NO ASCCII
    #RTPA
    if urlOrig.find("rtpa.es") != -1:
        try: urlOrig = urlOrig.split("video:")[0] + "video:_" + urlOrig.split("_")[1]
        except: pass
    #END - RTPA
    ## END - CASOS ESPECIALES 
    #if urlOrig.startswith("www"): urlOrig ="http://"+urlOrig
    if not urlOrig.startswith("http://"): urlOrig ="http://"+urlOrig
    if compURL(urlOrig):
        canal = qCanal(urlOrig, opcs)
        if canal == None:
            flash(u"Lo que has introducido no corresponde con ningún canal soportado por PyDownTV\n")
            return redirect(url_for('home'))
            #return render_template("index.html", msgs=TVnoSoportada)
    else: #TODO: meter huevos de pascua aquí :P
        flash(u"URL incorrecta: \'%s\'" % urlOrig)
        return redirect(url_for('home'))
        
        #Primero meter en una lista las posibles variaciones
        #try:
        #    last = RegistroDescargas.gql("WHERE vidTit IN :title order by date DESC LIMIT 20", title=[urlOrig])
        #except:
        #    last = None
        #return last[0].urlOrig

    try:
        info = canal.getInfo()
    except Error.GeneralPyspainTVsError, e:
        flash(u"ERROR al recuperar el vídeo: %s" % e.__str__())
        return redirect(url_for('home'))
        #return render_template("api.html", messages=msg)
    except Exception, e:
        #flash(unicode(e.__str__()))
        #return redirect(url_for('home'))
        flash(u"ERROR al recuperar el vídeo. ¿Es una URL válida? %s" % e.__str__())
        return redirect(url_for('home'))
        #return render_template("api.html", messages=ErrorDesconocido)
    
    # Guardar Registro antes de renderizar: ##.decode('iso-8859-1').encode('utf8')
    # try: 
    #     reg = RegistroDescargas(
    #                             urlOrig = urlOrig,
    #                             urlImg = info["videos"][0]["url_img"],
    #                             vidTit = info["titulos"][0].decode('utf8')#,
    #                             #vidDesc = info["descs"][0]
    #                             )
    #     reg.put()
    # except: pass #TODO: Mejorar esto (codificación...)

    # Cambios en URLs debido a localizaciones:
    # Desgeo URLs de grupo_a3
    for url in ["antena3.com", "lasexta.com", "lasextadeportes.com", "lasextanoticias.com"]:
        if urlOrig.find(url) != -1:
            try:
                resp_country = json.loads(Descargar.get(URL_CHECK_COUNTRY+request.remote_addr))
                if resp_country['country_code'] != 'ES':
                    for i in range(len(info["videos"])):
                        for b in range(len(info["videos"][i]["url_video"])):
                            info["videos"][i]["url_video"][b] = info["videos"][i]["url_video"][b].replace("geodesprogresiva", "desprogresiva")
            except: break
            break
    # Desgeo URLs de rtve.es
    if urlOrig.find("rtve.es") != -1:
        try:
            resp_country = json.loads(Descargar.get(URL_CHECK_COUNTRY+request.remote_addr))
            if resp_country['country_code'] != 'ES':
                for i in range(len(info["videos"])):
                    for b in range(len(info["videos"][i]["url_video"])):
                        info["videos"][i]["url_video"][b] = info["videos"][i]["url_video"][b].replace("TE_GLESP", "TE_NGVA")
                        info["videos"][i]["url_video"][b] = info["videos"][i]["url_video"][b].replace("TE_GLEAD", "TE_NGVA")
                        info["videos"][i]["url_video"][b] = info["videos"][i]["url_video"][b].replace("TE_GLUCA", "TE_NGVA")
        except: pass

    # Comillas dobles para Windows en EITB
    if urlOrig.find("eitb.tv") != -1:
        try:
            os = request.user_agent.platform
            if os == 'windows':
                for i in range(len(info["videos"])):
                    for b in range(len(info["videos"][i]["rtmpd_cmd"])):
                        info["videos"][i]["rtmpd_cmd"][b] = info["videos"][i]["rtmpd_cmd"][b].replace("\'", "\"")
        except: pass
    #END
    
    ####################### url2downloader:
    jdownloader = ""
    if urlOrig.find('mitele') != -1: #Hasta ahora los vídeos Mitele solo son de un enlace
        jdownloader += "http://web.pydowntv.com/mitele?urlOrig="+urlOrig+"\r\n"
    else:
        for vid in info['videos']:
            for url in vid['url_video']:
                jdownloader += url+"\r\n"
    #################################################

    return render_template(
                           "index.html",
                           videos=info["videos"],
                           titulos=info["titulos"],
                           descripciones=info["descs"],
                           urlOrig=urlOrig,
                           jdownloader=jdownloader,
                           last=last
                           )
    

def agranel(urlOrig=None): #TODO: Hacer HILOS!!! 
    opcs = _default_opcs
    
    # Medida temporal:
    if request.remote_addr in dosIPs:
        return '''Hemos detectado un posible abuso del servicio. Para más información ponte en contacto con aabilio@pydowntv.com''', 404
    
    # Obtener los últimos vídeos descargados:
    #try:
    #    last = RegistroDescargas.gql("order by date DESC LIMIT 4")
    #except:
    #    last = None
    last=None

    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['url']
            except:
                return render_template('agranel.html', last=last)
        else:
            urlOrig = request.form['urlOrig']
    
    if urlOrig == u'' or urlOrig == u"Introduce AQUÍ la URL del vídeo a descargar...":
        flash(u"No has introducido ninguna url.. oO")
        return redirect(url_for('agranel')) 

    a3user = request.cookies.get('a3user', None)
    a3pass = request.cookies.get('a3pass', None)
    opcs["a3user"] = a3user if a3user is not None else None
    opcs["a3pass"] = a3pass if a3pass is not None else None
    
    # Ahora hay que cambiar todo
    urlsOrig = urlOrig.split()
    vids=[]
    tits=[]
    descs=[]
    urlsO = []
    errors=[]
    jdownloader = ""
    for i in range(len(urlsOrig)):
        ## CASOS ESPECIALES URL NO ASCCII
        #RTPA
        if urlsOrig[i].find("rtpa.es") != -1:
            try: urlsOrig[i] = urlsOrig[i].split("video:")[0] + "video:_" + urlsOrig[i].split("_")[1]
            except: pass
        #END - RTPA
        ## END - CASOS ESPECIALES
        if not urlsOrig[i].startswith("http://"): urlsOrig[i] ="http://"+urlOrig[i]
        
        #TODO: NO SALIR, quedarme con las ur buenas PARA TODO LO QUE VIENE A CONTINUACIÓN ;)
        if compURL(urlsOrig[i]): 
            canal = qCanal(urlsOrig[i], opcs)
            if canal == None:
                errors.append(u"La URL: %s no corresponde con ningún canal soportado por PyDownTV" % urlsOrig[i])
                continue
                #flash(u"Lo que has introducido no corresponde con ningún canal soportado por PyDownTV\n")
                #return redirect(url_for('agranel'))
        else: #TODO: meter huevos de pascua aquí :P
            errors.append(u"URL incorrecta: \'%s\'" % urlsOrig[i])
            continue
            #flash(u"URL incorrecta: \'%s\'" % urlOrig)
            #return redirect(url_for('agranel'))

        try:
            info = canal.getInfo()
        except Error.GeneralPyspainTVsError, e:
            errors.append(u"ERROR al recuperar el vídeo: %s" % e.__str__())
            continue
            #flash(u"ERROR al recuperar el vídeo: %s" % e.__str__())
            #return redirect(url_for('agranel'))
        except Exception, e:
            errors.append(u"No se ha podido recuperar el vídeo de la URL: %s. ¿Es una URL correcta?" % urlsOrig[i])
            continue
            #flash(u"ERROR al recuperar el vídeo. ¿Es una URL válida?")
            #return redirect(url_for('agranel'))
        
        # Guardar Registro antes de renderizar: ##.decode('iso-8859-1').encode('utf8')
        # try: 
        #     reg = RegistroDescargas(
        #                             urlOrig = urlsOrig[i],
        #                             urlImg = info["videos"][0]["url_img"],
        #                             vidTit = info["titulos"][0].decode('utf8')#,
        #                             #vidDesc = info["descs"][0]
        #                             )
        #     reg.put()
        # except: pass #TODO: Mejorar esto (codificación...)
        
        for vid in info['videos']: vids.append(vid)
        for tit in info['titulos']: tits.append(tit)
        for desc in info['descs']: descs.append(desc)
        for a in range(len(info['videos'])): urlsO.append(urlsOrig[i])        
    
        ####################### url2downloader:
        
        if urlOrig.find('mitele') != -1: #Hasta ahora los vídeos Mitele solo son de un enlace
            jdownloader += "http://web.pydowntv.com/mitele?urlOrig="+urlOrig+"\r\n"
        else:
            for vid in info['videos']:
                for url in vid['url_video']:
                    jdownloader += url+"\r\n"
        #################################################
    
    return render_template(
                           "agranel.html",
                           videos=vids,
                           titulos=tits,
                           descripciones=descs,
                           urlsOrig=urlsO,
                           jdownloader=jdownloader,
                           errors=errors if errors else None,
                           last=last
                           )

def api(urlOrig=None):
    opcs = _default_opcs
    
    # Medida temporal:
    if request.remote_addr in dosIPs:
        return '''Hemos detectado un posible abuso del servicio. Para más información ponte en contacto con aabilio@pydowntv.com''', 404
        
    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['url']
            except:
                return render_template("api.html")
        else:
            urlOrig = request.form['urlOrig']

    c_a3user = request.cookies.get('a3user', None)
    c_a3pass = request.cookies.get('a3pass', None)
    p_a3user = request.args.get('a3user', None)
    p_a3pass = request.args.get('a3pass', None)
    a3user   = p_a3user if p_a3user is not None else c_a3user
    a3pass   = p_a3pass if p_a3pass is not None else c_a3pass 
    opcs["a3user"] = a3user if a3user is not None else None
    opcs["a3pass"] = a3pass if a3pass is not None else None


    ## CASOS ESPECIALES URL NO ASCCII
    #RTPA
    if urlOrig.find("rtpa.es") != -1:
        try: urlOrig = urlOrig.split("video:")[0] + "video:_" + urlOrig.split("_")[1]
        except: pass
    #END - RTPA
    ## END - CASOS ESPECIALES 
    
    urlOrig = urlOrig.replace(" ", "%20") # TODO: use other tec

    # Track API:
    utils.sendAPICall2Analytics(request.remote_addr, "/api/url/"+urlOrig)

    
    #opcs = _default_opcs
    #if request.method == "GET":
        #try:
        #    urlOrig = request.args['url']
        #except:
        #    return render_template("api.html")     
    #try:
    if not urlOrig.startswith("http://"): urlOrig ="http://"+urlOrig
    if compURL(urlOrig):
        canal = qCanal(urlOrig, opcs)
        if canal == None:
            js = json.dumps(TVnoSoportada)
            if request.args.has_key("jsoncallback"):
                return request.args["jsoncallback"] + "(" + js + ");"
            else:
                resp = Response(js, status=200, mimetype='application/json')
                return resp 
            #return render_template("api.html", messages=TVnoSoportada)
    else:
        js = json.dumps(URLmalFormada)
        if request.args.has_key("jsoncallback"):
            return request.args["jsoncallback"] + "(" + js + ");"
        else:
            resp = Response(js, status=200, mimetype='application/json')
            return resp 
        #return render_template("api.html", messages=URLmalFormada)


    try:
        info = canal.getInfo()
    except Error.GeneralPyspainTVsError, e:
        msg = {
            "exito": False,
            "mensaje": e.__str__()
            }
        js = json.dumps(msg)
        if request.args.has_key("jsoncallback"):
            return request.args["jsoncallback"] + "(" + js + ");"
        else:
            resp = Response(js, status=200, mimetype='application/json')
            return resp 
        #return render_template("api.html", messages=msg)
    except Exception, e:
        #return e.__str__()
        js = json.dumps(ErrorDesconocido)
        if request.args.has_key("jsoncallback"):
            return request.args["jsoncallback"] + "(" + js + ");"
        else:
            resp = Response(js, status=200, mimetype='application/json')
            return resp
        #return render_template("api.html", messages=ErrorDesconocido)
        
    # Guardar Registro antes de renderizar: ##.decode('iso-8859-1').encode('utf8')
    #try: #NO GUARDAR MIENTRAS ESTOY DE VACACIONES :D
    #    reg = RegistroDescargasAPI(
    #                            urlOrig = urlOrig,
    #                            urlImg = info["videos"][0]["url_img"],
    #                            vidTit = info["titulos"][0].decode('utf8')#,
    #                            #vidDesc = info["descs"][0]
    #                            )
    #    reg.put()
    #except: pass #TODO: Mejorar esto (codificación...)

    js = json.dumps(info)
    if request.args.has_key("jsoncallback"):
        return request.args["jsoncallback"] + "(" + js + ");"
    else:
        resp = Response(js, status=200, mimetype='application/json', headers={"Access-Control-Allow-Origin": "*"})
        return resp 
    #return render_template("api.html", messages=info)
    #except Error.GeneralPyspainTVsError, e:
    #    msg = {
    #        "exito": False,
    #        "mensaje": e
    #        }
    #    js = json.dumps(msg)
    #    resp = Response(js, status=200, mimetype='application/json')
    #    return resp
    #except Exception, e:
    #    js = json.dumps(ErrorDesconocido)
    #    resp = Response(js, status=200, mimetype='application/json')
    #    return resp
    #    #return render_template("api.html", messages=ErrorDesconocido)

def mitele(urlOrig=None):  #Ahora ya no se pasa por aquí
    '''Función especial para mitele'''
    opcs = _default_opcs
    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['urlOrig']
            except:
                return render_template('ayuda.html')
        else:
            urlOrig = request.form['urlOrig']
    try:
        response = redirect(miteleGAE.MiTele(urlOrig, opcs).getInfo()['videos'][0]['url_video'][0])
        #response.headers['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
        return response
    except:
        flash(u"Se ha producido un error al localizar el vídeo.\nEste error no se debería de haber producido.\nPuedes volver a intentar a descargar el vídeo.")
        return redirect(url_for('home'))
    #try:        
        #return redirect(miteleGAE.MiTele(urlOrig, opcs).getInfo()['videos'][0]['url_video'][0]) #BANNED!
        #return redirect("http://aabilio.me/pydowntv/mt.php?mt_url="+miteleGAE.MiTele(urlOrig, opcs).getInfo()['videos'][0]['url_video'][0]) #Mucho tiempo (caduca)
    #    return redirect("http://aabilio.me/pydowntv/mt.php?mt_url="+urlOrig)
    #except:
    #    flash(u"Se ha producido un error al localizar el vídeo.\nEste error no se debería de haber producido.\nPuedes volver a intentar a descargar el vídeo.")
    #    return redirect(url_for('home'))

def mediaset(urlOrig=None):
    '''Función especial para mediaset'''
    opcs = _default_opcs
    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['urlOrig']
            except:
                return render_template('ayuda.html')
        else:
            urlOrig = request.form['urlOrig']
    try:
        if urlOrig.find('cuatro.com/') != -1:
            response = redirect(cuatro.Cuatro(urlOrig, opcs).getInfo()['videos'][0]['url_video'][0])
        else:
            response = redirect(telecinco.Telecinco(urlOrig, opcs).getInfo()['videos'][0]['url_video'][0])
        #response.headers['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
        return response
    except:
        flash(u"Se ha producido un error al localizar el vídeo.\nEste error no se debería de haber producido.\nPuedes volver a intentar a descargar el vídeo.")
        return redirect(url_for('home'))

    

def embed(urlOrig=None):
    opcs = _default_opcs

    # Medida temporal:
    if request.remote_addr in dosIPs:
        return '''Hemos detectado un posible abuso del servicio. Para más información ponte en contacto con aabilio@pydowntv.com''', 404
    
    if urlOrig is None:
        if request.method == 'POST':
            urlOrig = request.form['urlOrig']
        else:
            return render_template('embed.html')

    # Obtener los últimos vídeos descargados:
    #try:
    #    last = RegistroDescargas.gql("order by date DESC LIMIT 4")
    #except:
    #    last = None
    last=None

    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['url']
            except:
                return render_template('index.html', last=last)
        else:
            urlOrig = request.form['urlOrig']
    
    if urlOrig == u'' or urlOrig == u"Introduce AQUÍ la URL del vídeo a descargar...":
        h(u"Parece que no has introducido ninguna url")
        return redirect(urflasl_for('home'))

    a3user = request.cookies.get('a3user', None)
    a3pass = request.cookies.get('a3pass', None)
    opcs["a3user"] = a3user if a3user is not None else None
    opcs["a3pass"] = a3pass if a3pass is not None else None
    
    ## CASOS ESPECIALES URL NO ASCCII
    #RTPA
    if urlOrig.find("rtpa.es") != -1:
        try: urlOrig = urlOrig.split("video:")[0] + "video:_" + urlOrig.split("_")[1]
        except: pass
    #END - RTPA
    ## END - CASOS ESPECIALES 
    #if urlOrig.startswith("www"): urlOrig ="http://"+urlOrig
    if not urlOrig.startswith("http://"): urlOrig ="http://"+urlOrig
    if compURL(urlOrig):
        canal = qCanal(urlOrig, opcs)
        if canal == None:
            flash(u"Lo que has introducido no corresponde con ningún canal soportado por PyDownTV\n")
            return redirect(url_for('home'))
            #return render_template("index.html", msgs=TVnoSoportada)
    else: #TODO: meter huevos de pascua aquí :P
        flash(u"URL incorrecta: \'%s\'" % urlOrig)
        return redirect(url_for('home'))
        
        #Primero meter en una lista las posibles variaciones
        #try:
        #    last = RegistroDescargas.gql("WHERE vidTit IN :title order by date DESC LIMIT 20", title=[urlOrig])
        #except:
        #    last = None
        #return last[0].urlOrig

    try:
        info = canal.getInfo()
    except Error.GeneralPyspainTVsError, e:
        flash(u"ERROR al recuperar el vídeo: %s" % e.__str__())
        return redirect(url_for('home'))
        #return render_template("api.html", messages=msg)
    except Exception, e:
        #flash(unicode(e.__str__()))
        #return redirect(url_for('home'))
        flash(u"ERROR al recuperar el vídeo. ¿Es una URL válida?")
        return redirect(url_for('home'))
        #return render_template("api.html", messages=ErrorDesconocido)
    
    # Guardar Registro antes de renderizar: ##.decode('iso-8859-1').encode('utf8')
    # try: 
    #     reg = RegistroDescargas(
    #                             urlOrig = urlOrig,
    #                             urlImg = info["videos"][0]["url_img"],
    #                             vidTit = info["titulos"][0].decode('utf8')#,
    #                             #vidDesc = info["descs"][0]
    #                             )
    #     reg.put()
    # except: pass #TODO: Mejorar esto (codificación...)
    
    ####################### url2downloader:
    jdownloader = ""
    if urlOrig.find('mitele') != -1: #Hasta ahora los vídeos Mitele solo son de un enlace
        jdownloader += "http://web.pydowntv.com/mitele?urlOrig="+urlOrig+"\r\n"
    else:
        for vid in info['videos']:
            for url in vid['url_video']:
                jdownloader += url+"\r\n"
    #################################################

    return render_template(
                           "index.html",
                           videos=info["videos"],
                           titulos=info["titulos"],
                           descripciones=info["descs"],
                           urlOrig=urlOrig,
                           jdownloader=jdownloader,
                           last=last
                           )

import requests
def rest_a3p_checker():
    url = request.args['url'] if request.args.has_key('url') else "http://fsmkjlkjkldfsdf.com"
    r = requests.head(url, allow_redirects=True)
    if r.url == "http://desprogresiva.antena3.com/mp_series1/util/video_decep.mp4":
        info = {"url": r.url,"statuscode": 404}
    else:
        info = {"url": r.url,"statuscode": unicode(r.status_code) or "404"}
    js = json.dumps(info)

    if request.args.has_key("jsoncallback"):
        return request.args["jsoncallback"] + "(" + js + ");"
    else:
        resp = Response(js, status=200, mimetype='application/json')
        return resp 
    #return unicode(requests.head(url).status_code) or "404"
    
def ayuda():
    return render_template("ayuda.html")

def canales():
    return render_template("canales.html")

def apps():
    return render_template("apps.html")

def legal():
    return render_template("legal.html")

def privacidad():
    return render_template("privacidad.html")

def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
    g.user_info = {
                 "name": username if username is not None else "NO ESPECIFICADO",
                 "ip": request.remote_addr if request.remote_addr is not None else "NO ESPECIFICADO",
                 "os": request.user_agent.platform if request.user_agent.platform is not None else "NO ESPECIFICADO",
                 "browser": request.user_agent.browser if request.user_agent.browser is not None else "NO ESPECIFICADO",
                 "browser_version": request.user_agent.version if request.user_agent.version is not None else "NO ESPECIFICADO",
                 "language": request.user_agent.language if request.user_agent.language is not None else "NO ESPECIFICADO",
                 "pais": request.headers.get('X-AppEngine-Country') or "NO ESPECIFICADO",
                 "region": request.headers.get('X-AppEngine-Region') or "NO ESPECIFICADO",
                 "ciudad": request.headers.get('X-AppEngine-City') or "NO ESPECIFICADO",
                 "latLong": request.headers.get('X-AppEngine-CityLatLong') or "NO ESPECIFICADO"
                }
    return render_template("hello.html")
    
    return str(request.headers)
    #return 'Hello %s' % " ".join(user_info.values())
def rest_url_home(url):
    '''http://web.pydowntv.com/url/http://www.antena3.com/....html'''
    return home(url)
def rest_url_api(url):
    '''http://web.pydowntv.com/api/http://www.antena3.com/....html'''
    return api(url)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

