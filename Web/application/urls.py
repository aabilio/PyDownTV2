# -*- coding: utf-8 -*-
"""
urls.py

URL dispatch route mappings and error handlers

"""

from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', 'home', view_func=views.home, methods=['GET', 'POST'])

# Help Page
app.add_url_rule('/ayuda', 'ayuda', view_func=views.ayuda, methods=['GET', 'POST'])

# Channels Page
app.add_url_rule('/canales', 'canales', view_func=views.canales, methods=['GET', 'POST'])

# Spintvs API page
app.add_url_rule('/api', 'api', view_func=views.api, methods=['GET', 'POST'])

# Apps page
app.add_url_rule('/apps', 'apps', view_func=views.apps, methods=['GET', 'POST'])

# Legal page
app.add_url_rule('/legal', 'legal', view_func=views.legal, methods=['GET', 'POST'])

# Say hello
app.add_url_rule('/hello/<username>', 'say_hello', view_func=views.say_hello)

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

