# Cálculos de la Masa de Aire y de la Posición del Sol

import numpy as np
import pvlib
import datetime

data = np.loadtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_data_may.txt', 
        delimiter = ',')

datetimestring = np.genfromtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_datestr_may.txt', 
        dtype='str', delimiter = '\n')

datetimeobject = []
for i in range(len(datetimestring)):
    datetimeobject.append(datetime.datetime.strptime(datetimestring[i], 
                                                     '%d-%b-%Y %H:%M:%S'))
    

panel_location = pvlib.location.Location(latitude=40.453,longitude=-3.727, 
                                         tz=1, altitude=658)

Airmass = panel_location.get_airmass(times=datetimeobject)

Solar_pos = panel_location.get_solarposition(times=datetimeobject, 
                                             pressure=None, 
                                             temperature=data[:,6])

airmass_array = np.array(Airmass['airmass_relative'])
zenith_array = np.array(Solar_pos['zenith'])
azimuth_array = np.array(Solar_pos['azimuth'])

relative_airmass = np.zeros((len(airmass_array),1))
zenith_array_aux = np.zeros((len(zenith_array),1))
azimuth_array_aux = np.zeros((len(azimuth_array),1))

for i in range(len(airmass_array)):
    relative_airmass[i,0] = airmass_array[i]
    zenith_array_aux[i,0] = zenith_array[i]
    azimuth_array_aux[i,0] = azimuth_array[i]

data = np.append(data, relative_airmass, 1)
data = np.append(data, zenith_array_aux, 1)
data = np.append(data, azimuth_array_aux, 1)

np.savetxt(fname='C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_data_complete_may.txt', 
           X=data, delimiter=',', fmt='%.10f')
