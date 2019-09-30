"""
“Copyright 2019 La Coordinadora d’Entitats per la Lleialtat Santsenca”

This file is part of GNGforms.

GNGforms is free software: you can redistribute it and/or modify
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

from GNGforms import app, mongo
import pprint

def migrateMongoSchema():
    
    # changes in schema version 2
    # replace "expireDate" for "expiryConditions"
    try:
        for form in mongo.db.forms.find():
            if 'expireDate' in form:
                expireDate=form['expireDate']
                #del form['expireDate']
                form["expiryConditions"] = {}
                form["expiryConditions"]["expireDate"]=expireDate
                mongo.db.forms.update_one({"_id": form["_id"]}, {"$unset": {'expireDate' :1}})
                pprint.pprint(form)
            else:
                break
    except:
        return None
        
    return 2
