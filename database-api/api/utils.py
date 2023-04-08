from flask import jsonify

# Global Variables
valid_spectypes = {'GALAXY', 'STAR', 'QSO'}
valid_subtypes = {'CV', 'M', 'G', 'K'}
default_limit = 100

from app import app

def formatJSON(q):
    """
    Formats row objects of query q by extracting the row's dictionary mappings.
    @Params:
        q (SQLAlchemy Query): Query object to format into JSON object
    @Returns:
         (JSON): JSON dictionary mapping of each object in q
    """
    results = []
    for target in q.all():
        results.append(dict(target._mapping))
    with app.app_context():
        return jsonify(results)
    
def filter_query(q, db_ref, body):
    """
    Filters query based on options and provided reference table. Returns JSON object of query.
    @Params:
        q (SQLAlchemy Query): Query object to apply filters
        db_ref (SQLAlchemy DeclarativeMeta): Table to use to apply filters (either Zpix or Ztile)
    
    @Returns:
         (JSON): JSON dictionary mapping of each object in q after filters have been applied, 
                 or JSON error string message.
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
