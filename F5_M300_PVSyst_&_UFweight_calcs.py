# Aplicación del modelo PVSyst

module_params = {'gamma_ref' : 4.456, 'mu_gamma' : 0.0012, 'I_L_ref' : 3.346, 
                 'I_o_ref' : 0.000000000004, 'R_sh_ref' : 4400, 
                 'R_sh_0': 17500, 'R_sh_exp' : 5.50, 'R_s' : 0.736, 
                 'alpha_sc' : 0.00, 'EgRef' : 1.87, 'irrad_ref' : 1000, 
                 'temp_ref' : 25, 'cells_in_series' : 42, 'eta_m' : 0.29, 
                 'alpha_absorption' : 0.9}

csys = CPVSystem(module=None, module_parameters=module_params,
                 modules_per_string=1, strings_per_inverter=1,
                 inverter=None, inverter_parameters=None,
                 racking_model='freestanding',
                 losses_parameters=None, name=None)

GNI = data[:, 17]
AmbientTemp = data[:, 10]
WindSpeed = data[:, 8]

celltemp = csys.pvsyst_celltemp(GNI, AmbientTemp, WindSpeed)

DNI = data[:, 16]

(photocurrent, saturation_current, resistance_series,
         resistance_shunt, nNsVth) = (csys.calcparams_pvsyst(DNI, celltemp))

csys.diode_params = (photocurrent, saturation_current, resistance_series, 
                     resistance_shunt, nNsVth)

csys.dc = csys.singlediode(photocurrent, saturation_current, resistance_series,
                           resistance_shunt, nNsVth)


# Obtención de los Pesos para los Factores de Utilización

real_power = data[:, 4]
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



AirMass = data[:,33]
real_voltage = data[:, 0]
estimation_volt = csys.dc['v_oc']

residuals_volt = estimation_volt - real_voltage

plt.plot(AirMass, residuals_volt, 'b.')


real_current = data[:, 1]
estimation_curr = csys.dc['i_sc']

residuals_curr = estimation_curr - real_current

plt.plot(AirMass, residuals_curr, 'b.')








