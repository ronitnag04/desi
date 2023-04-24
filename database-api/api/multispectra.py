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
    raw = params['targetIDs'].split(",")
    return [int(targetid) for targetid in raw]

def getSpectra(tile_rows, targetids):
    results = list()
    for tileid, lastnight, petal_loc in tile_rows:
        dir = os.path.join(os.environ.get('FUJIFILES'), 'tiles', 'cumulative', str(tileid), str(lastnight))
        filename = f'coadd-{str(petal_loc)}-{str(tileid)}-thru{str(lastnight)}.fits'
        path = os.path.join(dir, filename)
        spectrafiles = glob.glob(path)
        if len(spectrafiles) != 1:
            raise ValueError(f'Abmigious file match to {filename}')

        coadd = desispec.io.read_spectra(spectrafiles[0], single=True) 
        keep = np.isin(coadd.fibermap['TARGETID'], targetids)
        if np.any(keep):
            results.append(coadd[keep])
    return results


@app.route('/api/file/multispectra', methods=['GET'])
def plotServeMultispectra():
    params = request.args.to_dict()
    targetids = getTargetids(params)

    q = db.dbSession.query(db.Fiberassign.tileid, db.Tile.lastnight, db.Fiberassign.petal_loc).join(db.Tile)
    q = q.filter(db.Fiberassign.tileid == db.Tile.tileid)
    q = q.filter(db.Fiberassign.targetid.in_(targetids))
    q = q.order_by(db.Fiberassign.targetid)

    if q.count() == 0:
        return jsonify('TargetIDs not found!')
    
    tile_rows = q.limit(default_limit)
    try:
        results = desispec.spectra.stack(getSpectra(tile_rows, targetids))
    except ValueError as err:
        return jsonify(str(err))
    
    temp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=True, suffix='.fits')
    desispec.io.write_spectra(temp.name, results)
    return send_file(path_or_file=temp.name, as_attachment=True)

