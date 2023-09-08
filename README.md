# fetch_lc
Your one-stop shop to all catalogue lightcurves! 

Simply supply the Ra and Dec of your favourite object and see the magic happen. So far implemented TESS, PTF, ZTF, WISE, GALEX, SWIFT-UVOT, SWIFT-XRT and FERMI-LAT.

 `python fetch_lc.py --ra "XX.XX" --dec "XX.XX" `
 
(space or ":" separated formats are accepted too) and the code will identify your object and retrieve all available catalog lightcurves. It is also possible to call any of the individual scripts e.g.

`python tess.py --ra "XX.XX" --dec "XX.XX"`
# Requirements
* pyLRC [link](https://pages.github.com/) --> needs to be installed inside the fetch_lc dir
* swifttools 3.0.8
* lightkurve 2.4.0
* ztfquery 1.19.1
* astroquery 0.4.7.dev8076
# Installation
Simply clone the github repository and install the required dependencies

`git clone https://github.com/andresgur/fetch_lc`
