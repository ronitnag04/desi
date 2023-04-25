from flask import jsonify

# Global Variables
valid_spectypes = {'GALAXY', 'STAR', 'QSO'}
valid_subtypes = {'CV', 'M', 'G', 'K'}
default_limit = 100

from app import app


def parseParams(params):
    invalid_characters = [';', '-', '/', '\\', '=']
    if type(params) == str:
        if any(invalid_character in params for invalid_character in invalid_characters):
            raise ValueError(f'Illegal query parameter {params}')
    else:
        for param in params:
            parseParams(param)


def format_JSON(results):
    """
    Uses flask's jsonify with app context to format results into JSON.
    @Params:
        results : Must be jsonifiable type
    @Returns:
        (JSON): JSON convertion of results
    """
    with app.app_context():
        return jsonify(results)

def format_SQL_JSON(q):
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
    

def filter_index(q, options):
    """
    Filters query based on indexing options
    @Params:
        q (SQLAlchemy Query): Query object to apply filters
        options (dict): Contains filtering options (limit=100, start, end)
    
    @Returns:
        q (SQLAlchemy Query): Query object after filters have been applied
    """
    limit = options.get('limit', None)
    if limit: 
        limit = int(limit)
    start = options.get('start', None)
    if start: 
        start = int(start)
    end = options.get('end', None)
    if end: 
        end = int(end)

    if limit is not None:
        if start is not None and end is not None:
            raise ValueError('Cannot handle both limit and start/end arguments to filter query')
        elif (start is not None and end is None):
            q = q.offset(start).limit(limit)
        elif (end is not None and start is None):
            if end-limit < 0:
                raise ValueError(f'Invalid end argument {end} for provided limit {limit}')
            else:
                q = q.offset(end-limit).limit(limit)
        else:
            q = q.limit(limit)
    else:
        if start is None and end is None:
            q = q.limit(default_limit)
        elif start is None or end is None:
            raise ValueError(f'Must provide both start and end parameters if limit is not provided')
        elif end <= start:
            raise ValueError(f'Start parameter {start} must be less than end parameter {end}')
        else:
            q = q.offset(start).limit(end-start)
    
    return q



def filter_ztable(q, db_ref, options):
    """
    Filters query based on options and provided reference table. Returns JSON object of query.
    @Params:
        q (SQLAlchemy Query): Query object to apply filters
        db_ref (SQLAlchemy DeclarativeMeta): Table to use to apply filters (either Zpix or Ztile)
        options (dict): Contains filtering options (z_min, z_max, spectype, subtype, limit, start, end)
    
    @Returns:
        q (SQLAlchemy Query): Query object after filters have been applied
    """
    if not (db_ref.__name__ == 'Zpix' or db_ref.__name__ == 'Ztile'):
        raise ValueError(f'Cannot filter table {db_ref.__name__}')

    z_min = options.get('z_min', None)
    if z_min:
        z_min = float(z_min)
    z_max = options.get('z_max', None)
    if z_max:
        z_max = float(z_max)

    spectype = options.get('spectype', None)
    if spectype:
        spectype = str(spectype)
    subtype = options.get('subtype', None)
    if subtype:
        subtype = str(subtype)

    if (z_min and z_max and z_min > z_max):
        raise ValueError(f'z_min({z_min}) must be less than z_max({z_max})')
    
    if (spectype and spectype not in valid_spectypes):
        raise ValueError(f'Spectype {spectype} is not valid. Choose from available spectypes: {valid_spectypes}')
    if (subtype and subtype not in valid_subtypes):
        raise ValueError(f'Subtype {subtype} is not valid. Choose from available subtypes: {valid_subtypes}')
    if (spectype and subtype and spectype != 'STAR'):
        raise ValueError('Only STAR spectype currently has subtypes')
    
    if z_min:
        q = q.filter(db_ref.z >= z_min)
    if z_max:
        q= q.filter(db_ref.z <= z_max)
    if spectype:
        q = q.filter(db_ref.spectype == spectype)
    if subtype:
        q = q.filter(db_ref.subtype == subtype)
    
    q = filter_index(q, options)
    
    return q
