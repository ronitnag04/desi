from flask import request, jsonify

# DESI software
import desispec.database.redshift as db
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

#Flask Setup
from app import app
from .utils import filter_query


def getTableColumns(body):
    try:
        table = getattr(db, body['table'].lower().capitalize())
    except:
        return f'Could not resolve table {body["table"]}'
    
    columns = []
    for column in body['columns']:
        columns.append(getColumn(table, column['name']))
    return table, columns

def getColumn(table, column):
    try:
        return getattr(table, column.lower())
    except:
        return f'Could not find {column} in table {table.__table__.name}'


# Flask API Endpoints
@app.route('/api/table', methods=['POST'])
def queryTable():
    """ 
    @Params: 
        body (DICT): Contains query parameters.
            MUST CONTAIN: 
                table(STRING): Table in database to query
                columns(LIST(DICT)): List of Dictionaries specifying columns of table to return in query
                    Each dictionary 
                    MUST CONTAIN:
                        name(STRING): name of column
                    OPTIONAL:
                        e(INT or STRING): equal to filter
                        ne(INT or STRING): not equal to filter
                        lte(INT or STRING): less than or equal to filter
                        gte(INT or STRING): greater than or equal to filter
            OPTIONAL: (limit=100(INT) / start(INT) / end(INT)), spectype(STRING), subtype(STRING), 
                       z_min(DOUBLE), z_max(DOUBLE)
    
    @Returns:
        results (JSON): JSON Object containing the columns requested for the targets that matched the query
    """
    body = request.get_json()
    table, columns = getTableColumns(body)
    q = db.dbSession.query(*columns)
    for column in body['columns']:
        if 'e' in column:
            q = q.filter(getColumn(table, column['name']) == column['e'])
        if 'ne' in column:
            q = q.filter(getColumn(table, column['name']) != column['ne'])
        if 'lte' in column:
            q = q.filter(getColumn(table, column['name']) <= column['lte'])
        if 'gte' in column:
            q = q.filter(getColumn(table, column['name']) >= column['gte'])
    return filter_query(q, table, body)


@app.route('/api/table/columns', methods=['GET'])
def getColumnNamesTypes():
    args = request.args.to_dict()
    table = args['table']
    try:
        SQLtable = getattr(db, table.lower().capitalize())
    except:
        return f'Could not resolve table {table}'
    return jsonify([(c.key, c.type) for c in SQLtable.__table__.columns])
