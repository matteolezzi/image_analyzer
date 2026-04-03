
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor, Slider
from astropy.io import fits
from scipy.optimize import curve_fit

# SPLASH SCREEN

print("           _____ _____          ")
print("     /\   |  __ \_   _|   /\    ")
print("    /  \  | |__) || |    /  \   ")
print("   / /\ \ |  ___/ | |   / /\ \  ")
print("  / ____ \| |    _| |_ / ____ \ ")
print(" /_/    \_\_|   |_____/_/    \_|")
print(" ")
print(" Another Python Image Analyzer ")
print(" ")
print("      LABASTRO UNISALENTO      ")
print(" ")


# FUNZIONI LOCALI

def twoD_Gaussian(coord, amplitude, xo, yo, sigma_x, sigma_y, offset):
    x, y = coord
    xo = float(xo)
    yo = float(yo)
    g = offset + amplitude * np.exp(
        -(((x - xo) ** 2) / (2 * sigma_x ** 2) + ((y - yo) ** 2) / (2 * sigma_y ** 2))
    )
    return g.ravel()


def sigma_to_fwhm(sigma):
    return 2.3548 * sigma
cd 

# Controlla che il file FITS esista
fits_file ="/home/labastro/WORK/GRUPPO-1/OUTPUT/science/B/astrometry/Stack_B.fits"  # "/home/labastro/WORK/GRUPPO-1/OUTPUT/V/WFI.2002-06-21T00_48_13.036_CHIP_7.fits"  # Cambia con il tuo file
if not os.path.exists(fits_file):
    raise FileNotFoundError(f"Il file FITS '{fits_file}' non è stato trovato.")

log_filename = "stackB_log.txt" #"./WFI.2002-06-21T00_48_13.036_CHIP_7.fits.txt"
fit_n = 0

# Apro il file di log in modalità scrittura (sovrascrive il file esistente)
log_file = open(log_filename, "w")
log_file.write("x_center\ty_center\tfwhm_x\tfwhm_y\tfwhm_ave\tamplitude\toffset\n")

hdul = fits.open(fits_file)
hdr_primary = hdul[0].header
hdr_extension = hdul[0].header
data = hdul[0].data
hdul.close()

if data.ndim == 3 and data.shape[0] == 1:
    data = data[0]
elif data.ndim > 2:
    raise ValueError("Il file FITS ha più di 2 dimensioni. Gestiscilo manualmente.")

data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)

# Trova informazioni dell'immagine
#INFO_LIST = [hdr_extension['NAXIS1'], hdr_extension['NAXIS2'],, hdr_primary['TELESCOP'],
#             hdr_primary['OBJECT'], hdr_extension['EXPTIME'], hdr_extension['DATE-OBS'], #hdr_primary['RA'],
#             hdr_primary['DEC']]
# Queste variabili sono NONE se il fit non è fatto
fwhm_ave=None
x_center_abs=None
y_center_abs=None


# Contrasto
vmin_init = np.percentile(data, 5)
vmax_init = np.percentile(data, 99)

fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.25)

cax = ax.imshow(data, origin='lower', cmap='gray', vmin=vmin_init, vmax=vmax_init)
fig.colorbar(cax, ax=ax)
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

ax.set_title("Clicca su una stella → Premi ENTER per fit → Premi X per uscire")

print("🔍 Zooma sull'immagine, clicca su una stella. Dopo aver cliccato su una stella, puoi...")
print("⏎ Premi ENTER per eseguire il fit (immagine centrata sul centroide e quadrata).")
print(
    "📸 Premi C per costruire le curve di livello della stella selezionata (immagine centrata sul centroide e quadrata).")
print("📸 Premi A per la fotometria di apertura. Richiede di conoscere FWHM (ricavata tramite l'opzione ENTER).")
print("📸 Premi I per avere informazioni sulla'immagine.")
print("❌ Premi X per uscire.")

click_coords = []


def onclick(event):
    if event.inaxes == ax:
        x, y = int(event.xdata), int(event.ydata)
        click_coords.clear()
        click_coords.append((x, y))
        print(f"📍 Coordinate cliccate: x={x}, y={y}")


