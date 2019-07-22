import numpy as np
import pvlib
import datetime

data = np.loadtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\m300_data_filtered.txt', 
        delimiter = ',')

datetimestring = np.genfromtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\m300_datetime.txt', 
        dtype='str', delimiter = '\n')

datetimeobject = []
for i in range(len(datetimestring)):
    datetimeobject.append(datetime.datetime.strptime(datetimestring[i], 
                                                     '%d-%b-%Y %H:%M:%S'))
    

panel_location = pvlib.location.Location(latitude=45.641603,longitude=5.875387, 
                                         tz=1, altitude=234)

Airmass = panel_location.get_airmass(times=datetimeobject)

airmass_array = np.array(Airmass['airmass_relative'])
relative_airmass = np.zeros((len(airmass_array),1))
for i in range(len(airmass_array)):
    relative_airmass[i,0] = airmass_array[i]


data = np.append(data, relative_airmass, 1)

np.savetxt(fname='C:\\Users\\Marcos\\Desktop\\datos modelado\\m300_data_filtered_complete.txt', 
           X=data, delimiter=',', fmt='%.10f')

####################

IscDNI = data[:, 25]
DNI = data[:, 16]

module_params = {'gamma_ref' : 4.456, 'mu_gamma' : 0.0012, 'I_L_ref' : 3.346, 
                 'I_o_ref' : 0.000000000004, 'R_sh_ref' : 4400, 
                 'R_sh_0': 17500, 'R_sh_exp' : 5.50, 'R_s' : 0.736, 
                 'alpha_sc' : 0.00, 'irrad_ref' : 1000, 'temp_ref' : 25, 
                 'cells_in_series' : 42}

csys = CPVSystem(module=None, module_parameters=module_params,
                 modules_per_string=1, strings_per_inverter=1,
                 inverter=None, inverter_parameters=None,
                 racking_model='freestanding',
                 losses_parameters=None, name=None)

celltemp = csys.pvsyst_celltemp(data[:, 17], data[:, 10], data[:, 8])

(photocurrent, saturation_current, resistance_series,
         resistance_shunt, nNsVth) = (csys.calcparams_pvsyst(DNI, celltemp))

csys.diode_params = (photocurrent, saturation_current, resistance_series, 
                     resistance_shunt, nNsVth)

csys.dc = csys.singlediode(photocurrent, saturation_current, resistance_series,
                           resistance_shunt, nNsVth)

#######################

nontemp_data = np.loadtxt('C:\\Users\\Marcos\\Desktop\\datos modelado\\nontemp_measurements.txt', 
                          delimiter = ',')

nontemp_IscDNI = nontemp_data[:, 25]
nontemp_airmass = nontemp_data[:, 33]

import statistics as stats

IscDNI_medians = []
Airmass_aux = []
for i in np.arange(1,2.8,0.1):
    array_aux1 = []
    for j in range(len(nontemp_IscDNI)):
        if nontemp_airmass[j] > i-0.05 and nontemp_airmass[j] < i+0.05:
            array_aux1.append(nontemp_IscDNI[j])
    if len(array_aux1) > 0:
        IscDNI_medians.append(stats.median(array_aux1))
        Airmass_aux.append(i)

#m_low, n_low, m_high, n_high, thld = calc_uf_lines_airmass(Airmass_aux, IscDNI_medians)
m_low, n_low, error1 = calc_regression_line(Airmass_aux[:10], 
                                            IscDNI_medians[:10])
m_high, n_high, error2 = calc_regression_line(Airmass_aux[10:], 
                                              IscDNI_medians[10:])
thld = (n_high - n_low) / (m_low - m_high)

x = np.arange(1,5,0.1)
y1 = m_low * x + n_low
y2 = m_high * x + n_high

import matplotlib.pyplot as plt
plt.plot(nontemp_airmass, nontemp_IscDNI, 'b.', Airmass_aux, IscDNI_medians, 
         'g.', x, y1, 'g', x, y2, 'r')

max_IscDNI = m_low * thld + n_low
uf_am = []
for i in range(len(airmass_array)):
    uf_am.append(get_single_util_factor(airmass_array[i], thld, 
                                        m_low/max_IscDNI, m_high/max_IscDNI))

####################

nonairmass_data = np.loadtxt('C:\\Users\\Marcos\\Desktop\\datos modelado\\nonairmass_measurements.txt', 
                             delimiter = ',')

nonairmass_IscDNI = nonairmass_data[:, 25]
nonairmass_temp = nonairmass_data[:, 10]
m_low, n_low, m_high, n_high, thld = calc_uf_lines(nonairmass_temp, 
                                                   nonairmass_IscDNI,
                                                   'temp_air')

max_IscDNI = m_low * thld + n_low

AmbientTemp = data[:,10]

uf_at = []
for i in range(len(airmass_array)):
    uf_at.append(get_single_util_factor(AmbientTemp[i], thld, 
                                        m_low/max_IscDNI, m_high/max_IscDNI))

####################

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

