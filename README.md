# **G**NGforms is **N**ot **G**oogle forms

We have built this software with the hope it will be used by our neighbours, friends, and anyone else who feels GAFAM already has way to much data on **all** of us.

Don't feed the Dictator!

Please read INSTALL.txt for installation instructions.

At the center of GNGforms is the WYSIWYG web form creator [formbuilder](https://formbuilder.online/). Users build a form, choose a URL slug, and publish it.

## Resources
We'd like to think that sharing resources makes things easier, so GNGforms has been built to share server infraestructure with others. One server can serve multiple domains. An nginx proxy in front of GNGforms routes the domains you choose to the gunicorn process.

One installation, one database, one monitoring and one backup system mean less work for sysadmins too!

## Config
Copy `config.example.cfg` to `config.cfg`. The configuration option are pretty straight forward.

ROOT_USERS is a list of emails. Users with these emails are "Root users".

## User profiles
**Anonymous users**:
 * Can fill out published forms
 
**Normal registered users:**
 * Can create and publish forms.
 * Can edit collected data on the web interface
 * Download collected form data in CSV
 * Share edit permission with other users on the site
 * Set some basic expiry conditions.
 * And other stuff

**Admins:**
 * Edit frontpage text
 * Invite new users to the site
 * Enable and disable users.
 * Give/remove admin permissions to users
 * Read all forms
 * Delete users and their forms
 * Site configuration. Invite only, Data protection text, smtp config, etc.
 * Admins **cannot** read collected data of other users' forms

GNGforms can serve multiple sites.

**Root users:**
 * Bootstrap the first Admin of a new site
 * Have the same permissions as admins across **all sites**.

## Bootstrapping root_users
1. From the index page, choose 'Forgot your password?' link.
2. Enter an email defined as a root_user in the config.cfg
3. Fill out the new user form.
4. Go to the configuration page and get the SMTP config working first.

## Bootstrapping a second site
1. Get your friend to point their subdomain to your server IP.
2. Configure nginx proxy to direct traffic to the running gunicorn process.
3. Go to your config page and send the person you know an Admin invitation for the new site.
4. Tell them to go to the configuration page and get the SMTP config working first.

New user invitations, and password restore emails, expire in 24 hours. You can change that in the config.cfg

