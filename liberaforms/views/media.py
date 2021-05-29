"""
This file is part of LiberaForms.

# SPDX-FileCopyrightText: 2021 LiberaForms.org
# SPDX-License-Identifier: AGPL-3.0-or-later
"""

import json, logging
from flask import g, request, render_template, redirect
from flask import Blueprint, current_app
from flask import flash
from flask_babel import gettext as _

from liberaforms.models.media import Media
from liberaforms.utils.wraps import *
from liberaforms.utils.utils import make_url_for, JsonResponse
from liberaforms.utils import validators

from pprint import pprint

media_bp = Blueprint('media_bp',
                    __name__,
                    template_folder='../templates/media')


@media_bp.route('/media/save', methods=['POST'])
@enabled_user_required
def save_image():
    if not (current_app.config['ENABLE_UPLOADS'] and request.files['file']):
        return JsonResponse(json.dumps({"image_url": ""}))
    # TODO: check mimetype and size first
    media = Media()
    saved = media.save_media(g.current_user,
                             request.files['file'],
                             request.form['alt_text'])
    url = media.get_url()

    return JsonResponse(json.dumps({"image_url": url}))


@media_bp.route('/media/list/<string:username>', methods=['GET'])
@enabled_user_required
def list_media(username):
    return render_template('list-media.html')
