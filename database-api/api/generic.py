from flask import request, jsonify
import json

# DESI software
import desispec.database.redshift as db
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

# Flask Setup
from app import app

from api.utils import format_JSON, format_SQL_JSON, default_limit, parseParams


def getTableColumns(params):
    """
    @Params: 
        params (dict):
            table (String): SQL table name
            columns (dict):
                name (STRING): Column names from table
    
    @Returns:
        table (SQLAlchemy DeclarativeMeta): SQL Table object that matched the table string name
        columns (list(SQLAlchemy column)): SQL Column objects that matched string name of columns and were found in table 
    """
    table = getTable(params['table'])
    
    columns = []
    for column in json.loads(params['columns']):
        columns.append(getColumn(table, column['name']))
    return table, columns

def getColumn(table, column):
    """
    @Params: 
        table (SQLAlchemy DeclarativeMeta): SQL Table object 
        column (String): Column name to access
    
    @Returns:
        (SQLAlchemy column): SQL Column objects that matched string name of columns and were found in table 
    """
    try:
        return getattr(table, column.lower())
    except:
        raise ValueError(f'Could not find {column} in table {table.__table__.name}')

def getTable(table):
    """
    @Params: 
        table (String): SQL table name 
    
    @Returns:
        (SQLAlchemy DeclarativeMeta): SQL Table object 
    """
    try:
        return getattr(db, table.lower().capitalize())
    except:
        raise ValueError(f'Could not resolve table {table}')


# Flask API Endpoints
@app.route('/api/table', methods=['GET'])
def queryTable():
    """ 
    @Params: 
        Query parameters:
            MUST CONTAIN: 
                table(STRING): Table in database to query
                columns(STRING): String list of Dictionaries specifying columns of table to return in query
                    Each dictionary 
                    MUST CONTAIN:
                        name(STRING): name of column
                    OPTIONAL: (value type must be comparable to column type)
                        e: equal to filter
                        ne: not equal to filter
                        lte: less than or equal to filter
                        gte: greater than or equal to filter
            OPTIONAL: limit=100(INT)
    
    @Returns:
        (JSON): JSON Object containing the columns requested for the targets that matched the query
    """
    params = request.args.to_dict()
    parseParams(params)
    table, columns = getTableColumns(params)
    q = db.dbSession.query(*columns)
    for column in json.loads(params['columns']):
        if 'e' in column:
            q = q.filter(getColumn(table, column['name']) == column['e'])
        if 'ne' in column:
            q = q.filter(getColumn(table, column['name']) != column['ne'])
        if 'lte' in column:
            q = q.filter(getColumn(table, column['name']) <= column['lte'])
        if 'gte' in column:
            q = q.filter(getColumn(table, column['name']) >= column['gte'])
    if 'limit' in params:
        q = q.limit(params['limit'])
    else:
        q = q.limit(default_limit)
    
    try:
        return format_SQL_JSON(q)
    except ValueError as err:
        return jsonify(str(err))


@app.route('/api/table/columns', methods=['GET'])
def getColumnNamesTypes():
    """
    @Params: 
        Query parameters:
            table(STRING): Table in database to return columns
    
    @Returns:
        (JSON): JSON Object containing the column info (name, type) for each column in requested table
    """
    params = request.args.to_dict()
    parseParams(params)
    table = getTable(params['table'])
    results = [{"name":c.key, "type":c.type.__visit_name__} for c in table.__table__.columns]
    try:
        return format_JSON(results)
    except ValueError as err:
        return jsonify(str(err))
