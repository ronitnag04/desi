from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Response

spectra_plot_cmap = {'b':'C0', 'r':'C1', 'z':'C2'}

def figToPNG(fig):
    """
    Converts Matplotlib figure into image bytes and packages into flask Response to be serve at api endpoint.
    @Params:
        fig(matplotlib Figure)
    
    @Returns: 
        image(flask Response): PNG image of fig wrapped into flask response object
    """
    output = BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def plotSpectra(spectra, ispec, axs, i):
    """
    Plots the bands of spectra object onto axs subplot, with appropriate axis labels
    @Params:
        spectra (desispec.spectra.Spectra): Spectra object
        ispec (integer): Index of spectra to plot bands
        axs (Matplotlib.pyplot subplots): Matplotlib subplots object
        i (integer): Index of subplot of axs to plot spectra bands  
    """
    for band in spectra.bands:
        axs[i].plot(spectra.wave[band], spectra.flux[band][ispec], f'{spectra_plot_cmap[band]}-', alpha=0.5, label=f'band {band}')
    axs[i].set_xlabel(r'Wavelength $Å$')
    axs[i].set_ylabel(r'Flux $10^{-17} \cdot \frac{ergs}{s \cdot cm^2 \cdot Å}$')
    axs[i].legend(loc="upper right")