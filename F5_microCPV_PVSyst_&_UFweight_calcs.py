# Aplicación del modelo PVSyst

module_params = {'gamma_ref' : 5.524, 'mu_gamma' :R 0.0012, 'I_L_ref' : 0.96, 
                 'I_o_ref' :R 0.000000000004, 'R_sh_ref' : 5226, 
                 'R_sh_0': 21000, 'R_sh_exp' : 5.50, 'R_s' : 0.01, 
                 'alpha_sc' : 0.00, 'EgRef' : 1.87, 'irrad_ref' : 1000, 
                 'temp_ref' : 25, 'cells_in_series' : 12, 'eta_m' : 0.32, 
                 'alpha_absorption' : 0.9}

csys = CPVSystem(module=None, module_parameters=module_params,
                 modules_per_string=1, strings_per_inverter=1,
                 inverter=None, inverter_parameters=None,
                 racking_model='freestanding',
                 losses_parameters=None, name=None)

GNI = filt_data[:, 10]
AmbientTemp = filt_data[:, 8]
WindSpeed = filt_data[:, 11]

celltemp = csys.pvsyst_celltemp(GNI, AmbientTemp, WindSpeed)

IscDNI = np.divide(filt_data[:,5],filt_data[:,14])
DNI = filt_data[:, 14]

(photocurrent, saturation_current, resistance_series,
         resistance_shunt, nNsVth) = (csys.calcparams_pvsyst(DNI, celltemp))

csys.diode_params = (photocurrent, saturation_current, resistance_series, 
                     resistance_shunt, nNsVth)

csys.dc = csys.singlediode(photocurrent, saturation_current, resistance_series,
                           resistance_shunt, nNsVth)


# Obtención de los Pesos para los Factores de Utilización

real_power = filt_data[:, 2]
estimation = csys.dc['p_mp']

weight_am_final = 1.0
rmsd = 10000

for weight_am in np.arange(0,1,0.05):
    weight_at = 1.0 - weight_am
    
    modeled_power = estimation * (np.multiply(weight_am, uf_am) + 
                                  np.multiply(weight_at, uf_at))
    rmsd_temp = math.sqrt(mean_squared_error(real_power, modeled_power))
    
    if rmsd_temp < rmsd:
        weight_am_final = weight_am
        rmsd = rmsd_temp



AirMass = filt_data[:,24]
real_voltage = filt_data[:, 6]
estimation_volt = csys.dc['v_oc']

residuals_volt = estimation_volt - real_voltage

plt.plot(AirMass, residuals_volt, 'b.')


real_current = filt_data[:, 1]
estimation_curr = csys.dc['i_sc']

residuals_curr = estimation_curr - real_current

plt.plot(AirMass, residuals_curr, 'b.')








