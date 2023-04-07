from sqlalchemy.sql import func
from flask import request, jsonify

# DESI software
import desispec.database.redshift as db
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

#Flask Setup
from app import app
from .utils import filter_query


@app.route('/query/ztile', methods=['POST'])
def getRedshiftsByTileID():
    """ 
    @Params: 
        body (DICT): Contains query parameters.
            MUST CONTAIN: tileID(INT)
            OPTIONAL: (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), subtype(STRING), 
                       z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object (targetID, redshift) containing the targetIDs and associated 
                  redshifts for targets found in provided tileID.     
    """
    body = request.get_json()
    tileID = body['tileID']
    
    if (tileID < 1):
        return jsonify(f'Tile ID {tileID} is invalid')                         
  
    q = db.dbSession.query(db.Ztile.targetid, db.Ztile.z).filter(db.Ztile.tileid == tileID)
    
    if (q.first() is None):
        return jsonify(f'Tile ID {tileID} was not found')
    
    return filter_query(q, db.Ztile, body)


@app.route('/query/zpix', methods=['POST'])
def getRedshiftsByHEALPix():
    """ 
    @Params: 
        body (DICT): Contains query parameters.
            MUST CONTAIN: healpix (INT)
            OPTIONAL: (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), subtype(STRING), 
                       z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object (targetID, redshift) containing the targetIDs and associated 
                  redshifts for targets found in provided HealPIX.   
    """
    body = request.get_json()
    healpix = body['healpix']
    
    if (healpix < 1): # Set healpix bounds
        return jsonify(f'HEALPix {healpix} is invalid')
    
    q = db.dbSession.query(db.Zpix.targetid, db.Zpix.z).filter(db.Zpix.healpix == healpix)
    
    if (q.first() is None):
        return jsonify(f'HEALPix ID {healpix} was not found')
    
    return filter_query(q, db.Zpix, body)


@app.route('/query/radec', methods=['POST'])
def getRedshiftsByRADEC():
    """ 
    @Params: 
        body (DICT): Contains query parameters.
            MUST CONTAIN: ra(DOUBLE), dec(DOUBLE)
            OPTIONAL: radius=0.01(INT), (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), 
                      subtype(STRING), z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object (targetID, ra, dec, redshift) for targets found
                        in cone search of the provided ra, dec, radius
    """
    body = request.get_json()
    ra = body['ra']
    dec = body['dec']
    radius = body.get('radius', 0.01)
    if (ra > 360 or ra < 0):
        return jsonify(f'Invalid Right Ascension {ra}')
    elif (dec > 90 or dec < -90):
        return jsonify(f'Invalid Declination {dec}')
    elif (radius < 0):
        return jsonify(f'Invalid Radius {radius}')
    
    q = db.dbSession.query(db.Photometry.targetid, db.Photometry.ra, db.Photometry.dec, db.Zpix.z)
    q = q.join(db.Zpix).filter(func.q3c_radial_query(db.Photometry.ra, db.Photometry.dec, ra, dec, radius))
    
    if (q.first() is None):
        return jsonify(f'No objects found at RA {ra} and DEC {dec} within radius {radius}')
        
    return filter_query(q, db.Zpix, body)
