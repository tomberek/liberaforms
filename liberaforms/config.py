"""
“Copyright 2020 LiberaForms.org”

This file is part of LiberaForms.

LiberaForms is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""

DO NOT edit this file.

You can copy values from the 'DefaultConfig' class and
 * paste them into your config.cfg or
 * export them as ENV variables before running flask

"""

import os, shutil

"""
Managed environment variables
"""
ENV_VARIABLES = [
    'SECRET_KEY',
    'FLASK_RUN_HOST',
    'FLASK_RUN_PORT',
    'FLASK_DEBUG',
    'ROOT_USERS',
    'MONGODB_DB',
    'MONGODB_HOST',
    'MONGODB_PORT',
    'MONGODB_USERNAME',
    'MONGODB_PASSWORD'
]

class DefaultConfig(object):
    # Required config:
    # SECRET_KEY = 'super secret key'
    # ROOT_USERS = ['your_email_address@example.com']
    # MONGODB_HOST = '127.0.0.1'
    # MONGODB_PORT = 27017
    # MONGODB_DB = 'liberaforms'
    # MONGODB_USERNAME = 'webapp'
    # MONGODB_PASSWORD = 'pwd123'

    """
    User overridable settings with their sensible defaults.
    """
    
    # Optional config:
    DEFAULT_LANGUAGE = "en"
    TMP_DIR = "/tmp"

    # Session management (see docs/INSTALL)
    SESSION_TYPE = "filesystem"
    #SESSION_TYPE = "memcached"

    # 3600 seconds = 1hrs. Time to fill out a form.
    # This number must be less than PERMANENT_SESSION_LIFETIME (see below)
    WTF_CSRF_TIME_LIMIT = 21600
    
    # User sessions last 8h (refreshed on every request)
    PERMANENT_SESSION_LIFETIME = 28800
    
    # 86400 seconds = 24h ( token are used for password resets, invitations, ..)
    TOKEN_EXPIRATION = 604800
    
    # formbuilder
    FORMBUILDER_CONTROL_ORDER = ["header", "paragraph"]

    # Extra configuration to be merged with standard config
    EXTRA_RESERVED_SLUGS = []
    EXTRA_RESERVED_USERNAMES = []


class InternalConfig(object):
    """
    Internal settings that cannot be overridden.
    """

    SCHEMA_VERSION = 24

    RESERVED_SLUGS = [
        "login",
        "logout",
        "admin", "admins",
        "user", "users",
        "form", "forms",
        "site", "sites",
        "profile",
        "update",
        "embed",
        "api",
        "static",
        "upload", "uploads",
        "logo", "favicon.ico",
    ]
    # DPL = Data Protection Law
    RESERVED_FORM_ELEMENT_NAMES = [
        "marked",
        "created",
        "csrf_token",
        "DPL",
        "id",
        "checked",
        "sendConfirmation"
    ]
    RESERVED_USERNAMES = ["system", "admin", "root"]
    
    #CONDITIONAL_FIELD_TYPES = ['select']

    FORMBUILDER_DISABLED_ATTRS = ["className", "toggle", "access"]
    FORMBUILDER_DISABLE_FIELDS = ["autocomplete", "hidden", "button", "file"]

    BABEL_TRANSLATION_DIRECTORIES = "translations;form_templates/translations"
    # http://www.lingoes.net/en/translator/langcode.htm
    LANGUAGES = {
        "en": ("English", "en-US"),
        "ca": ("Català", "ca-ES"),
        "es": ("Castellano", "es-ES"),
        "eu": ("Euskara ", "eu-ES"),
    }


def default_instance_setup(app):
    # create config.cfg if not present
    config_file=os.path.join(app.instance_path, 'config.cfg')
    if not os.path.isfile(config_file):
        os.makedirs(app.instance_path, exist_ok=True)
        example_cfg = os.path.join(app.root_path, 'config.example.cfg')
        shutil.copyfile(example_cfg, config_file)
    # create 'branding' dir if not present
    branding_dir = os.path.join(app.instance_path, 'branding')
    if not os.path.isdir(branding_dir):
        os.makedirs(branding_dir, exist_ok=True)

def load_env_variables(app, env):
    for variable in ENV_VARIABLES:
        if variable in env:
            app.config[variable] = env[variable]
