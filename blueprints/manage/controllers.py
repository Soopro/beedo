# coding=utf-8
from __future__ import absolute_import

from flask import (current_app, g, session, redirect, url_for, request,
                   flash, render_template)

from models import Entry
from utils.misc import hmac_sha, process_slug
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
    identity = request.form['identity']
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
    return render_template('dashboard.html', count=count)


# entry
@blueprint.route('/entries')
@login_required
def entries():
    entries = []
    statics = []
    for k, v in g.files.iteritems():
        if k in current_app.config['STATIC_FILENAME']:
            statics.append(v)
        else:
            entries.append(v)
    entries = sorted(entries, key=lambda k: k['_id'])
    return render_template('entries.html', entries=entries, statics=statics)


@blueprint.route('/entry')
@blueprint.route('/entry/<_id>')
@login_required
def entry(_id=None):
    entry = g.files.get(_id, {})
    return render_template('entry.html', entry=entry)


@blueprint.route('/entry', methods=['POST'])
@login_required
def add_entry():
    fname = request.form['filename']
    rtype = request.form['type']
    keys = request.form['keywords']
    text = request.form.get('text', u'')
    status = request.form.get('status', 0)

    _id = '.md'.format(process_slug(fname))
    if g.files.get(_id):
        raise Exception('Entry duplicated.')

    entry = Entry({
        '_id': _id,
        'type': rtype,
        'keywords': _parse_input_keys(keys),
        'status': status,
        'text': text,
        'messages': [],
    })
    entry.save()

    return_url = url_for('.entry', _id=entry['_id'])
    return redirect(return_url)


@blueprint.route('/entry/<_id>', methods=['POST'])
@login_required
def update_entry(_id):
    rtype = request.form['type']
    keys = request.form['keywords']
    text = request.form.get('text', u'')
    status = request.form.get('status', 0)

    entry = g.files.get(_id)
    if not entry:
        raise Exception('Entry not found.')

    entry['type'] = rtype
    entry['keywords'] = _parse_input_keys(keys)
    entry['status'] = status
    entry['text'] = text
    entry.save()

    return_url = url_for('.entry', _id=entry['_id'])
    return redirect(return_url)


@blueprint.route('/entry/<_id>/message', methods=['POST'])
@login_required
def add_entry_message(_id):
    title = request.form.get('title', u'')
    description = request.form.get('description', u'')
    picurl = request.form.get('picurl', u'')
    url = request.form.get('url', u'')

    entry = g.files.get(_id)
    if not entry:
        raise Exception('Entry not found.')
    if len(entry['messages']) >= 8:
        raise Exception('Too many messages.')

    entry['messages'].append({
        'title': title,
        'description': description,
        'picurl': picurl,
        'url': url
    })
    entry.save()

    return_url = url_for('.entry', _id=entry['_id'])
    return redirect(return_url)


@blueprint.route('/entry/<_id>/message/<idx>', methods=['POST'])
@login_required
def edit_entry_message(_id, idx):
    title = request.form.get('title', u'')
    description = request.form.get('description', u'')
    picurl = request.form.get('picurl', u'')
    url = request.form.get('url', u'')

    entry = g.files.get(_id)
    if not entry:
        raise Exception('Entry not found.')
    try:
        entry['messages'][idx] = {
            'title': title,
            'description': description,
            'picurl': picurl,
            'url': url
        }
    except IndexError:
        raise Exception('Message index out of range.')

    entry.save()

    return_url = url_for('.entry', _id=entry['_id'])
    return redirect(return_url)


@blueprint.route('/entry/<_id>/message/<idx>/del')
@login_required
def del_entry_message(_id, idx):
    entry = g.files.get(_id)
    if not entry:
        raise Exception('Entry not found.')
    try:
        entry['messages'].pop(idx)
    except IndexError:
        raise Exception('Message index out of range.')

    entry.save()

    return_url = url_for('.entry', _id=entry['_id'])
    return redirect(return_url)


@blueprint.route('/entry/<_id>/remove')
@login_required
def remove_entry(_id):
    entry = g.files.pop(_id, None)
    if not entry:
        raise Exception('Entry not found.')
    entry.delete()

    return_url = url_for('.entries')
    return redirect(return_url)


# helpers
def _parse_input_keys(keys):
    keys = keys.split('|')
    return [k.lower().strip() for k in keys]
