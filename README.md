# fetch_lc
Your one-stop shop to all catalogue lightcurves! Simply supply the Ra and Dec of your favourite object and see the magic happen. So far implemented TESS, PTF, ZTF, WISE, GALEX, SWIFT-UVOT, SWIFT-XRT and FERMI-LAT.

To use it simply run
 `python fetch_lc.py --ra "XX.XX" --dec "XX.XX" `
(space or ":" separated formats are accepted too) and the code will identify your object and retrieve all available catalog lightcurves. It is also possible to call any of the individual scripts e.g.
`python tess.py --ra "XX.XX" --dec "XX.XX"`
# Requirements
* pyLRC [pyLRC](https://pages.github.com/) --> needs to be installed inside the fetch_lc dir
* swifttools 
# Installation
Simply clone the github repository and install the required dependencies
`git clone https://github.com/andresgur/fetch_lc`
