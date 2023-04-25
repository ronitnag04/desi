import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import jsonify, send_file, request

# DESI software
import desispec.database.redshift as db
import desispec.io
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

# Flask Setup
from app import app

from api.utils import default_limit, parseParams
from api.multispectra import getTargetids, queryTargetIDs, getSpectra
from gui.utils import figToPNG, plotSpectra

spectra_plot_cmap = {'b':'C0', 'r':'C1', 'z':'C2'}


@app.route('/gui/display/tile-qa', methods=['GET'])
def displayTileQA():
    """ 
    Serves image file for specified tile, which is exists on the NERSC global filesystem
    Query parameters:
        MUST CONTAIN: 
            tileID (STRING): Integer string of tileid requested
    @Returns:
        image (PNG): PNG image of tile-qa
    """
    params = request.args.to_dict()
    parseParams(params)
    tileid = int(params.get("tileID"))

    q = db.dbSession.query(db.Tile.lastnight).filter(db.Tile.tileid == tileid)

    assert q.count() == 1
    lastnight = q[0][0]

    folder = os.path.join(os.environ.get('FUJIFILES'), 'tiles', 'cumulative', str(tileid), str(lastnight))
    filename = f'tile-qa-{tileid}-thru{lastnight}.png'
    tilepath = os.path.join(folder, filename)
    tileQA = glob.glob(tilepath)

    assert len(tileQA) == 1
    image_path = tileQA[0]
    return send_file(image_path)

@app.route('/gui/display/target', methods=['GET'])  
def displayTargetSpectra():
    """ 
    Displays cumulative coadd spectra of the target for each tile it was observed on.
    Query parameters:
        MUST CONTAIN: 
            targetID (String): Numeric string of targetID to plot
    @Returns:
        image (PNG): Plot contains spectra (wavelength vs. flux) for each tile where targetid is found.
                     Spectra plots are stacked vertically, with each tile plot measuring 1600px by 300px.
    """
    params = request.args.to_dict()
    parseParams(params)
    targetid = int(params.get("targetID"))

    q = db.dbSession.query(db.Fiberassign.tileid, db.Tile.lastnight, db.Fiberassign.petal_loc).join(db.Tile)
    q = q.filter(db.Fiberassign.targetid == targetid and db.Fiberassign.tileid == db.Tile.tileid)
    if q.count() == 0:
        return jsonify(f'Target {targetid} not found!')
    
    tile_rows = q.all()
    tile_rows.sort(key=lambda r:r[0])
    
    fig, axs = plt.subplots(len(tile_rows), 1, figsize=(16,len(tile_rows)*3))
    if len(tile_rows) == 1:
        axs = np.array([axs])
    
    for i, (tileid, lastnight, petal_loc) in enumerate(tile_rows):
        axs[i].set_title(f'Tile {tileid}')
        dir = os.path.join(os.environ.get('FUJIFILES'), 'tiles', 'cumulative', str(tileid), str(lastnight))
        filename = f'coadd-{str(petal_loc)}-{str(tileid)}-thru{str(lastnight)}.fits'
        path = os.path.join(dir, filename)
        spectrafiles = glob.glob(path)
        
        if len(spectrafiles) == 0:
            axs[i].text(x=0.5, y=0.5, s= f'Could not find spectra for Tile {tileid}', va='center', ha='center', transform=axs[i].transAxes)
        elif len(spectrafiles) > 1:
            axs[i].text(x=0.5, y=0.5, s= f'Too many spectra for Tile {tileid}', va='center', ha='center', transform=axs[i].transAxes)
        else:
            spectra = desispec.io.read_spectra(spectrafiles[0], single=True) 
            fib = np.where(spectra.fibermap['TARGETID'] == targetid)
            assert len(fib) == 1
            ispec = fib[0][0]
            plotSpectra(spectra, ispec, axs, i)
    
    fig.tight_layout()
    return figToPNG(fig)

@app.route('/gui/display/multispectra', methods=['GET'])  
def displayMultispectra():
    """
    @Params: 
        Query parameters:
            MUST CONTAIN: 
                targetIDs (String): Comma-seperated numeric strings of targetIDs
    
    @Returns:
        image (PNG): Plot contains spectra (wavelength vs. flux) for each targetID provided.
                     Spectra plots are stacked vertically, with each tile plot measuring 1600px by 300px.
    """
    params = request.args.to_dict()
    parseParams(params)
    targetids = getTargetids(params)
    q = queryTargetIDs(targetids)
    if q.count() == 0:
        return jsonify('TargetIDs not found!')
    
    tile_rows = q.limit(default_limit)
    try:
        spectra = getSpectra(tile_rows)
    except ValueError as err:
        return jsonify(str(err))
    
    num = len(spectra.fibermap)
    fig, axs = plt.subplots(num, 1, figsize=(16,num*3))
    if num == 1:
        axs = np.array([axs])
    for i in range(num):
        axs[i].set_title(f'Target {spectra.fibermap["TARGETID"][i]} on Tile {spectra.fibermap["TILEID"][i]}')
        plotSpectra(spectra, i, axs, i)
    
    fig.tight_layout()
    return figToPNG(fig)
    
