import os
import glob
import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import jsonify, send_file, Response

# DESI software
import desispec.database.redshift as db
import desispec.io
specprod = 'fuji'

# Database Setup
postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')

# Flask Setup
from app import app

spectra_plot_cmap = {'b':'C0', 'r':'C1', 'z':'C2'}


@app.route('/gui/display/tile-qa/<tileid>', methods=['GET'])
def displayTileQA(tileid):
    """ 
    Serves image file for specified tile, which is exists on the NERSC global filesystem
    @Params: 
        tileid (STRING): Integer string of tileid requested
    @Returns:
        image (PNG): PNG image of tile-qa
    """
    q = db.dbSession.query(db.Tile.lastnight).filter(db.Tile.tileid == int(tileid))

    assert q.count() == 1
    lastnight = q[0][0]
    tilepath = os.path.join(os.environ.get('FUJIFILES'), 'tiles', 'cumulative', tileid, str(lastnight), f'tile-qa-{tileid}-thru{lastnight}.png')
    tileQA = glob.glob(tilepath)
    assert len(tileQA) == 1
    image_path = tileQA[0]
    return send_file(image_path)

@app.route('/gui/display/target/<targetid>', methods=['GET'])  
def displayTargetSpectra(targetid):
    """ 
    Displays cumulative coadd spectra of the target for each tile it was observed on.
    @Params: 
        targetid (STRING): Integer string of targetid to plot spectra 
    @Returns:
        image (PNG): PNG image of matplotlib plot. 
                     Plot contains spectra (wavelength vs. flux) for each tile where targetid is found.
                     Spectra plots are stacked vertically, with each tile plot measuring 1600px by 300px.
    """
    q = db.dbSession.query(db.Fiberassign.tileid, db.Tile.lastnight, db.Fiberassign.petal_loc).join(db.Tile).filter(db.Fiberassign.targetid == int(targetid) and db.Fiberassign.tileid == db.Tile.tileid)
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
            fib = np.where(spectra.fibermap['TARGETID'] == int(targetid))
            assert len(fib) == 1
            ispec = fib[0][0]
            for band in spectra.bands:
                axs[i].plot(spectra.wave[band], spectra.flux[band][ispec], f'{spectra_plot_cmap[band]}-', alpha=0.5, label=f'band {band}')
            axs[i].set_xlabel(r'Wavelength $Å$')
            axs[i].set_ylabel(r'Flux $10^{-17} \cdot \frac{ergs}{s \cdot cm^2 \cdot Å}$')
            axs[i].legend(loc="upper right")
    
    fig.tight_layout()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
        
        