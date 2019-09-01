# Cálculos de la Masa de Aire
import numpy as np
import pvlib
import datetime

data = np.loadtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_data.txt', 
        delimiter = ',')

datetimestring = np.genfromtxt(
        'C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_datestr.txt', 
        dtype='str', delimiter = '\n')

datetimeobject = []
for i in range(len(datetimestring)):
    datetimeobject.append(datetime.datetime.strptime(datetimestring[i], 
                                                     '%d-%b-%Y %H:%M'))
    

panel_location = pvlib.location.Location(latitude=40.453,longitude=-3.727, 
                                         tz=1, altitude=658)

Airmass = panel_location.get_airmass(times=datetimeobject)

airmass_array = np.array(Airmass['airmass_relative'])
relative_airmass = np.zeros((len(airmass_array),1))
for i in range(len(airmass_array)):
    relative_airmass[i,0] = airmass_array[i]


data = np.append(data, relative_airmass, 1)

np.savetxt(fname='C:\\Users\\Marcos\\Desktop\\datos modelado\\insolight_data_complete.txt', 
           X=data, delimiter=',', fmt='%.10f')
