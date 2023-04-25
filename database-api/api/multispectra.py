# DESI software
import desispec.database.redshift as db
import desispec.io 
import desispec.spectra
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

# Flask Setup
from app import app

import numpy as np
from flask import request, send_file, jsonify
import glob
import os
import tempfile

from api.utils import default_limit

def getTargetids(params):
    """
    @Params:
        params (DICT): Contains query parameters
            MUST CONTAIN: 
                targetIDs (str): Comma seperated string of numeric targetIds
    
    @Returns:
        targetIds (List(INT)): List of integers representing the targetIds provided
    """
    raw = params['targetIDs'].split(",")
    return [int(targetid) for targetid in raw]

def queryTargetIDs(targetids):
    """
    @Params:
        targetids (List(integer*)): List of integers for each target's targetID

    @Returns:
        q (SQLAlchemy Query): Query object containing (targetid, tileid, lastnight, petal_loc) columns for each targetID found
    """
    q = db.dbSession.query(db.Fiberassign.targetid, db.Fiberassign.tileid, db.Tile.lastnight, db.Fiberassign.petal_loc).join(db.Tile)
    q = q.filter(db.Fiberassign.tileid == db.Tile.tileid)
    q = q.filter(db.Fiberassign.targetid.in_(targetids))
    q = q.order_by(db.Fiberassign.targetid)

    return q

def getSpectra(tile_rows):
    """
    @Params:
        tile_rows (List(str, str, str, str)): 
            Output from SQLAlchemy query, containing targetid, tileid, lastnight, and petal_loc values for each target
    
    @Returns:
        results (desispec.spectra.Spectra):
            Stacked spectra object from the cumulative coadd spectra files for each target provided.
    """
    results = list()
    for targetid, tileid, lastnight, petal_loc in tile_rows:
        folder = os.path.join(os.environ.get('FUJIFILES'), 'tiles', 'cumulative', str(tileid), str(lastnight))
        filename = f'coadd-{str(petal_loc)}-{str(tileid)}-thru{str(lastnight)}.fits'
        path = os.path.join(folder, filename)
        spectrafiles = glob.glob(path)
        if len(spectrafiles) != 1:
            raise ValueError(f'Unable to resolve file match to {filename}')

        coadd = desispec.io.read_spectra(spectrafiles[0], single=True)
        keep = (coadd.fibermap['TARGETID'] == targetid)
        if np.any(keep):
            results.append(coadd[keep])
    return desispec.spectra.stack(results)

@app.route('/api/file/multispectra', methods=['GET'])
def serveMultispectra():
    """
    @Params: 
        Query parameters:
            MUST CONTAIN: 
                targetIDs (String): Comma-seperated numeric strings of targetIDs
    
    @Returns:
        temp (.fits): .fits file containing the Spectra objects for each target found matching the provided targetIds.
            Spectra objects come from the coadd .fits files from cumulative spectra data. File is immediately removed
            from storage once delivered to user  
    """
    params = request.args.to_dict()
    targetids = getTargetids(params)
    q = queryTargetIDs(targetids)
    if q.count() == 0:
        return jsonify('TargetIDs not found!')
    
    tile_rows = q.limit(default_limit)
    try:
        results = getSpectra(tile_rows)
    except ValueError as err:
        return jsonify(str(err))
    
    temp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=True, suffix='.fits')
    desispec.io.write_spectra(temp.name, results)
    return send_file(path_or_file=temp.name, as_attachment=True)

