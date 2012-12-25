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

from flask import render_template, flash, url_for, redirect, Response, json, request

#from models import ExampleModel
#from decorators import login_required, admin_required
#from forms import ExampleForm

from models import RegistroDescargas

import re

from spaintvs import *
from spaintvs import miteleGAE

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
        urls = ["antena3.com", "lasexta.com", "lasextadeportes.com", "lasextanoticias.com"]
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
        urls = ["telecinco.es", "divinity.es"]
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
        urls = ["eitb.tv"]
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
        urls = ["tv3.cat", "3cat24.cat", "324.cat", "3xl.cat", "catradio.cat"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False
    
    def isGiraldaTV(self):
        '''return True si la URL pertenece a Giralda Televisón'''
        urls = ["giraldatv.es"]
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
    
    # Obtener los últimos vídeos descargados:
    try:
        last = RegistroDescargas.gql("order by date DESC LIMIT 4")
    except:
        last = None
    
    if urlOrig is None:
        if request.method == "GET": # La URL se pasa por parámetro http://web.pydowntv.com/?url=""
            try:
                urlOrig = request.args['url']
            except:
                return render_template('index.html', last=last)
        else:
            urlOrig = request.form['urlOrig']
    
    if urlOrig == u'' or urlOrig == u"Introduce AQUÍ la URL del vídeo a descargar...":
        flash(u"No has introducido ninguna url.. oO")
        return redirect(url_for('home'))
    
    ## CASOS ESPECIALES URL NO ASCCII
    #RTPA
    if urlOrig.find("rtpa.es") != -1:
        try: urlOrig = urlOrig.split("video:")[0] + "video:_" + urlOrig.split("_")[1]
        except: pass
    #END - RTPA
    ## END - CASOS ESPECIALES 
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
        #return render_template("api.html", messages=URLmalFormada)

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
    
    # Guardar Registro antes de renderizar: .decode('iso-8859-1').encode('utf8')
    try: 
        reg = RegistroDescargas(
                                urlOrig = urlOrig,
                                urlImg = info["videos"][0]["url_img"],
                                vidTit = info["titulos"][0]#,
                                #vidDesc = info["descs"][0]
                                )
        reg.put()
    except: pass #TODO: Mejorar esto (codificación...)

    return render_template(
                           "index.html",
                           videos=info["videos"],
                           titulos=info["titulos"],
                           descripciones=info["descs"],
                           urlOrig=urlOrig,
                           last=last
                           )



def api(url=None):
    opcs = _default_opcs
    if request.method == "GET":
        try:
            urlOrig = request.args['url']
        except:
            return render_template("api.html")     
    try:
        search = urlOrig
        #search = url if url is not None else request.args['url']
        ## CASOS ESPECIALES URL NO ASCCII
        #RTPA
        try: search = search.split("video:")[0] + "video:_" + search.split("_")[1]
        except: pass
        #END - RTPA
        ## END - CASOS ESPECIALES 
        if compURL(search):
            canal = qCanal(search, opcs)
            if canal == None:
                js = json.dumps(TVnoSoportada)
                resp = Response(js, status=200, mimetype='application/json')
                return resp
                #return render_template("api.html", messages=TVnoSoportada)
        else:
            js = json.dumps(URLmalFormada)
            resp = Response(js, status=200, mimetype='application/json')
            return resp
            #return render_template("api.html", messages=URLmalFormada)


        try:
            info = canal.getInfo()
        except Error.GeneralPyspainTVsError, e:
            msg = {
                "exito": False,
                "mensaje": e
                }
            js = json.dumps(msg)
            resp = Response(js, status=200, mimetype='application/json')
            return resp
            #return render_template("api.html", messages=msg)
        except:
            js = json.dumps(ErrorDesconocido)
            resp = Response(js, status=200, mimetype='application/json')
            return resp
            #return render_template("api.html", messages=ErrorDesconocido)
        js = json.dumps(info)
        resp = Response(js, status=200, mimetype='application/json')
        return resp
        #return render_template("api.html", messages=info)
    except Error.GeneralPyspainTVsError, e:
        msg = {
            "exito": False,
            "mensaje": e
            }
        js = json.dumps(msg)
        resp = Response(js, status=200, mimetype='application/json')
        return resp
    except Exception, e:
        js = json.dumps(ErrorDesconocido)
        resp = Response(js, status=200, mimetype='application/json')
        return resp
        #return render_template("api.html", messages=ErrorDesconocido)
        
def mitele(urlOrig=None):
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
            
    return redirect(miteleGAE.MiTele(urlOrig, opcs).getInfo()['videos'][0]['url_video'][0])

def ayuda():
    return render_template("ayuda.html")

def canales():
    return render_template("canales.html")

def apps():
    return render_template("apps.html")

def legal():
    return render_template("legal.html")

def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
    return 'Hello %s' % username


#@login_required
#def list_examples():
#    """List all examples"""
#    examples = ExampleModel.all()
#    form = ExampleForm()
#    if form.validate_on_submit():
#        example = ExampleModel(
#            example_name = form.example_name.data,
#            example_description = form.example_description.data,
#            added_by = users.get_current_user()
#        )
#        try:
#            example.put()
#            example_id = example.key().id()
#            flash(u'Example %s successfully saved.' % example_id, 'success')
#            return redirect(url_for('list_examples'))
#        except CapabilityDisabledError:
#            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
#            return redirect(url_for('list_examples'))
#    return render_template('list_examples.html', examples=examples, form=form)
#
#
#@login_required
#def delete_example(example_id):
#    """Delete an example object"""
#    example = ExampleModel.get_by_id(example_id)
#    try:
#        example.delete()
#        flash(u'Example %s successfully deleted.' % example_id, 'success')
#        return redirect(url_for('list_examples'))
#    except CapabilityDisabledError:
#        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
#        return redirect(url_for('list_examples'))
#
#
#@admin_required
#def admin_only():
#    """This view requires an admin account"""
#    return 'Super-seekrit admin page.'


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

