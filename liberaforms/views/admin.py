"""
This file is part of LiberaForms.

# SPDX-FileCopyrightText: 2020 LiberaForms.org
# SPDX-License-Identifier: AGPL-3.0-or-later
"""

import os, json
from flask import g, request, render_template, redirect
from flask import session, flash, Blueprint
from flask import send_file, after_this_request
from flask_babel import gettext

from liberaforms.models.user import User
from liberaforms.models.form import Form
from liberaforms.models.site import Site, Invite, Installation
from liberaforms.utils.wraps import *
from liberaforms.utils.utils import make_url_for, JsonResponse
from liberaforms.utils.email import EmailServer
import liberaforms.utils.wtf as wtf

#from pprint import pprint as pp

admin_bp = Blueprint('admin_bp', __name__,
                    template_folder='../templates/admin')


@admin_bp.route('/admin', methods=['GET'])
@admin_required
def site_admin():
    sites = Site.objects() if g.current_user.is_root_user() else None
    context = {
        'site': g.site,
        'sites': sites,
        'installation': Installation.get()
    }
    return render_template('admin-panel.html', user=g.current_user, **context)

""" User management """

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def list_users():
    return render_template('list-users.html',
                            users=User.find_all(),
                            invites=Invite.find_all()) 

@admin_bp.route('/admin/users/<string:id>', methods=['GET'])
@admin_required
def inspect_user(id):
    user=User.find(id=id)
    if not user:
        flash(gettext("User not found"), 'warning')
        return redirect(make_url_for('admin_bp.list_users'))
    return render_template('inspect-user.html', user=user) 


@admin_bp.route('/admin/users/toggle-blocked/<string:id>', methods=['POST'])
@admin_required
def toggle_user_blocked(id):       
    user=User.find(id=id)
    if not user:
        return JsonResponse(json.dumps())
    if user.id == g.current_user.id:
        # current_user cannot disable themself
        blocked=user.blocked
    else:
        blocked=user.toggle_blocked()
    return JsonResponse(json.dumps({'blocked':blocked}))


@admin_bp.route('/admin/users/toggle-admin/<string:id>', methods=['POST'])
@admin_required
def toggle_admin(id):       
    user=User.find(id=id)
    if not user:
        return JsonResponse(json.dumps())
    if user.username == g.current_user.username:
        # current_user cannot remove their own admin permission
        is_admin=True
    else:
        is_admin=user.toggle_admin()
    return JsonResponse(json.dumps({'admin':is_admin}))


@admin_bp.route('/admin/users/delete/<string:id>', methods=['GET', 'POST'])
@admin_required
def delete_user(id):       
    user=User.find(id=id)
    if not user:
        flash(gettext("User not found"), 'warning')
        return redirect(make_url_for('admin_bp.list_users'))
  
    if request.method == 'POST' and 'username' in request.form:
        if user.is_root_user():
            flash(gettext("Cannot delete root user"), 'warning')
            return redirect(make_url_for('admin_bp.inspect_user', id=user.id)) 
        if user.id == g.current_user.id:
            flash(gettext("Cannot delete yourself"), 'warning')
            return redirect(make_url_for('admin_bp.inspect_user', username=user.username)) 
        if user.username == request.form['username']:
            user.delete_user()
            flash(gettext("Deleted user '%s'" % (user.username)), 'success')
            return redirect(make_url_for('admin_bp.list_users'))
        else:
            flash(gettext("Username does not match"), 'warning')
    return render_template('delete-user.html', user=user)


@admin_bp.route('/admin/users/csv', methods=['GET'])
@admin_required
def csv_users():
    csv_file = g.site.write_users_csv()
    @after_this_request 
    def remove_file(response): 
        os.remove(csv_file) 
        return response
    return send_file(csv_file, mimetype="text/csv", as_attachment=True)
    

""" Form management """

@admin_bp.route('/admin/forms', methods=['GET'])
@admin_required
def list_forms():
    return render_template('list-forms.html', forms=Form.find_all()) 


@admin_bp.route('/admin/forms/toggle-public/<string:id>', methods=['GET'])
@admin_required
def toggle_form_public_admin_prefs(id):
    queriedForm = Form.find(id=id)
    if not queriedForm:
        flash(gettext("Can't find that form"), 'warning')
        return redirect(make_url_for('form_bp.my_forms'))
    queriedForm.toggle_admin_form_public()
    return redirect(make_url_for('form_bp.inspect_form', id=id))


@admin_bp.route('/admin/forms/change-author/<string:id>', methods=['GET', 'POST'])
@admin_required
def change_author(id):
    queriedForm = Form.find(id=id)
    if not queriedForm:
        flash(gettext("Can't find that form"), 'warning')
        return redirect(make_url_for('user_bp.my_forms'))
    if request.method == 'POST':
        author = queriedForm.get_author()
        if not ('old_author_username' in request.form and \
                request.form['old_author_username']==author.username):
            flash(gettext("Current author incorrect"), 'warning')
            return render_template('change-author.html', form=queriedForm)
        if 'new_author_username' in request.form:
            new_author=User.find(username=request.form['new_author_username'], hostname=queriedForm.hostname)
            if new_author:
                if new_author.enabled:
                    old_author=author
                    if queriedForm.change_author(new_author):
                        queriedForm.add_log(gettext("Changed author from %s to %s" % (old_author.username, new_author.username)))
                        flash(gettext("Changed author OK"), 'success')
                        return redirect(make_url_for('form_bp.inspect_form', id=queriedForm.id))
                else:
                    flash(gettext("Cannot use %s. The user is not enabled" % (request.form['new_author_username'])), 'warning')
            else:
                flash(gettext("Can't find username %s" % (request.form['new_author_username'])), 'warning')
    return render_template('change-author.html', form=queriedForm)


""" Invitations """

@admin_bp.route('/admin/invites', methods=['GET'])
@admin_required
def list_invites():
    return render_template('list-invites.html', invites=Invite.find_all())


@admin_bp.route('/admin/invites/new', methods=['GET', 'POST'])
@admin_required
def new_invite():
    wtform=wtf.NewInvite()
    if wtform.validate_on_submit():  
        message=wtform.message.data
        invite=Invite.create(wtform.hostname.data, wtform.email.data, message, wtform.admin.data)
        EmailServer().sendInvite(invite)
        flash(gettext("We've sent an invitation to %s") % invite.email, 'success')
        return redirect(make_url_for('admin_bp.list_invites'))
    wtform.message.data=Invite.default_message()
    return render_template('new-invite.html',
                            wtform=wtform,
                            total_invites=Invite.find_all().count(),
                            sites=Site.find_all())


@admin_bp.route('/admin/invites/delete/<string:id>', methods=['GET'])
@admin_required
def delete_invite(id):
    invite=Invite.find(id=id)
    if invite:
        invite.delete()
        flash(gettext("Invitation to {} deleted OK".format(invite.email)), 'success')
    else:
        flash(gettext("Opps! We can't find that invitation"), 'error')
    return redirect(make_url_for('admin_bp.list_invites'))


""" Personal Admin preferences """

@admin_bp.route('/admin/toggle-newuser-notification', methods=['POST'])
@admin_required
def toggle_newUser_notification(): 
    return json.dumps({'notify': g.current_user.toggle_new_user_notification()})


@admin_bp.route('/admin/toggle-newform-notification', methods=['POST'])
@admin_required
def toggle_newForm_notification(): 
    return json.dumps({'notify': g.current_user.toggle_new_form_notification()})
