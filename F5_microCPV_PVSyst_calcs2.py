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

aoi_thld = 61.978505569631494
aoi_mlow = -2.716773886925838e-07
aoi_mhigh = -1.781998474992582e-05
am_thld = 4.574231933073185
am_mlow = 3.906372068620377e-06
am_mhigh = -3.0335768119184845e-05
at_thld = 50
at_mlow = 4.6781224141650075e-06
at_mhigh = 0

weight_am = 0.25
weight_at = 0.75

# Obtención de los Factores de Utilización Simples y del UF Global:
uf_am = get_simple_util_factor(Airmass, am_thld, am_mlow/IscDNI_ast, 
                               am_mhigh/IscDNI_ast)
uf_at = get_simple_util_factor(AmbientTemp, at_thld, at_mlow/IscDNI_ast, 
                               at_mhigh/IscDNI_ast)
    
uf_am_at = np.multiply(weight_am, uf_am) + np.multiply(weight_at, uf_at)

uf_aoi = get_simple_util_factor(aoi, aoi_thld, aoi_mlow/IscDNI_ast, 
                                aoi_mhigh/IscDNI_ast)
# Se normaliza el SUF(AOI):
uf_aoi_ast = get_simple_util_factor(0, aoi_thld, aoi_mlow/IscDNI_ast, 
                                     aoi_mhigh/IscDNI_ast)

uf_aoi_norm = np.divide(uf_aoi, uf_aoi_ast)

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


a= np.divide(real_power,corrected_estimated_power)
np.mean(a)
b= np.divide(real_power,estimation)
np.mean(b)
c= np.divide(filt_data[:, 12],scsys.dc['i_sc'])
np.mean(c)
np.mean(uf_aoi)

residuals_power = estimation - real_power

plt.plot(Airmass, residuals_power, 'b.')
plt.plot(AmbientTemp, residuals_power, 'b.')
plt.plot(aoi, residuals_power, 'b.')
plt.plot(aoi, corrected_estimated_power - real_power, 'b.')


real_current = filt_data[:, 12]
estimation_curr = scsys.dc['i_sc']

residuals_curr = estimation_curr - real_current

plt.plot(Airmass, residuals_curr, 'b.')

