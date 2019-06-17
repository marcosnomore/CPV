"""
The ``cpvsystem`` module contains functions for modeling the output and
performance of CPV modules.
"""

from pvlib import pvsystem
from collections import OrderedDict
import io
import os
import numpy as np
import pandas as pd

from pvlib import atmosphere, irradiance, tools, singlediode as _singlediode
from pvlib.tools import _build_kwargs
from pvlib.location import Location

import math
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score


class CPVSystem(object):
    """
    The CPVSystem class defines a set of CPV system attributes and modeling 
    functions. This class describes the collection and interactions of CPV 
    system components installed on a Dual Axis Tracker.

    The class supports basic system topologies consisting of:

        * `N` total modules arranged in series
          (`modules_per_string=N`, `strings_per_inverter=1`).
        * `M` total modules arranged in parallel
          (`modules_per_string=1`, `strings_per_inverter=M`).
        * `NxM` total modules arranged in `M` strings of `N` modules each
          (`modules_per_string=N`, `strings_per_inverter=M`).

    The class is complementary to the module-level functions.

    The attributes should generally be things that don't change about
    the system, such the type of module and the inverter. The instance
    methods accept arguments for things that do change, such as
    irradiance and temperature.

    Parameters
    ----------
    module : None or string, default None
        The model name of the modules.
        May be used to look up the module_parameters dictionary
        via some other method.

    module_parameters : None, dict or Series, default None
        Module parameters as defined by the SAPM, CEC, or other.

    modules_per_string: int or float, default 1
        See system topology discussion above.

    strings_per_inverter: int or float, default 1
        See system topology discussion above.

    inverter : None or string, default None
        The model name of the inverters.
        May be used to look up the inverter_parameters dictionary
        via some other method.

    inverter_parameters : None, dict or Series, default None
        Inverter parameters as defined by the SAPM, CEC, or other.

    racking_model : None or string, default 'open_rack_cell_glassback'
        Used for cell and module temperature calculations.

    losses_parameters : None, dict or Series, default None
        Losses parameters as defined by PVWatts or other.

    name : None or string, default None

    **kwargs
        Arbitrary keyword arguments.
        Included for compatibility, but not used.
    """

    def __init__(self,
                 module=None, module_parameters=None,
                 modules_per_string=1, strings_per_inverter=1,
                 inverter=None, inverter_parameters=None,
                 racking_model='open_rack_cell_glassback',
                 losses_parameters=None, name=None, **kwargs):

        self.name = name

        # could tie these together with @property
        self.module = module
        if module_parameters is None:
            self.module_parameters = {}
        else:
            self.module_parameters = module_parameters

        self.modules_per_string = modules_per_string
        self.strings_per_inverter = strings_per_inverter

        self.inverter = inverter
        if inverter_parameters is None:
            self.inverter_parameters = {}
        else:
            self.inverter_parameters = inverter_parameters

        if losses_parameters is None:
            self.losses_parameters = {}
        else:
            self.losses_parameters = losses_parameters

        self.racking_model = racking_model

    def __repr__(self):
        attrs = ['name', 'module', 'inverter', 'racking_model']
        return ('PVSystem: \n  ' + '\n  '.join(
            ('{}: {}'.format(attr, getattr(self, attr)) for attr in attrs)))

    def get_irradiance(self, solar_zenith, solar_azimuth, dni, ghi, dhi,
                       dni_extra=None, airmass=None, model='haydavies',
                       **kwargs):
        """
        Uses the :py:func:`irradiance.get_total_irradiance` function to
        calculate the plane of array irradiance components on a Dual axis 
        tracker.

        Parameters
        ----------
        solar_zenith : float or Series.
            Solar zenith angle.
        solar_azimuth : float or Series.
            Solar azimuth angle.
        dni : float or Series
            Direct Normal Irradiance
        ghi : float or Series
            Global horizontal irradiance
        dhi : float or Series
            Diffuse horizontal irradiance
        dni_extra : None, float or Series, default None
            Extraterrestrial direct normal irradiance
        airmass : None, float or Series, default None
            Airmass
        model : String, default 'haydavies'
            Irradiance model.

        **kwargs
            Passed to :func:`irradiance.total_irrad`.

        Returns
        -------
        poa_irradiance : DataFrame
            Column names are: ``total, beam, sky, ground``.
        """

        # not needed for all models, but this is easier
        if dni_extra is None:
            dni_extra = irradiance.get_extra_radiation(solar_zenith.index)

        if airmass is None:
            airmass = atmosphere.get_relative_airmass(solar_zenith)

        return irradiance.get_total_irradiance(90 - solar_zenith,
                                               solar_azimuth,
                                               solar_zenith, solar_azimuth,
                                               dni, ghi, dhi,
                                               dni_extra=dni_extra,
                                               airmass=airmass,
                                               model=model,
                                               albedo=self.albedo,
                                               **kwargs)

    def calcparams_pvsyst(self, effective_irradiance, temp_cell):
        """
        Use the :py:func:`pvsystem.calcparams_pvsyst` function, the input
        parameters and ``self.module_parameters`` to calculate the
        module currents and resistances.

        Parameters
        ----------
        effective_irradiance : numeric
            The irradiance (W/m2) that is converted to photocurrent.

        temp_cell : float or Series
            The average cell temperature of cells within a module in C.

        Returns
        -------
        See pvsystem.calcparams_pvsyst for details
        """

        kwargs = _build_kwargs(['gamma_ref', 'mu_gamma', 'I_L_ref', 'I_o_ref',
                                'R_sh_ref', 'R_sh_0', 'R_sh_exp',
                                'R_s', 'alpha_sc', 'EgRef',
                                'irrad_ref', 'temp_ref',
                                'cells_in_series'],
                               self.module_parameters)

        return pvsystem.calcparams_pvsyst(effective_irradiance, 
                                          temp_cell, **kwargs)

    def pvsyst_celltemp(self, poa_global, temp_air, wind_speed=1.0):
        """
        Uses :py:func:`pvsystem.pvsyst_celltemp` to calculate module 
        temperatures based on ``self.racking_model`` and the input parameters.

        Parameters
        ----------
        See pvsystem.pvsyst_celltemp for details

        Returns
        -------
        See pvsystem.pvsyst_celltemp for details
        """
        
        kwargs = _build_kwargs(['eta_m', 'alpha_absorption'],
                               self.module_parameters)
        
        return pvsystem.pvsyst_celltemp(poa_global, temp_air, wind_speed, 
                                        model_params=self.racking_model, 
                                        **kwargs)
 
    def singlediode(self, photocurrent, saturation_current,
                    resistance_series, resistance_shunt, nNsVth,
                    ivcurve_pnts=None):
        """Wrapper around the :py:func:`pvsystem.singlediode` function.

        Parameters
        ----------
        See pvsystem.singlediode for details

        Returns
        -------
        See pvsystem.singlediode for details
        """
        
        return pvsystem.singlediode(photocurrent, saturation_current, 
                                    resistance_series, resistance_shunt, 
                                    nNsVth, ivcurve_pnts=ivcurve_pnts)

    def get_am_util_factor(self, airmass, am_thld, am_uf_m_low, am_uf_m_high):
        """
        Retrieves the utilization factor for airmass.
        
        Parameters
        ----------
        airmass : numeric
            absolute airmass.
        
        am_thld : numeric
            limit between the two regression lines of the utilization factor.
            
        am_uf_m_low : numeric
            inclination of the first regression line of the utilization factor 
            for airmass.
            
        am_uf_m_high : numeric
            inclination of the second regression line of the utilization factor 
            for airmass.
        
        Returns
        -------
        am_uf : numeric
            the utilization factor for airmass.
        """
        
        return get_single_util_factor(x = airmass, thld = am_thld, 
                                      m_low = am_uf_m_low,
                                      m_high = am_uf_m_high)
    
    def get_tempair_util_factor(self, temp_air, ta_thld, ta_uf_m_low, 
                                ta_uf_m_high):
        """
        Retrieves the utilization factor for ambient temperature. 
        
        Parameters
        ----------
        temp_air : numeric
            Ambient dry bulb temperature in degrees C.
            
        ta_thld : numeric
            limit between the two regression lines of the utilization factor.
            
        ta_uf_m_low : numeric
            inclination of the first regression line of the utilization factor 
            for ambient temperature.
            
        ta_uf_m_high : numeric
            inclination of the second regression line of the utilization factor 
            for ambient temperature.
        
        Returns
        -------
        ta_uf : numeric
            the utilization factor for ambient temperature.
        """
        
        return get_single_util_factor(x = temp_air, thld = ta_thld, 
                                      m_low = ta_uf_m_low,
                                      m_high = ta_uf_m_high)
    
    def get_dni_util_factor(self, dni, dni_thld, dni_uf_m_low, dni_uf_m_high):
        """
        Retrieves the utilization factor for SMR top-middle.
        
        Parameters
        ----------
        dni : numeric
            Direct Normal Irradiance
            
        dni_thld : numeric
            limit between the two regression lines of the utilization factor.
            
        dni_uf_m_low : numeric
            inclination of the first regression line of the utilization factor 
            for DNI.
            
        dni_uf_m_low_uf_m_high : numeric
            inclination of the second regression line of the utilization factor 
            for DNI.
        
        Returns
        -------
        dni_uf : numeric
            the utilization factor for DNI.
        """
                
        return get_single_util_factor(x = dni, thld = dni_thld, 
                                      m_low = dni_uf_m_low,
                                      m_high = dni_uf_m_high)
    
    def get_utilization_factor(self, airmass, am_thld, am_uf_m_low, 
                               am_uf_m_high, am_weight, temp_air, ta_thld, 
                               ta_uf_m_low, ta_uf_m_high, ta_weight, dni, 
                               dni_thld, dni_uf_m_low, dni_uf_m_high, 
                               dni_weight):
        """
        Retrieves the unified utilization factor for airmass, ambient 
        temperature and dni.
        
        Parameters
        ----------
        airmass : numeric
            absolute airmass.
        
        am_thld : numeric
            limit between the two regression lines of the utilization factor.
            
        am_uf_m_low : numeric
            inclination of the first regression line of the utilization factor 
            for airmass.
            
        am_uf_m_high : numeric
            inclination of the second regression line of the utilization factor 
            for airmass.
            
        am_weight : numeric
            ponderation for the airmass utilization factor.
            
        temp_air : numeric
            Ambient dry bulb temperature in degrees C.
            
        ta_thld : numeric
            limit between the two regression lines of the utilization factor.
            
        ta_uf_m_low : numeric
            inclination of the first regression line of the utilization factor 
            for ambient temperature.
            
        ta_uf_m_high : numeric
            inclination of the second regression line of the utilization factor 
            for ambient temperature.
            
        ta_weight : numeric
            ponderation for the ambient temperature utilization factor.
            
        dni : numeric
            Direct Normal Irradiance
            
        dni_thld : numeric
            limit between the two regression lines of the utilization factor.
            
        dni_uf_m_low : numeric
            inclination of the first regression line of the utilization factor 
            for DNI.
            
        dni_uf_m_low_uf_m_high : numeric
            inclination of the second regression line of the utilization factor 
            for DNI.
            
        dni_weight : numeric
            ponderation for the DNI utilization factor.
        
        Returns
        -------
        uf : numeric
            global utilization factor.
        """
        
        am_uf = get_single_util_factor(x = airmass, thld = am_thld, 
                                       m_low = am_uf_m_low,
                                       m_high = am_uf_m_high)
        
        ta_uf = get_single_util_factor(x = temp_air, thld = ta_thld, 
                                       m_low = ta_uf_m_low,
                                       m_high = ta_uf_m_high)
        
        dni_uf = get_single_util_factor(x = dni, thld = dni_thld, 
                                        m_low = dni_uf_m_low,
                                        m_high = dni_uf_m_high)
        
        uf = am_uf * am_weight + ta_uf * ta_weight + dni_uf * dni_weight
        
        return uf


