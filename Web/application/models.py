# -*- coding: utf-8 -*-
"""
models.py

App Engine datastore models

"""


from google.appengine.ext import db


class ExampleModel(db.Model):
    """Example Model"""
    example_name = db.StringProperty(required=True)
    example_description = db.TextProperty(required=True)
    added_by = db.UserProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    
class RegistroDescargas(db.Model):
    '''Model para guardar el registro de vídeos descargados en la web'''
    date = db.DateTimeProperty(auto_now_add=True)
    urlOrig = db.StringProperty(required=True)
    urlImg = db.StringProperty(required=True)
    vidTit = db.StringProperty(required=True)
    vidDesc = db.TextProperty()
    
