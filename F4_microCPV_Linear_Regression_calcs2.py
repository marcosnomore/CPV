# Carga y Procesado de Datos

filt_data = np.loadtxt('C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_data_filtered_complete_may.txt', 
                          delimiter = ',')

IscDII = np.divide(filt_data[:,12],filt_data[:,9])
Pmp = filt_data[:, 15]
zenith = filt_data[:, 18]
azimuth = filt_data[:, 19]


# Se calcula el AOI y su UF
module_params = {'gamma_ref' : 5.524, 'mu_gamma' : 0.003, 'I_L_ref' : 0.96, 
                 'I_o_ref' : 0.00000000017, 'R_sh_ref' : 5226, 
                 'R_sh_0': 21000, 'R_sh_exp' : 5.50, 'R_s' : 0.01, 
                 'alpha_sc' : 0.00, 'EgRef' : 3.91, 'irrad_ref' : 1000, 
                 'temp_ref' : 25, 'cells_in_series' : 12, 'eta_m' : 0.32, 
                 'alpha_absorption' : 0.9}

scsys = StaticCPVSystem(surface_tilt=30, surface_azimuth=180, module=None, 
                 module_parameters=module_params, modules_per_string=1, 
                 strings_per_inverter=1, inverter=None, 
                 inverter_parameters=None, racking_model='insulated',
                 losses_parameters=None, name=None)

aoi = scsys.get_aoi(solar_zenith=zenith, solar_azimuth=azimuth)

m_low, n_low, m_high, n_high, thld = calc_uf_lines(aoi, IscDII, limit=60)

x1 = np.arange(10,70,0.1)
y1 = m_low * x1 + n_low
x2 = np.arange(55,85,0.1)
y2 = m_high * x2 + n_high

import matplotlib.pyplot as plt
plt.plot(aoi, IscDII, 'b.', x1, y1, 'g', x2, y2, 'r')
plt.xlabel('Ángulo de Incidencia (º)')
plt.ylabel('Isc/DII (A/(W/m2))')
plt.title('Análisis de Isc/DII en función del Ángulo de Incidencia')
plt.savefig("grafica1.png", dpi=300)
