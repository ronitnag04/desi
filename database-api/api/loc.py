from sqlalchemy.sql import func
from flask import request, jsonify

# DESI software
from app import db

#Flask Setup
from app import app

from api.utils import filter_ztable, format_SQL_JSON, parseParams


@app.route('/api/loc/ztile', methods=['GET'])
def getRedshiftsByTileID():
    """ 
    @Params: 
        Query parameters:
            MUST CONTAIN: tileID(INT)
            OPTIONAL: (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), subtype(STRING), 
                       z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        (JSON): JSON Object (targetID, redshift) containing the targetIDs and associated 
                  redshifts for targets found in provided tileID.   
    """
    params = request.args.to_dict()
    parseParams(params)
    tileID = int(params['tileID'])
    
    if (tileID < 1):
        return jsonify(f'Tile ID {tileID} is invalid')                         
  
    q = db.dbSession.query(db.Ztile.targetid, db.Ztile.z).filter(db.Ztile.tileid == tileID)
    
    if (q.first() is None):
        return jsonify(f'Tile ID {tileID} was not found')
    
    try:
        q = filter_ztable(q, db.Ztile, params)
        return format_SQL_JSON(q)
    except ValueError as err:
        return jsonify(str(err))


@app.route('/api/loc/zpix', methods=['GET'])
def getRedshiftsByHEALPix():
    """ 
    @Params: 
        Query parameters:
            MUST CONTAIN: healpix (INT)
            OPTIONAL: (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), subtype(STRING), 
                       z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object (targetID, redshift) containing the targetIDs and associated 
                  redshifts for targets found in provided HealPIX.   
    """
    params = request.args.to_dict()
    parseParams(params)
    healpix = int(params['healpix'])
    
    if (healpix < 1): # Set healpix bounds
        return jsonify(f'HEALPix {healpix} is invalid')
    
    q = db.dbSession.query(db.Zpix.targetid, db.Zpix.z).filter(db.Zpix.healpix == healpix)
    
    if (q.first() is None):
        return jsonify(f'HEALPix ID {healpix} was not found')
    
    try:
        q = filter_ztable(q, db.Zpix, params)
        return format_SQL_JSON(q)
    except ValueError as err:
        return jsonify(str(err))


@app.route('/api/loc/radec', methods=['GET'])
def getRedshiftsByRADEC():
    """ 
    @Params: 
        Query parameters:
            MUST CONTAIN: ra(DOUBLE), dec(DOUBLE)
            OPTIONAL: radius=0.01(INT), (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), 
                      subtype(STRING), z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object (targetID, ra, dec, redshift) for targets found
                        in cone search of the provided ra, dec, radius
    """
    params = request.args.to_dict()
    parseParams(params)
    ra = float(params['ra'])
    dec = float(params['dec'])
    radius = float(params.get('radius', 0.01))

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
        
    try:
        q = filter_ztable(q, db.Zpix, params)
        return format_SQL_JSON(q)
    except ValueError as err:
        return jsonify(str(err))
