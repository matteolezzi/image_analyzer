# Astronomical FITS Image Analyzer

Interactive Python tool for the analysis of astronomical images in FITS format.

The software was developed as part of the Astrophysics Laboratory at the **Università del Salento**, with the aim of providing a practical tool for the analysis of stellar sources in astronomical images.

## Features

The analyzer provides the following functionalities:

* FITS image visualization
* Interactive selection of stellar sources
* Interactive image contrast adjustment
* Two-dimensional Gaussian fitting
* Stellar centroid determination
* FWHM measurement along the X and Y axes
* Mean FWHM calculation
* Estimation of uncertainties from the Gaussian fit covariance matrix
* Visualization of stellar profiles along the X and Y axes
* Visualization of the fitted stellar image
* Interactive contour plots
* FITS header information display
* Aperture photometry
* Background estimation using a sky annulus
* Background-subtracted flux calculation
* Signal-to-noise ratio estimation
* Automatic logging of Gaussian fit parameters

## Analysis Workflow

The program provides an interactive workflow for analyzing individual stellar sources.

### 1. FITS Image

The FITS image is loaded using `astropy.io.fits` and displayed using Matplotlib.

The initial contrast is automatically determined from the 5th and 99th percentiles of the image data. Two sliders can then be used to adjust the minimum and maximum intensity displayed.

### 2. Source Selection

A stellar source can be selected directly by clicking on the image.

The selected pixel coordinates are recorded and used as the initial position for the subsequent analysis.

### 3. Two-Dimensional Gaussian Fit

Pressing `ENTER` performs a two-dimensional Gaussian fit on the selected source.

A preliminary fit is first used to estimate the position of the source. The image is then recentered on the estimated centroid and a second, more precise fit is performed.

The Gaussian model is defined as:

```text
f(x,y) = offset + amplitude *
         exp[-((x-x0)^2/(2*sigma_x^2)
             +(y-y0)^2/(2*sigma_y^2))]
```

The fit provides:

* Amplitude
* X centroid
* Y centroid
* Sigma X
* Sigma Y
* Background offset

The full width at half maximum is calculated from:

```text
FWHM = 2.3548 * sigma
```

separately for the X and Y directions.

The mean FWHM is then calculated as the average of the two values.

Uncertainties on the fitted parameters are obtained from the covariance matrix returned by `scipy.optimize.curve_fit`.

### 4. Stellar Profiles

After a successful fit, the program generates profiles through the center of the source along the X and Y directions.

The measured data are plotted together with the corresponding Gaussian model.

The generated files are named:

```text
profile_x_<x>_<y>_<n>.png
profile_y_<x>_<y>_<n>.png
```

A separate image showing the fitted source and its estimated centroid is also generated:

```text
fit_image_<x>_<y>_<n>.png
```

### 5. Contour Visualization

Pressing `C` opens a dedicated view of the selected source with interactive contour levels.

The user can adjust:

* Number of contour levels
* Minimum intensity
* Maximum intensity

This provides a visual representation of the spatial distribution of the source.

### 6. Aperture Photometry

After performing a Gaussian fit, pressing `A` performs aperture photometry.

The aperture radius is defined using the measured mean FWHM:

```text
aperture radius = mean FWHM
```

The background is estimated from a surrounding annulus:

```text
inner radius = 1.5 * aperture radius
outer radius = 2.5 * aperture radius
```

The program calculates:

* Raw stellar flux
* Median sky background
* Estimated sky contribution
* Background-subtracted flux
* Estimated noise
* Signal-to-noise ratio

The sky contribution is estimated from the median background value multiplied by the area of the aperture.

The noise is estimated as:

```text
noise = sqrt(area) * sky_std
```

and the signal-to-noise ratio is calculated as:

```text
S/N = net_flux / noise
```

### 7. FITS Header Information

Pressing `I` displays information extracted from the FITS header, including, when available:

* Image dimensions
* Telescope
* Instrument
* Object
* Exposure time
* Right ascension
* Declination
* Observation date

## Keyboard Controls

| Key     | Function                                         |
| ------- | ------------------------------------------------ |
| `ENTER` | Perform a 2D Gaussian fit on the selected source |
| `C`     | Display interactive contours                     |
| `A`     | Perform aperture photometry                      |
| `I`     | Display FITS image information                   |
| `X`     | Exit the program                                 |


## Output

The Gaussian fit results are stored in a tab-separated log file.

The output contains:

```text
x_center
y_center
fwhm_x
fwhm_y
fwhm_ave
amplitude
offset
```

The program also generates PNG files containing the X and Y profiles and the fitted image.

## Dependencies

The program uses the following Python libraries:

* NumPy
* Matplotlib
* Astropy
* SciPy

The corresponding imports are shown in the original implementation.

Install the required packages with:

```bash
pip install numpy matplotlib astropy scipy
```

## Source Code Availability

The source code is **not publicly available in this repository**.

The software was developed specifically as part of the **Astrophysics Laboratory at the Università del Salento** and is therefore not distributed as an independent open-source project.

This repository serves as a documentation and project reference for the work carried out during the laboratory.

## Scientific Applications

The analyzer was developed for practical astronomical image analysis and can be used to investigate:

* Stellar image profiles
* Point-spread functions
* Stellar centroids
* FWHM measurements
* Aperture photometry
* Background estimation
* Signal-to-noise ratios
* FITS image metadata

The Gaussian fitting procedure is particularly useful for characterizing the spatial profile of stellar sources.

## Limitations

The current implementation is designed primarily for interactive analysis of individual sources.

Some aspects of the implementation are specific to the laboratory environment, including the configuration and location of the input FITS data.

The aperture photometry procedure also relies on assumptions concerning the aperture size, background annulus, and dominant noise contribution.

## Project Context

This project was developed during the **Astrophysics Laboratory** at:

**Università del Salento**
**LABASTRO – Astrophysics Laboratory**
Lecce, Italy

## Author

**Matteo Lezzi**

MSc in Physics — Astrophysics
Università del Salento


* The tool assumes stars are reasonably well described by a Gaussian profile
* Photometry is very basic (just circular aperture + sky annulus)
* It’s mainly meant for quick inspection, not for high-precision pipelines

