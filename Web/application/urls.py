# -*- coding: utf-8 -*-
"""
urls.py

URL dispatch route mappings and error handlers

"""

from flask import render_template, request, redirect, Response

from application import app
from application import views
from application import utils


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', 'home', view_func=views.home, methods=['GET', 'POST'])

# A Granel page
app.add_url_rule('/agranel', 'agranel', view_func=views.agranel, methods=['GET', 'POST'])

# Help Page
app.add_url_rule('/ayuda', 'ayuda', view_func=views.ayuda, methods=['GET', 'POST'])

# Channels Page
app.add_url_rule('/canales', 'canales', view_func=views.canales, methods=['GET', 'POST'])

# Spintvs API page
app.add_url_rule('/api', 'api', view_func=views.api, methods=['GET', 'POST'])

# Apps page
app.add_url_rule('/apps', 'apps', view_func=views.apps, methods=['GET', 'POST'])

# MiTele and Mediaset special page
app.add_url_rule('/mitele', 'mitele', view_func=views.mitele, methods=['GET', 'POST'])
app.add_url_rule('/mediaset', 'mediaset', view_func=views.mediaset, methods=['GET', 'POST'])

# Iframe embed content
app.add_url_rule('/embed', 'embed', view_func=views.embed, methods=['GET', 'POST'])

# Legal page
app.add_url_rule('/legal', 'legal', view_func=views.legal, methods=['GET', 'POST'])

# Privacy page
app.add_url_rule('/privacidad', 'privacidad', view_func=views.privacidad, methods=['GET', 'POST'])

# Say hello
app.add_url_rule('/hello/<username>', 'say_hello', view_func=views.say_hello)

# Rest get URL format home
app.add_url_rule('/url/<path:url>', 'rest_url_home', view_func=views.rest_url_home)

# Rest get URL format API
app.add_url_rule('/api/<path:url>', 'rest_url_api', view_func=views.rest_url_api)

app.add_url_rule('/atresplayer/checker', 'rest_a3p_checker', view_func=views.rest_a3p_checker)

#Utils
app.add_url_rule('/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzE/<episode>', 'utils1', view_func=utils.random1)
app.add_url_rule('/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzM/<episode>', 'utils3', view_func=utils.random3)
app.add_url_rule('/utils/YXRyZXNwbGF5ZXJfcmFuZG9tXzI/<path:toenc>', 'utils2', view_func=utils.random2)
app.add_url_rule('/utils/cnR2ZV9yYW5kb21fNA/', 'utils4', view_func=utils.random4, methods=['POST'])


# Examples list page
#app.add_url_rule('/examples', 'list_examples', view_func=views.list_examples, methods=['GET', 'POST'])

# Contrived admin-only view example
#app.add_url_rule('/admin_only', 'admin_only', view_func=views.admin_only)

# Delete an example (post method only)
#app.add_url_rule('/examples/delete/<int:example_id>', view_func=views.delete_example, methods=['POST'])


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

## Other handlers
@app.before_request
def change_request_url():
	#request.headers['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
	#return request.headers.get('User-Agent')
	if request.url.find("http://localhost:") != -1:
		pass
	elif request.url.find("pydowntv.appspot.com") != -1:
		pass
	elif request.url.find("pydowntv2.appspot.com") != -1:
		pass
	elif request.url.find("://web.pydowntv.") != -1:
		return redirect(request.url.replace("://web.pydowntv.", "://www.pydowntv."))
	else:
		pass

import urllib
from markupsafe import Markup
@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)

import re
@app.template_filter('rtmpdownloadid')
def rtmpdownloadid_filter(s):
	return urlencode_filter("http://descargavideos.tv/mitele_handler.php?rtmp&id=" + re.findall("slist=1(.*?).mp4",s)[1]+".mp4")

@app.template_filter('rtmpdownloadnoexec')
def rtmpdownloadnoexec_filter(s):
	return urlencode_filter(s.replace('rtmpdump ','')) #" ".join(s.split()[1:])





