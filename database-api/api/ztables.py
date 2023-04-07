from sqlalchemy.sql import func
from flask import Flask, request, jsonify

# DESI software
import desispec.database.redshift as db
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

#Flask Setup
from app import app
from .utils import filter_query

# Flask API Endpoints
@app.route('/api/table/<table>', methods=['POST'])
def queryTable(table):
    """ 
    @Params: 
        table (STRING): Table to query (either zpix or ztile)
        body (DICT): Contains query parameters.
            MUST CONTAIN: columns(LIST(STRINGS)) = List of Strings specifying columns of table to return in query
            OPTIONAL: (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), subtype(STRING), 
                       z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object (targetID, redshift) containing the targetIDs and associated 
                  redshifts for targets found in provided tileID.     
    """
    return jsonify('Unsopported Feature')


def queryZpix(body):
    return jsonify('Unsopported Feature')


def queryZtile(body):
    return jsonify('Unsopported Feature')
