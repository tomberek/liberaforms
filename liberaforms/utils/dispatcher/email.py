"""
This file is part of LiberaForms.

# SPDX-FileCopyrightText: 2021 LiberaForms.org
# SPDX-License-Identifier: AGPL-3.0-or-later
"""

import os, traceback
import smtplib, ssl
from flask import current_app
from email.utils import formatdate, make_msgid


class EmailServer():
    connection = None
    username = None
    password = None
    timeout = 7

    def __init__(self, site):
        self.host = site.smtpConfig['host']
        self.port = site.smtpConfig['port']
        self.use_ssl = True if site.smtpConfig['encryption'] == 'SSL' else False
        self.use_tls = True if site.smtpConfig['encryption'] == 'STARTTLS' else False
        self.username = site.smtpConfig['user']
        self.password = site.smtpConfig['password']
        self.default_sender = site.smtpConfig['noreplyAddress']

    def open_connection(self):
        if self.use_ssl:
            try:
                self.connection = smtplib.SMTP_SSL( host=self.host,
                                                    port=self.port,
                                                    timeout=self.timeout)
                self.connection.login(self.username, self.password)
            except Exception as error:
                current_app.logger.warning(traceback.format_exc())
                self.connection = None
                return error
        elif self.use_tls:
            try:
                self.connection = smtplib.SMTP( host=self.host,
                                                port=self.port,
                                                timeout=self.timeout)
                context = ssl.create_default_context()
                self.connection.ehlo()
                self.connection.starttls(context=context)
                self.connection.ehlo()
                self.connection.login(self.username, self.password)
            except Exception as error:
                current_app.logger.warning(traceback.format_exc())
                self.connection = None
                return error
        else:
            try:
                self.connection = smtplib.SMTP( host=self.host,
                                                port=self.port,
                                                timeout=self.timeout)
                if self.username and self.password:
                    self.connection.login(self.username, self.password)
            except Exception as error:
                current_app.logger.warning(traceback.format_exc())
                self.connection = None
                return error

    def close_connection(self):
        """Closes the connection with the email server."""
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the connection.
                self.connection.close()
            except smtplib.SMTPException as e:
                current_app.logger.warning(traceback.format_exc())
        finally:
            self.connection = None

    def send_mail(self, msg):
        if 'SKIP_EMAILS' in os.environ and os.environ['SKIP_EMAILS'] == 'True':
            # TESTING environment sets 'SKIP_EMAILS'
            return {
                "email_sent": True
            }
        exception = self.open_connection()
        if exception:
            return {
                "email_sent": False,
                "msg": str(exception)
            }
        if self.connection:
            msg = self.prep_message(msg)
            try:
                self.connection.sendmail(msg['From'],
                                         msg['To'],
                                         msg.as_string())
                self.close_connection()
                return {
                    "email_sent": True
                }
            except Exception as error:
                current_app.logger.warning(traceback.format_exc())
                return {
                    "email_sent": False,
                    "msg": str(error)
                }
        return {
            "email_sent": False,
            "msg": f"Cannot connect to {self.host}"
        }

    def send_mail_async(self, app, msg):
        with app.app_context():
            return self.send_mail(msg)

    def prep_message(self, msg):
        msg['From'] = self.default_sender
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid()
        """
        admins=User.find_all(isAdmin=True)
        if admins:
            msg['Errors-To'] = admins[0].email
        """
        return msg