def get_single_util_factor(x, thld, m_low, m_high):
    """
    Retrieves the utilization factor for a variable.
    
    Parameters
    ----------
    x : variable value for the utilization factor calc.
    
    thld : numeric
        limit between the two regression lines of the utilization factor.
    
    m_low : numeric
        inclination of the first regression line of the utilization factor.
    
    m_high : numeric
        inclination of the second regression line of the utilization factor.
    
    Returns
    -------
    single_uf : numeric
        utilization factor for the x variable.
    """
    
    if x <= thld:
        single_uf = 1 + (x - thld) * m_low
    
    else:
        single_uf = 1 + (x - thld) * m_high
    
    return single_uf


def calc_uf_lines(x, y):
    """
    Calculates the parameters of two regression lines for a utilization factor.
        
    Parameters
    ----------
    x : list or numpy.array of float
    
    y : list or numpy.array of float
    
    Returns
    -------
    m_low : numeric
        inclination of the first regression line of the utilization factor.
    
    n_low : numeric
        ordinate at the origin of the first regression line.
    
    m_high : numeric
        inclination of the second regression line of the utilization factor.
    
    n_high : numeric
        ordinate at the origin of the second regression line.
    
    thld : numeric
        limit between the two regression lines of the utilization factor.
    """
    
    # Auxiliar variables initialization.
    x_aux1 = []
    x_aux2 = []
    
    y_aux1 = [] 
    y_aux2 = [] 
    
    m_low, n_low, m_high, n_high, thld = 0, 0, 0, 0, 0
    rmsd = 10000
    
    # The x array is traversed in order to find the most fitting 
    # regression lines.
    for i in x:
        # The original measurements are divided into two sets by the limit.
        for j in range(len(x)):
            if x[j] < i:
                x_aux1.append(x[j])
                y_aux1.append(y[j])
            else:
                x_aux2.append(x[j])
                y_aux2.append(y[j])
                
        # Regression lines are calculated for the two sets.
        m_low_temp, n_low_temp, rmsd_low_temp = calc_regression_line(x_aux1, 
                                                                     y_aux1)
            
        m_high_temp, n_high_temp, rmsd_high_temp = calc_regression_line(x_aux2, 
                                                                        y_aux2)
        
        # Less suitable regression lines are rejected.
        rmsd_temp = rmsd_low_temp + rmsd_high_temp
        
        if rmsd_temp < rmsd:
            m_low = m_low_temp
            n_low = n_low_temp
            m_high = m_high_temp
            n_high = n_high_temp
    
    # The intersection between the two final regression lines is calculated.
    thld = (n_high - n_low) / (m_low - m_high)
    
    return m_low, n_low, m_high, n_high, thld


def calc_regression_line(x, y):
    """
    Wrapper for regression line calcs.
        
    Parameters
    ----------
    x : array of numbers
    
    y : array of numbers
    
    Returns
    -------
    m : numeric
        inclination of the regression line.
        
    n : numeric
        ordinate at the origin of the regression line.
        
    rmsd : numeric
        root-mean-square deviation between the regression line and the 
        measurements.
    """
    
    # Initial input treatment.
    if not isinstance(x, np.ndarray):
        x = np.array(x)
    x = x[:, np.newaxis]
    
    if not isinstance(y, np.ndarray):
        y = np.array(y)
    y = y[:, np.newaxis]
    
    # The regression line model is executed.
    model = linear_model.LinearRegression()
    model.fit(x, y)
    
    # Coeficients of the line are obtained.
    m = model.coef_[0][0]
    
    n = model.intercept_[0]
    
    # The root-mean-square deviation is calculated.
    y_pred = model.predict(x)
    
    rmsd = math.sqrt(mean_squared_error(y, y_pred))
    
    return m, n, rmsd




































