from sqlalchemy.sql import func
from flask import Flask, request, jsonify

# DESI software
import desispec.database.redshift as db
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

#Flask Setup
app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=False)


# Helper Methods
valid_spectypes = {'GALAXY', 'STAR', 'QSO'}
valid_subtypes = {'CV', 'M', 'G', 'K'}
default_limit = 100

def filter_query(q, db_ref, body):
    """
    Filters query based on options and provided reference table
    @Params:
        q (SQLAlchemy Query): Query object to apply filters
        db_ref (SQLAlchemy DeclarativeMeta): Table to use to apply filters (either Zpix or Ztile)
    
    @Returns:
        q (SQLAlchemy Query): Query object after filters have been applied
    """
    z_min = body.get('z_min', -1.0)
    z_max = body.get('z_max', 6.0)
    spectype = body.get('spectype', None)
    subtype = body.get('subtype', None)
    limit = body.get('limit', None)
    start = body.get('start', None)
    end = body.get('end', None)
    if (z_min > z_max):
        return jsonify(f'z_min({z_min}) must be less than z_max({z_max})')
    if (spectype and spectype not in valid_spectypes):
        return jsonify(f'Spectype {spectype} is not valid. Choose from available spectypes: {valid_spectypes}')
    
    if (subtype and subtype not in valid_subtypes):
        return jsonify(f'Subtype {subtype} is not valid. Choose from available subtypes: {valid_subtypes}')
        
    if (spectype and subtype and spectype != 'STAR'):
        return jsonify('Only STAR spectype currently has subtypes')
    
    q = q.filter(db_ref.z >= z_min).filter(db_ref.z <= z_max)
    if spectype:
        q = q.filter(db_ref.spectype == spectype)
    if subtype:
        q = q.filter(db_ref.subtype == subtype)
    
    if limit is not None:
        if start is not None and end is not None:
            return jsonify('Cannot handle both limit and start/end arguments to filter query')
        elif (start is not None and end is None):
            q = q.offset(start).limit(limit)
        elif (end is not None and start is None):
            if end-limit < 0:
                raise IndexError(f'Invalid end argument {end} for provided limit {limit}')
            else:
                q = q.offset(end-limit).limit(limit)
        else:
            q = q.limit(limit)
    else:
        if start is None and end is None:
            q.limit(default_limit)
        elif start is None or end is None:
            return jsonify(f'Must provide both start and end parameters if limit is not provided')
        elif end <= start:
            return jsonify(f'Start parameter {start} must be less than end parameter {end}')
        else:
            q = q.offset(start).limit(end-start)
    
    return formatJSON(q)


def formatJSON(q):
    results = []
    for target in q.all():
        results.append(dict(target._mapping))
    with app.app_context():
        return jsonify(results)


# Flask API Endpoints

@app.route('/query/target/<targetID>', methods=['GET'])
def getRedshiftByTargetID(targetID):
    """ 
    @Params: 
        targetID (BIGINT): Big Integer representing which object to query for redshift
    
    @Returns:
        z (DOUBLE): Redshift of the first object 
    """
    targetID = int(targetID)
    if (targetID < 0):
        return jsonify(f'Target ID {targetID} is invalid')
    
    q = db.dbSession.query(db.Zpix.z).filter(db.Zpix.targetid == targetID)
    
    if (q.first() is None):
        return jsonify(f'Target ID {targetID} was not found')
    if (q.count() > 1):
        print(f'More than one redshift value found for target: {targetID}. Returning first found')
        
    z = q[0][0]
    return jsonify(z)


@app.route('/query/ztile', methods=['POST'])
def getRedshiftsByTileID():
    """ 
    @Params: 
        body (DICT): Contains query parameters.
            MUST CONTAIN: tileID, (limit/start/end)
            OPTIONAL: spectype, subtype, z_min, z_max
    
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
            MUST CONTAIN: healpix, (limit/start/end)
            OPTIONAL: spectype, subtype, z_min, z_max
    
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
            MUST CONTAIN: ra, dec, (limit/start/end)
            OPTIONAL: radius(default=0.01), spectype, subtype, z_min, z_max
    
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
