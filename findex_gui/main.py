import os
from flask import render_template, request, flash, session, redirect, url_for, send_from_directory, abort
from findex_gui import app, settings, themes
from forms import ContactForm
from orm.models import Users, Files
from findex_gui import db
from flaskext.auth import Auth, AuthUser, login_required, logout


@app.route('/')
def root():
    return themes.render('main/home')


@app.errorhandler(404)
def error(e):
    return themes.render('main/error', msg=str(e))


# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     form = ContactForm()
#
#     if request.method == 'POST':
#         if not form.validate():
#             flash(form.validate())
#             return render_template('contact.html', form=form)
#         else:
#             return 'Form posted.'
#     elif request.method == 'GET':
#         return render_template('contact.html', form=form)