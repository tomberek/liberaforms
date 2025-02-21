"""
This file is part of LiberaForms.

# SPDX-FileCopyrightText: 2021 LiberaForms.org
# SPDX-License-Identifier: AGPL-3.0-or-later
"""

import os
import pytest
from flask import g
from liberaforms.models.user import User
from .utils import login

class TestSharedForm():
    def test_access_shared_forms(self, client, anon_client, users, forms):
        login(client, users['editor'])
        form_id=forms['test_form'].id
        url = f"/forms/share/{form_id}"
        response = anon_client.get(
                        url,
                        follow_redirects=True,
                    )
        assert response.status_code == 200
        html = response.data.decode()
        assert '<!-- site_index_page -->' in html
        response = client.get(
                        url,
                        follow_redirects=False,
                    )
        assert response.status_code == 200
        html = response.data.decode()
        assert '<!-- share_form_page -->' in html
        assert f'"/forms/add-editor/{form_id}" method="POST"' in html
        assert f'"/forms/add-shared-notification/{form_id}" method="POST"' in html
        assert '<div id="enabled_links" style="display:None">' in html

    def test_add_editor(self, client, users, forms):
        form_id=forms['test_form'].id
        initial_log_count = forms['test_form'].log.count()
        nonexistent_user_email = "nonexistent@example.com"
        response = client.post(
                        f"/forms/add-editor/{form_id}",
                        data = {
                            "email": nonexistent_user_email,
                        },
                        follow_redirects=True,
                    )
        assert response.status_code == 200
        html = response.data.decode()
        assert f'"/forms/add-editor/{form_id}" method="POST"' in html
        assert forms['test_form'].log.count() == initial_log_count
        # make the dummy_1 user a new editor
        dummy_1 = User.find(username=users['dummy_1']['username'])
        existent_user_email = dummy_1.email
        response = client.post(
                        f"/forms/add-editor/{form_id}",
                        data = {
                            "email": existent_user_email,
                        },
                        follow_redirects=True,
                    )
        assert response.status_code == 200
        html = response.data.decode()
        assert f'"/forms/add-editor/{form_id}" method="POST"' in html
        assert existent_user_email in html
        assert forms['test_form'].log.count() == initial_log_count + 1

    def test_add_shared_notification(self, client, forms):
        form_id=forms['test_form'].id
        url = f"/forms/add-shared-notification/{form_id}"
        invalid_email = "invalid@domain"
        valid_email = "valid@domain.com"
        response = client.post(
                        url,
                        data = {
                            "email": invalid_email,
                        },
                        follow_redirects=True,
                    )
        assert response.status_code == 200
        html = response.data.decode()
        assert '<!-- share_form_page -->' in html
        assert valid_email not in html
        initial_log_count = forms['test_form'].log.count()
        response = client.post(
                        url,
                        data = {
                            "email": valid_email,
                        },
                        follow_redirects=True,
                    )
        assert response.status_code == 200
        html = response.data.decode()
        assert '<!-- share_form_page -->' in html
        assert valid_email in html
        assert valid_email in forms['test_form'].shared_notifications
        assert forms['test_form'].log.count() == initial_log_count + 1

    def test_remove_shared_notification(self, anon_client, client, users, forms):
        form_id=forms['test_form'].id
        initial_log_count = forms['test_form'].log.count()
        url = f"/forms/remove-shared-notification/{form_id}"
        shared_with_email = forms['test_form'].shared_notifications[0]
        response = client.post(
                        url,
                        data = {
                            "email": shared_with_email,
                        },
                        follow_redirects=True,
                    )
        assert response.status_code == 200
        assert response.is_json == True
        assert response.json == True
        assert shared_with_email not in forms['test_form'].shared_notifications
        assert forms['test_form'].log.count() == initial_log_count + 1

    def test_toggle_shared_answers(self, client, users, forms):
        form_id=forms['test_form'].id
        initial_enabled = forms['test_form'].sharedAnswers['enabled']
        initial_log_count = forms['test_form'].log.count()
        response = client.post(
                        f"/form/toggle-shared-answers/{form_id}",
                        follow_redirects=False,
                    )
        assert response.status_code == 200
        assert response.is_json == True
        assert forms['test_form'].sharedAnswers['enabled'] != initial_enabled
        assert response.json['enabled'] == forms['test_form'].sharedAnswers['enabled']
        assert forms['test_form'].log.count() == initial_log_count + 1

    def test_toggle_restricted_form_access(self, client, forms):
        form_id=forms['test_form'].id
        initial_restriced_access = forms['test_form'].restrictedAccess
        initial_log_count = forms['test_form'].log.count()
        response = client.post(
                        f"/form/toggle-restricted-access/{form_id}",
                        follow_redirects=False,
                    )
        assert response.status_code == 200
        assert response.is_json == True
        assert response.json['restricted'] == True
        assert forms['test_form'].restrictedAccess == True
        assert forms['test_form'].log.count() == initial_log_count + 1
