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

from models import ExampleModel
from decorators import login_required, admin_required
from forms import ExampleForm

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
        urls = ["telecinco.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isMitele(self):
        '''return True si la URL pertenece al Grupo de Telecinco'''
        urls = ["mitele.es"]
        for url in urls:
            if self._url.find(url) != -1: return True
        return False

    def isCRTVG(self):
        '''return True si la URL pertenece al Grupo de Telecinco'''
        urls = ["crtvg.es"]
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

def home():
    return '''Web en Construcción<br \>
    Nueva API para el módulo spaintvs.<br \>
    Peticiones GET a: http://pydowntv2.appspot.com/api?url=<br \>
    spaintvs en GitHub <a href="https://github.com/aabilio/PyDownTV2/">aquí</a>'''

def api(url=None):
    opcs = _default_opcs
    try:
        search = url if url is not None else request.args['url'] 
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

def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
    return 'Hello %s' % username


@login_required
def list_examples():
    """List all examples"""
    examples = ExampleModel.all()
    form = ExampleForm()
    if form.validate_on_submit():
        example = ExampleModel(
            example_name = form.example_name.data,
            example_description = form.example_description.data,
            added_by = users.get_current_user()
        )
        try:
            example.put()
            example_id = example.key().id()
            flash(u'Example %s successfully saved.' % example_id, 'success')
            return redirect(url_for('list_examples'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('list_examples'))
    return render_template('list_examples.html', examples=examples, form=form)


@login_required
def delete_example(example_id):
    """Delete an example object"""
    example = ExampleModel.get_by_id(example_id)
    try:
        example.delete()
        flash(u'Example %s successfully deleted.' % example_id, 'success')
        return redirect(url_for('list_examples'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_examples'))


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

