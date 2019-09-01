# Fichero de aplicación del modelo PVSyst

filt_data = np.loadtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_data_filtered_complete_may.txt', 
        delimiter = ',')

GII = filt_data[:, 10]
AmbientTemp = filt_data[:, 6]
WindSpeed = filt_data[:, 7]
Airmass = filt_data[:, 17]

zenith = filt_data[:, 18]
azimuth = filt_data[:, 19]
aoi = scsys.get_aoi(solar_zenith=zenith, solar_azimuth=azimuth)

IscDNI_ast = 0.96/1000

aoi_thld = 61.27513380360832
aoi_mlow = 8.519370511455714e-07
aoi_mhigh = -1.8410812659460265e-05
am_thld = 4.574231933073185
am_mlow = 3.906372068620377e-06
am_mhigh = -3.0335768119184845e-05
at_thld = 150
at_mlow = 4.6781224141650075e-06
at_mhigh = 0

weight_am = 0.55
weight_at = 0.45

uf_aoi = []
uf_am = []
uf_at = []

# Obtención de los Factores de Utilización Simples y del UF Global:
for i in range(len(aoi)):
    uf_aoi.append(get_single_util_factor(aoi[i], aoi_thld, aoi_mlow/IscDNI_ast, 
                                         aoi_mhigh/IscDNI_ast))
    uf_am.append(get_single_util_factor(Airmass[i], am_thld, 
                                        am_mlow/IscDNI_ast, 
                                        am_mhigh/IscDNI_ast))
    uf_at.append(get_single_util_factor(AmbientTemp[i], at_thld, 
                                        at_mlow/IscDNI_ast, 
                                        at_mhigh/IscDNI_ast))
    
uf_am_at = np.multiply(weight_am, uf_am) + np.multiply(weight_at, uf_at)

UF_global = np.multiply(uf_am_at, uf_aoi)

# Aplicación del modelo PVSyst:
celltemp = scsys.pvsyst_celltemp(GII, AmbientTemp, WindSpeed)

DII = filt_data[:, 9]

(photocurrent, saturation_current, resistance_series,
         resistance_shunt, nNsVth) = (scsys.calcparams_pvsyst(DII, celltemp))

scsys.diode_params = (photocurrent, saturation_current, resistance_series, 
                     resistance_shunt, nNsVth)

scsys.dc = scsys.singlediode(photocurrent, saturation_current, resistance_series,
                           resistance_shunt, nNsVth)

# Obtención de la Potencia Estimada Corregida:

real_power = filt_data[:, 15]
estimation = scsys.dc['p_mp']

corrected_estimated_power = estimation * UF_global

rmsd = math.sqrt(mean_squared_error(real_power, corrected_estimated_power))




residuals_power = estimation - real_power

plt.plot(Airmass, residuals_power, 'b.')


real_current = filt_data[:, 12]
estimation_curr = scsys.dc['i_sc']

residuals_curr = estimation_curr - real_current

plt.plot(Airmass, residuals_curr, 'b.')

