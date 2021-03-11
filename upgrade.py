"""
This file is part of LiberaForms.

# SPDX-FileCopyrightText: 2020 LiberaForms.org
# SPDX-License-Identifier: AGPL-3.0-or-later
"""

from liberaforms import app
from migrate_db import migrate_db
import sys, os, shutil, subprocess

print("Have you backed up the database? yes/no")
choice = input().lower()
if choice != "yes":
   sys.exit()

rolled_back=False
git_pulled=False
pip_upgraded=False
db_up_to_date=False

# create a rollback directory
liberaforms_dir=os.path.dirname(os.path.abspath(__file__))
rollback_dir=os.path.join(liberaforms_dir, 'rollback')
dest_dir=os.path.join(rollback_dir, app.config['APP_VERSION'])

print("Creating rollback of LiberaForms version {} at {}".format(app.config['APP_VERSION'], dest_dir))
if not os.path.isdir(dest_dir):
    try:
        shutil.copytree(liberaforms_dir, dest_dir, ignore=shutil.ignore_patterns("rollback", "flask_session"))
        rolled_back=True
        print("OK")
    except Exception as e:
        print(e)
else:
    rolled_back=True
    print("(directory already exists)")

if rolled_back:
    print("\nPulling code from git repository..")
    try:
        process = subprocess.run(   ["git", "pull", "origin", "main"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.stderr:
            print(process.stderr.decode())
        else:
            git_pulled=True
            print(process.stdout.decode())
    except Exception as e:
        print(e)

if git_pulled:
    print("Updating python libraries with pip..")
    try:
        pip_setuptools = subprocess.run(["pip", "install", "--upgrade", "setuptools"],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pip_install = subprocess.run(["pip", "install", "-r", os.path.join(liberaforms_dir, 'requirements.txt')],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pip_setuptools.stderr or pip_install.stderr:
            if pip_setuptools.stderr:
                print(pip_setuptools.stderr.decode())
            if pip_install.stderr:
                print(pip_install.stderr.decode())
        else:
            pip_upgraded=True
            print("OK")
    except Exception as e:
        print(e)

if pip_upgraded:
    print("\nMigrating the database..")
    db_up_to_date=migrate_db()

if db_up_to_date:
    print("\nUpgrade completed OK.")