fig.canvas.mpl_connect('button_press_event', onclick)


def onkey(event):
    global fit_n
    global INFO_LIST
    global fwhm_ave
    global x_center_abs
    global y_center_abs
    if event.key == 'enter' and click_coords:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xmin, xmax = int(np.floor(xlim[0])), int(np.ceil(xlim[1]))
        ymin, ymax = int(np.floor(ylim[0])), int(np.ceil(ylim[1]))

        xmin = max(xmin, 0)
        ymin = max(ymin, 0)
        xmax = min(xmax, data.shape[1] - 1)
        ymax = min(ymax, data.shape[0] - 1)

        sub_image = data[ymin:ymax, xmin:xmax]
        if sub_image.size == 0:
            print("❌ Sottoimmagine vuota, prova a zoomare meglio.")
            return

        # PARAMETRI INIZIALI DEL FIT
        y_indices, x_indices = np.mgrid[0:sub_image.shape[0], 0:sub_image.shape[1]]
        x0, y0 = click_coords[0]
        x0_local = x0 - xmin
        y0_local = y0 - ymin

        amplitude_init = sub_image.max() - sub_image.min()
        offset_init = sub_image.min()
        sigma_init = 3
        initial_guess = (amplitude_init, x0_local, y0_local, sigma_init, sigma_init, offset_init)

        try:
            popt_prelim, _ = curve_fit(twoD_Gaussian,
                                       (x_indices, y_indices),
                                       sub_image.ravel(),
                                       p0=initial_guess)
        except RuntimeError:
            print("❌ Fit preliminare non riuscito, usa un altro punto o zoom.")
            return

        _, x_center, y_center, _, _, _ = popt_prelim

        lato = max(sub_image.shape[0], sub_image.shape[1])
        lato = int(np.ceil(lato))
        half_lato = lato // 2

        x_center_global = x_center + xmin
        y_center_global = y_center + ymin

        x_min_new = int(round(x_center_global)) - half_lato
        x_max_new = x_min_new + lato
        y_min_new = int(round(y_center_global)) - half_lato
        y_max_new = y_min_new + lato

        if x_min_new < 0:
            x_max_new += -x_min_new
            x_min_new = 0
        if y_min_new < 0:
            y_max_new += -y_min_new
            y_min_new = 0
        if x_max_new > data.shape[1]:
            diff = x_max_new - data.shape[1]
            x_min_new = max(0, x_min_new - diff)
            x_max_new = data.shape[1]
        if y_max_new > data.shape[0]:
            diff = y_max_new - data.shape[0]
            y_min_new = max(0, y_min_new - diff)
            y_max_new = data.shape[0]

        sub_image_centrata = data[y_min_new:y_max_new, x_min_new:x_max_new]
        if sub_image_centrata.size == 0:
            print("❌ Sottoimmagine centrata vuota, controlla i limiti.")
            return

        y_idx_centrata, x_idx_centrata = np.mgrid[0:sub_image_centrata.shape[0], 0:sub_image_centrata.shape[1]]

        x0_new = x_center_global - x_min_new
        y0_new = y_center_global - y_min_new

        amplitude_init2 = sub_image_centrata.max() - sub_image_centrata.min()
        offset_init2 = sub_image_centrata.min()
        initial_guess2 = (amplitude_init2, x0_new, y0_new, sigma_init, sigma_init, offset_init2)

        try:
            popt, pcov = curve_fit(twoD_Gaussian,
                                   (x_idx_centrata, y_idx_centrata),
                                   sub_image_centrata.ravel(),
                                   p0=initial_guess2)
        except RuntimeError:
            print("❌ Fit definitivo non riuscito.")
            return

        amp, x_center_fit, y_center_fit, sigma_x, sigma_y, offset = popt
        fwhm_x = sigma_to_fwhm(sigma_x)
        fwhm_y = sigma_to_fwhm(sigma_y)
        fwhm_ave = (fwhm_x + fwhm_y) / 2.0

        # Calcolo incertezze sui parametri
        perr = np.sqrt(np.diag(pcov))
        amp_err, x_center_err, y_center_err, sigma_x_err, sigma_y_err, offset_err = perr
        fwhm_x_err = sigma_to_fwhm(sigma_x_err)
        fwhm_y_err = sigma_to_fwhm(sigma_y_err)
        fwhm_ave_err = (fwhm_x_err + fwhm_y_err) / 2.0

        x_center_abs = x_center_fit + x_min_new
        y_center_abs = y_center_fit + y_min_new

        print("\n✅ Fit definitivo riuscito:")
        print(
            f"  • Centroide (x, y): ({x_center_abs:.2f} ± {x_center_err:.2f}, {y_center_abs:.2f} ± {y_center_err:.2f})")
        print(f"  • Ampiezza: {amp:.2f} ± {amp_err:.2f}")
        print(f"  • FWHM X: {fwhm_x:.2f} ± {fwhm_x_err:.2f} px")
        print(f"  • FWHM Y: {fwhm_y:.2f} ± {fwhm_y_err:.2f} px")
        print(f"  • FWHM MEDIA: {fwhm_ave:.2f} ± {fwhm_ave_err:.2f} px")
        print(f"  • Offset: {offset:.2f} ± {offset_err:.2f}")

        # Scrivi i risultati nel file di log
        log_file.write(
            f"{x_center_abs:.2f}\t{y_center_abs:.2f}\t{fwhm_x:.2f}\t{fwhm_y:.2f}\t{fwhm_ave:.2f}\t{amp:.2f}\t{offset:.2f}\n")
        log_file.flush()

        ax.set_xlim(x_center_abs - lato / 2, x_center_abs + lato / 2)
        ax.set_ylim(y_center_abs - lato / 2, y_center_abs + lato / 2)
        fig.canvas.draw_idle()

        fig_x, ax_x = plt.subplots()
        x_vals = np.arange(sub_image_centrata.shape[1])
        data_x = sub_image_centrata[int(round(y_center_fit)), :]
        fit_x = twoD_Gaussian((x_vals, np.full_like(x_vals, y_center_fit)), *popt).reshape(-1)
        ax_x.plot(x_vals, data_x, 'o', label='Dati (X)')
        ax_x.plot(x_vals, fit_x, 'r--', label='Fit Gaussiano')
        ax_x.set_title("Profilo lungo X")
        ax_x.set_xlabel("Pixel X")
        ax_x.set_ylabel("Intensità")
        ax_x.legend()
        fig_x.savefig(f"profile_x_{int(x_center_abs)}_{int(y_center_abs)}_{int(fit_n)}.png")

        fig_y, ax_y = plt.subplots()
        y_vals = np.arange(sub_image_centrata.shape[0])
        data_y = sub_image_centrata[:, int(round(x_center_fit))]
        fit_y = twoD_Gaussian((np.full_like(y_vals, x_center_fit), y_vals), *popt).reshape(-1)
        ax_y.plot(y_vals, data_y, 'o', label='Dati (Y)')
        ax_y.plot(y_vals, fit_y, 'r--', label='Fit Gaussiano')
        ax_y.set_title("Profilo lungo Y")
        ax_y.set_xlabel("Pixel Y")
        ax_y.set_ylabel("Intensità")
        ax_y.legend()
        fig_y.savefig(f"profile_y_{int(x_center_abs)}_{int(y_center_abs)}_{int(fit_n)}.png")

        fig_fit, ax_fit = plt.subplots()
        ax_fit.imshow(sub_image_centrata, origin='lower', cmap='gray')
        ax_fit.set_title("Immagine con centroide stimato")
        ax_fit.plot(x_center_fit, y_center_fit, 'r+', markersize=12)
        fig_fit.savefig(f"fit_image_{int(x_center_abs)}_{int(y_center_abs)}_{int(fit_n)}.png")

        plt.show()
        fit_n = fit_n + 1


    elif event.key == 'c' and click_coords:
        # Prepara immagine centrata sulla stella
        x_click, y_click = click_coords[0]
        size = 50  # dimensione ritaglio (puoi modificarla)

        x_min = int(x_click - size // 2)
        x_max = int(x_click + size // 2)
        y_min = int(y_click - size // 2)
        y_max = int(y_click + size // 2)

        # Controlla bordi
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(data.shape[1], x_max)
        y_max = min(data.shape[0], y_max)

        cutout = data[y_min:y_max, x_min:x_max]

        # Setup figura
        fig_c, ax_c = plt.subplots(figsize=(6, 6))
        plt.subplots_adjust(bottom=0.25)

        img = ax_c.imshow(cutout, origin='lower', cmap='gray', vmin=slider_vmin.val, vmax=slider_vmax.val)
        contours = [10]  # valore iniziale temporaneo
        contour_plot = ax_c.contour(cutout, levels=contours, colors='cyan')

        ax_c.set_title("Centroide al centro con curve di livello")

        # Slider: livello, min e max
        axcolor = 'lightgoldenrodyellow'
        ax_level = plt.axes([0.15, 0.15, 0.7, 0.03], facecolor=axcolor)
        ax_cmin = plt.axes([0.15, 0.10, 0.7, 0.03], facecolor=axcolor)
        ax_cmax = plt.axes([0.15, 0.05, 0.7, 0.03], facecolor=axcolor)

        slider_levels = Slider(ax_level, 'Livelli', 1, 50, valinit=10, valstep=1)
        slider_cmin = Slider(ax_cmin, 'Valore Min', float(np.min(cutout)), float(np.max(cutout)),
                             valinit=np.percentile(cutout, 50))
        slider_cmax = Slider(ax_cmax, 'Valore Max', float(np.min(cutout)), float(np.max(cutout)),
                             valinit=np.percentile(cutout, 95))

        # Funzione per aggiornare i contorni
        def update_contour(val):
            nonlocal contour_plot

            # Rimuovi i vecchi contorni, se presenti
            if contour_plot:
                for coll in contour_plot.collections:
                    try:
                        coll.remove()
                    except ValueError:
                        pass  # la collection era già stata rimossa o non è più valida

            n_levels = int(slider_levels.val)
            cmin = slider_cmin.val
            cmax = slider_cmax.val

            if cmin >= cmax:
                return

            levels = np.linspace(cmin, cmax, n_levels)
            contour_plot = ax_c.contour(cutout, levels=levels, colors='cyan')
            fig_c.canvas.draw_idle()

        slider_levels.on_changed(update_contour)
        slider_cmin.on_changed(update_contour)
        slider_cmax.on_changed(update_contour)

        plt.show()

    elif event.key == 'i':
        print("ℹ️ Informazioni sull'immagine.")
        print("--------------------------------")
        print("NAXIS1: ", INFO_LIST[0])
        print("NAXIS2: ", INFO_LIST[1])
        print("TELESCOPE: ", INFO_LIST[3])
        print("INSTRUMENT: ", INFO_LIST[2])
        print("OBJECT: ", INFO_LIST[4])
        print("EXPTIME: ", INFO_LIST[5])
        print("RA: ", INFO_LIST[8])
        print("DEC: ", INFO_LIST[7])
        print("DATE-OBS: ", INFO_LIST[6])
        print("-------------------------------")

    elif event.key == 'a':
        print("📷 Fotometria di apertura e S/N.")
        if (fwhm_ave and x_center_abs and y_center_abs):

            aperture_radius = fwhm_ave
            sky_annulus_inner = aperture_radius * 1.5
            sky_annulus_outer = aperture_radius * 2.5

            y_indices, x_indices = np.indices(data.shape)
            r = np.sqrt((x_indices - x_center_abs)**2 + (y_indices - y_center_abs)**2)

            # Apertura (cerchio sulla stella)
            mask_star = r <= aperture_radius
            flux_star = np.sum(data[mask_star])
            area_star = np.sum(mask_star)

            # Anello di cielo
            mask_sky = (r >= sky_annulus_inner) & (r <= sky_annulus_outer)
            if np.sum(mask_sky) == 0:
                print("⚠️  Anello di cielo troppo piccolo o fuori dai bordi.")
                return

            sky_values = data[mask_sky]
            sky_median = np.median(sky_values)
            sky_std = np.std(sky_values)

            # Sottrazione del cielo
            sky_flux_total = sky_median * area_star
            net_flux = flux_star - sky_flux_total

            # Rumore (assumendo fondo dominante)
            noise = np.sqrt(area_star) * sky_std
            sn_ratio = net_flux / noise if noise > 0 else np.nan

            print("\n📷 Fotometria di apertura:")
            print(f"  • Raggio apertura: {aperture_radius:.2f} px")
            print(f"  • Flusso stella grezzo: {flux_star:.2f}")
            print(f"  • Flusso cielo stimato: {sky_flux_total:.2f}")
            print(f"  • Flusso netto: {net_flux:.2f}")
            print(f"  • Rumore stimato: {noise:.2f}")
            print(f"  • S/N: {sn_ratio:.2f}")

            # ================================
            # 🔍 Figura con cerchi di fotometria
            # ================================

            # Dimensione ritaglio centrato sulla stella
            box_size = int(sky_annulus_outer * 2.2)  # un po' oltre l'anello esterno
            half_box = box_size // 2

            x_min = int(x_center_abs - half_box)
            x_max = int(x_center_abs + half_box)
            y_min = int(y_center_abs - half_box)
            y_max = int(y_center_abs + half_box)

            # Controllo bordi
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(data.shape[1], x_max)
            y_max = min(data.shape[0], y_max)

            sub_img = data[y_min:y_max, x_min:x_max]

            # Nuova figura
            fig_ap, ax_ap = plt.subplots(figsize=(6, 6))
            img_ap = ax_ap.imshow(sub_img, origin='lower', cmap='gray',
                                  vmin=slider_vmin.val, vmax=slider_vmax.val)

            # Centri locali
            x0 = x_center_abs - x_min
            y0 = y_center_abs - y_min

            # Cerchi: apertura e anello
            from matplotlib.patches import Circle

            circle_aperture = Circle((x0, y0), aperture_radius, color='blue', fill=False, linewidth=1.5, label='Apertura')
            circle_sky_in = Circle((x0, y0), sky_annulus_inner, color='red', fill=False, linestyle='--', linewidth=1, label='Fondo (interno)')
            circle_sky_out = Circle((x0, y0), sky_annulus_outer, color='red', fill=False, linestyle='--', linewidth=1, label='Fondo (esterno)')

            for circ in [circle_aperture, circle_sky_in, circle_sky_out]:
                ax_ap.add_patch(circ)

            ax_ap.set_title("📷 Fotometria di Apertura")
            ax_ap.legend(loc='upper right')
            plt.show()
            # DOPO IL PLOT LE VARIABILI SONO RIFISSATE A NONE
            
            fwhm_ave=None
            x_center_abs=None
            y_center_abs=None

        else:
            print("⚠️  Fotometria non disponibile. Esegui prima il fit (ENTER).")
            return



    elif event.key == 'x':
        print("⛔ Uscita richiesta. Chiusura del programma.")
        log_file.close()  # chiudi il file di log prima di uscire
        plt.close('all')


fig.canvas.mpl_connect('key_press_event', onkey)

axcolor = 'lightgoldenrodyellow'
ax_vmin = plt.axes([0.15, 0.12, 0.65, 0.03], facecolor=axcolor)
ax_vmax = plt.axes([0.15, 0.08, 0.65, 0.03], facecolor=axcolor)

slider_vmin = Slider(ax_vmin, 'Contrasto Min', float(data.min()), float(data.max()), valinit=vmin_init)
slider_vmax = Slider(ax_vmax, 'Contrasto Max', float(data.min()), float(data.max()), valinit=vmax_init)


def update_contrast(val):
    vmin = slider_vmin.val
    vmax = slider_vmax.val
    if vmin < vmax:
        cax.set_clim(vmin, vmax)
        fig.canvas.draw_idle()


slider_vmin.on_changed(update_contrast)
slider_vmax.on_changed(update_contrast)

plt.show()
