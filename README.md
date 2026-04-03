# FITS Image Analyzer

This is a small interactive Python tool to work with astronomical FITS images.
It was mainly developed to quickly inspect stars in an image and extract basic quantities like centroid, FWHM and flux.

---

## What it does

* lets you click on a star in the image
* fits a 2D Gaussian to estimate:

  * centroid
  * FWHM (x, y and average)
* performs simple aperture photometry with sky subtraction
* computes a rough signal-to-noise ratio
* shows a few plots (profiles, fit, photometry region)
* saves results to file

---

## How to run it

Clone the repo and install dependencies:

```bash
git clone https://github.com/matteolezzi/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

Then run:

```bash
python image_analyzer.py path/to/file.fits
```

---

## Controls

* click on a star → select it
* ENTER → run Gaussian fit
* C → show contour levels
* A → run aperture photometry (after fitting)
* I → print image info
* X → exit

---

## Output

The script will:

* print fit parameters in the terminal
* save a log file with:

  * centroid
  * FWHM
  * amplitude and offset
* generate some plots:

  * X/Y profiles with Gaussian fit
  * fitted image
  * photometry apertures

---

## Notes

* The tool assumes stars are reasonably well described by a Gaussian profile
* Photometry is very basic (just circular aperture + sky annulus)
* It’s mainly meant for quick inspection, not for high-precision pipelines

