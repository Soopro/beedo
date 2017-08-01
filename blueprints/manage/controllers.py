# coding=utf-8
from __future__ import absolute_import

from flask import (current_app, g, session, redirect, url_for, request,
                   flash, render_template)

from utils.misc import hmac_sha, process_slug, parse_int
from decorators import login_required
from .main import blueprint


# auth
@blueprint.route('/auth')
def auth():
    if session.get('identity'):
        return redirect(url_for('.dashboard'))
    return render_template('auth.html')


@blueprint.route('/login', methods=['POST'])
def login():
    identity = request.args['identity']
    if identity != current_app.config['IDENTITY']:
        flash('Invalid identity.', 'error')
        return redirect(url_for('.auth'))
    else:
        session['identity'] = hmac_sha(current_app.secret_key, identity)
        return redirect(url_for('.dashboard'))


@blueprint.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('.auth'))


# dashboard
@blueprint.route('')
@login_required
def dashboard():
    count = len(g.files)
    entries = []
    statics = []
    for f in g.files:
        if f['slug'] in current_app.config['STATIC_SLUGS']:
            statics.append(f)
        else:
            entries.append(f)
    entries = sorted(entries, key=lambda k: k['slug'])
    return render_template('dashboard.html', count=count,
                           entries=entries, statics=statics)


@blueprint.route('/entry')
@blueprint.route('/entry/<slug>')
@login_required
def entry(slug=None):
    entry = g.files.get(slug, {})
    return render_template('entry.html', entry=entry)


@blueprint.route('/entry', methods=['POST'])
@login_required
def add_entry():
    slug = request.form['slug']
    rtype = request.form['rtype']
    keys = request.form['keys']
    text = request.form.get('text', u'')
    status = request.form.get('status', 0)

    if g.files.get(slug):
        raise Exception('Entry duplicated.')

    entry = {
        'slug': process_slug(slug),
        'type': rtype,
        'keys': _parse_input_keys(keys),
        'status': status,
        'text': text,
        'messages': [],
    }
    return_url = url_for('.entry', slug=entry['slug'])
    return redirect(return_url)


@blueprint.route('/entry/<slug>', methods=['POST'])
@login_required
def update_entry(slug):
    rtype = request.form['rtype']
    keys = request.form['keys']
    text = request.form.get('text', u'')
    status = request.form.get('status', 0)

    entry = g.files.get(slug)
    if not entry:
        raise Exception('Entry not found.')

    entry['type'] = rtype
    entry['keys'] = _parse_input_keys(keys)
    entry['status'] = status
    entry['text'] = text

    return_url = url_for('.entry', slug=entry['slug'])
    return redirect(return_url)


@blueprint.route('/entry/<slug>/message', methods=['POST'])
@login_required
def add_entry_message(slug):
    title = request.form.get('title', u'')
    description = request.form.get('description', u'')
    picurl = request.form.get('picurl', u'')
    url = request.form.get('url', u'')
    pos = request.form.get('pos', u'')

    entry = g.files.get(slug)
    if not entry:
        raise Exception('Entry not found.')

    entry['messages'].insert(parse_int(pos), {
        'title': title,
        'description': description,
        'picurl': picurl,
        'url': url
    })

    return_url = url_for('.entry', slug=entry['slug'])
    return redirect(return_url)


@blueprint.route('/entry/<slug>/message/<idx>/del')
@login_required
def del_entry_message(slug, idx):
    entry = g.files.get(slug)
    if not entry:
        raise Exception('Entry not found.')
    try:
        entry['messages'].pop(idx)
    except IndexError:
        raise Exception('Message index out of range.')

    return_url = url_for('.entry', slug=entry['slug'])
    return redirect(return_url)


@blueprint.route('/entry/<slug>/remove')
@login_required
def remove_entry(slug):
    entry = g.files.pop(slug, None)
    if not entry:
        raise Exception('Entry not found.')
    return_url = url_for('.entries')
    return redirect(return_url)


# helpers
def _parse_input_keys(keys):
    keys = keys.split('|')
    return [k.lower().strip() for k in keys]
