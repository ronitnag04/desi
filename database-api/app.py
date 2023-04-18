from flask import Flask

# DESI software
import desispec.database.redshift as db
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

#Flask Setup
app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=False)

import api.generic
import api.loc
import api.multispectra
import gui.display
import gui.multispectra
