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
from flask import request, send_file, render_template, jsonify
import glob
import os
import tempfile

from api.utils import format_JSON, format_SQL_JSON, default_limit


@app.route('/multispectra', methods=['GET'])
def multispectraPage():
    return render_template('multispectra.html')


def getTargetids(params):
    raw = params['targetIDs'].split(",")
    return [int(targetid) for targetid in raw]


@app.route('/file/multispectra', methods=['GET'])
def plotServeMultispectra():
    params = request.args.to_dict()
    targetids = getTargetids(params)
    q = db.dbSession.query(db.Fiberassign.targetid, db.Fiberassign.tileid, db.Tile.lastnight, db.Fiberassign.petal_loc).join(db.Tile)
    q = q.filter(db.Fiberassign.targetid.in_(targetids) and db.Fiberassign.tileid == db.Tile.tileid)

    if q.count() == 0:
        return jsonify(f'TargetIDs not found!')
    
    tile_rows = q.limit(default_limit)

    results = list()
    for targetid, tileid, lastnight, petal_loc in tile_rows:
        path = os.path.join(os.environ.get('FUJIFILES'), 'tiles', 'cumulative', str(tileid), str(lastnight), f'coadd-{str(petal_loc)}-{str(tileid)}-thru{str(lastnight)}.fits')
        spectrafiles = glob.glob(path)

        coadd = desispec.io.read_spectra(spectrafiles[0], single=True) 
        fib = np.where(coadd.fibermap['TARGETID'] == targetid)
        if np.any(fib):
            results.append(fib)

    results = desispec.spectra.stack(results)
    temp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=True)
    app.logger.info(f'temp.name: {temp.name}')
    desispec.io.write_spectra(temp, results)
    return send_file(path_or_file=temp.name, as_attachment=True)


