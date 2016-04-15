#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013-2016 David Manthey
#
# Licensed under the Apache License, Version 2.0 ( the "License" ); you may
# not use this file except in compliance with the License.  You may obtain a
# copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Ballistics program for spherical projectiles.

See help for details.
"""

import math
import md5
import os
import pprint
import shutil
import sys
import time
import types

from formattext import line_break
from materials import determine_material, list_materials
from units import convert_units, list_units

# Modules that will get loaded if needed.  None of these are required.
csv = None
matplotlib = None
psutil = None
StringIO = None

# The version auto updates using the version_check() function.  The version is
# the date of the last update followed by a build number.  The program
# signature is the md5sum hash of the entire source code file excepting the 32
# characters of the signature string.  The following two lines should not be
# altered by hand unless you know what you are doing.
__version__ = '2016-04-13v33'
PROGRAM_SIGNATURE = '6fc567669c4bdd05cc72383a2449c475'

# The current state is stored in a dictionary with the following values:
# These values are specified initially:
#  initial_angle: initial trajectory angle in degrees, 0 is horizontal,
#      positive is up
#  charge: amount of gunpowder in kg
#  final_velocity: the final velocity at the ending range in m/s
#  initial_height: initial height above sea level in m
#  final_height: final height above sea level in m
#  power_factor: power factor of the powder in J/kg
#  range: total distance travelled by projectile in m
#  final_time: duration of flight in s
#  initial_velocity: the initial velocity of the projectile in m/s
#  max_height: the maximum height in m
#  time_delta: the time step for computations in s
# These values are specified initially and used directly in calculations:
#  diam: diameter in m
#  T: temperature in Kelvin
#  mass: mass in kilograms
#  rh: relative humidity, 0-100 (optional) (often called phi)
#  pressure: atmospheric pressure in Pa at pressure_y0 (optional)
#  pressure_y0: altitude of the specified pressure above sea level in m
#  material: the material of the projectile.  A text string.
#  material_density: the density of the material of the projectile in kg/m/m/m.
# These values are directly used in trajectory step calculations:
#  vx: velocity in the horizontal direction in m/s
#  vy: velocity in the vertical direction in m/s
#  y: altitude above sea level in m
# These items are updated as the various steps are computed:
#  time: elapsed time in s
#  x: horizontal distance travelled in m (starting at 0)
#  ax: acceleration in the x direction
#  ay: acceleration in the y direction
# These items are added during calculation:
#  density_data: a dictionary from density computation, including:
#      pressure: atmospheric pressure at the current point in Pa
#      xv: more fraction of water vapor
#      psv: vapor pressure at saturation in Pa
#      T: current temperature in K
#      h: relative humidity on a scale of [0-1]
#      density: atmospheric density in kg/(m^3)
#      y: current altitude above sea level in m
#  viscosity_data: a dictionary from viscosity computation, including:
#      mua: viscosity of dry air in  kg/m/s
#      muv: viscosity of water vapor in kg/m/s
#      mu: viscosity at the current point and conditions in kg/m/s
#  drag_data: a dictionary from coefficient of drag computation, including:
#      Re: Reynolds number based on viscosity, velcotiy, density, and diameter
#      sos: speed of sound in the current atmospheric conditions in m/s
#      Mn: Mach number in the current atmospheric conditions
#      critical_Re: one of the critical Reynolds numbers for the current Mach
#          conditions; this is the point of least drag at low speeds
#      cd: the computed coefficient of drag based on Re and Mn
#      in_range: True if cd was interpolated, false if extrapolated
# If the trajectory calculation fails, it can also contain:
#  error: the error that stopped the trajectory calculation.

GET_CPU_TIME = True

MinPointInterval = 0.01
PrecisionInDigits = 6
UseRungeKutta = True
Verbose = 0

# This table consists of a list of tuples of the form (Mach number, [List of
# (Reynolds Number, Coefficient of Drag)], critial Reynolds number).  The data
# for Mach number == 0 is taken from Munson, Bruce R., Donald F. Young, and
# Theodore H. Okiishi. "Fundamentals of Fluid Mechanics, Third Edition."  New
# York: John Wiley & Sons, Inc., 1998.  Fig. 9.21, p. 600.  The data for the
# other Mach numbers is taken from Miller, Donald G., and Allan B. Bailey.
# "Sphere drag at Mach numbers from 0.3 to 2.0 at Reynolds Numbers approaching
# 10^7."  Journal of Fluid Mechanics.  93, no. 3 (1979): 449-464.  Fig. 4, p.
# 456.  Selected points on each graph were estimated to form these tables; they
# should be viewed as approximations of the data from those sources.
MnReCdDataTable = [
    # data for Mach 0 as digitized from Munson
    # (0, [(1e-1, 124.9), (2e-1, 106.3), (4e-1, 54.95), (5e-1, 45.71),
    #      (1, 24.93), (5, 6.607), (10, 3.920), (50, 1.502), (100, 1.047),
    #      (500, 0.5012), (1e3, 0.4105), (2e3, 0.3743), (5e3, 0.3801),
    #      (1e4, 0.3890), (5e4, 0.4105), (1e5, 0.4169), (2e5, 0.3890),
    #      (4e5, 0.09261), (5e5, 0.08912), (6e5, 0.1063), (8e5, 0.1359),
    #      (1e6, 0.1622), (5e6, 0.3114), (1e7, 0.3388)]),
    # data for Mach 0 modified from Munson to match the expected values from
    # Miller at Re>1e4, and truncated to ignore values above 1e6 as they seem
    # weak
    (0, [(1e-1, 124.9), (2e-1, 106.3), (4e-1, 54.95), (5e-1, 45.71),
         (1, 24.93), (5, 6.607), (10, 3.920), (50, 1.502), (100, 1.047),
         (500, 0.5012), (1e3, 0.4105), (2e3, 0.3743), (5e3, 0.3801),
         (1e4, 0.3890), (3.2e4, 0.431), (7.1e4, 0.453), (1.5e5, 0.462),
         (2.3e5, 0.458), (3e5, 0.438), (3.5e5, 0.373), (3.954e5, 0.0916),
         (4.21e5, 0.0785), (5e5, 0.08912), (7.6e5, 0.158),
         (1e6, 0.20)], 4.21e5),
    (0.1, [(1e4, 0.3983), (3.093e4, 0.4352), (4.65e4, 0.4495)], 4.21e5),
    (0.2, [(1e4, 0.3995), (2.75e4, 0.4376), (4.874e4, 0.4590),
           (8.306e4, 0.4732), (1.484e5, 0.4792), (1.877e5, 0.4780)], 4.21e5),
    (0.3, [(1e4, 0.4126), (3.191e4, 0.4542), (7.101e4, 0.4768),
           (1.472e5, 0.4851), (2.302e5, 0.4816), (2.958e5, 0.4614),
           (3.488e5, 0.3960), (3.954e5, 0.0916), (4.21e5, 0.0785),
           (4.886e5, 0.0892), (7.58e5, 0.1593)], 4.21e5),
    (0.6, [(1e4, 0.4435), (2.369e4, 0.4685), (5.791e4, 0.4994),
           (1.137e5, 0.5220), (2.394e5, 0.5279), (3.571e5, 0.5113),
           (4.625e5, 0.4709), (5.082e5, 0.4031), (5.368e5, 0.2212),
           (5.583e5, 0.2117), (5.852e5, 0.2164), (7.232e5, 0.2580),
           (9.15e5, 0.3032), (1.323e6, 0.3591)], 5.583e5),
    (0.7, [(1e4, 0.4602), (1.613e4, 0.4709), (4.436e4, 0.5089),
           (8.984e4, 0.5375), (1.819e5, 0.5565), (3.2e5, 0.5577),
           (4.277e5, 0.5375), (5.082e5, 0.5030), (6.846e5, 0.4031),
           (8.394e5, 0.3520), (9.078e5, 0.3496), (1.054e6, 0.3650),
           (1.419e6, 0.4304), (1.927e6, 0.4875), (2.596e6, 0.5279),
           (3.552e6, 0.5517)], 9.078e5),
    (0.8, [(1e4, 0.4982), (1.691e4, 0.5137), (4.99e4, 0.5624),
           (1.405e5, 0.6052), (3.328e5, 0.6231), (5.244e5, 0.6231),
           (6.329e5, 0.6088), (7.404e5, 0.5743), (8.198e5, 0.5303),
           (9.742e5, 0.5054), (1.087e6, 0.5054), (1.476e6, 0.5363),
           (2.496e6, 0.5743), (3.842e6, 0.5945)], 9.963e5),
    (0.9, [(1e4, 0.5529), (1.704e4, 0.5672), (3.069e4, 0.5933),
           (5.029e4, 0.6219), (7.925e4, 0.6528), (1.722e5, 0.7075),
           (2.982e5, 0.7313), (8.798e5, 0.7384), (4.601e6, 0.7384)], 1e6),
    (1.0, [(1e4, 0.7146), (1.626e4, 0.7158), (3.618e4, 0.7408),
           (1.068e5, 0.7967), (2.413e5, 0.8300), (4.773e5, 0.8419),
           (5.257e6, 0.8407)], 1e6),
    (1.1, [(1e4, 0.7753), (1.917e4, 0.7895), (4.836e4, 0.8240),
           (1.076e5, 0.8656), (2.451e5, 0.8954), (5.162e5, 0.9061),
           (5.776e6, 0.9025)], 1e6),
    (1.2, [(1e4, 0.8193), (1.902e4, 0.8276), (5.313e4, 0.8609),
           (1.259e5, 0.8989), (3.276e5, 0.9298), (7.761e5, 0.9417),
           (7.194e6, 0.9417)], 1e6),
    (1.4, [(1e4, 0.8954), (1.815e4, 0.8906), (3.913e4, 0.9084),
           (8.571e4, 0.9394), (1.952e5, 0.9679), (3.832e5, 0.9834),
           (8.134e5, 0.9857), (1e7, 0.9810)], 1e6),
    (1.8, [(1e4, 0.9453), (1.412e4, 0.9382), (3.166e4, 0.9394),
           (7.74e4, 0.9572), (1.543e5, 0.9738), (2.651e5, 0.9822),
           (6.686e5, 0.9857), (1e7, 0.9810)], 1e6),
    (2.0, [(1e4, 0.9575), (2.15e4, 0.9391), (1e5, 0.9592), (1e6, 0.992),
           (1e7, 0.9932)], 1e6),
    (2.5, [(1e4, 0.9663), (3.3e4, 0.9288), (1e5, 0.9473), (1e6, 0.9691),
           (1e7, 0.973)], 1e6),
    (3.0, [(1e4, 0.9663), (3.3e4, 0.9288), (1e5, 0.9329), (1e6, 0.9485),
           (1e7, 0.9494)], 1e6),
    # Mach 4.5 is from Munson, fig 11.2, p. 709
    (4.5, [(1e4, 0.906), (1e7, 0.906)], 1e6),
    ]

Factors = {
    # properties are:
    #  long: long name used on command line
    #  short: short name (only one character) used on the command line
    #  units: internal units
    #  si: SI units used for output.  Defaults to units.
    #  eng: English or statute units used for output.  Defaults to units.
    #  title: title for output
    #  desc: description
    #  method: calculation method.  Either 'direct', 'scan', 'binary' (the
    #      default), or None.  See trajectory_error for details.
    #  min: the minimum value used for binary or scan calculation.  This may be
    #      a number if it is in the internal units of the factor, or be a
    #      string with units to explicitly specity the units.
    #  max: the maximum value used for binary or scan calculation.  See
    #      comments on min.
    #  step: the step used in scan calculation.  See comments on min.
    #  weak: if True, solving for this parameter is ill-conditioned.
    # units, 'desc': description, 'method': calculation method, either direct,
    # scan, or binary (the default), 'min':
    'charge': {
        'long': 'charge',
        'short': 'c',
        'units': 'kg',
        'eng': 'lb',
        'min': 0.001,
        'max': 100,
        'title': 'Powder Charge',
        'desc': 'Powder charge by weight.'
    },
    'diam': {
        'long': 'diameter',
        'short': 'd',
        'units': 'm',
        'eng': 'in',
        'min': 0.001,
        'max': 10,
        'weak': True,
        'title': 'Diameter',
        'desc': 'Diameter of projectile.'
    },
    'final_height': {
        'long': 'height',
        'short': 'h',
        'units': 'm',
        'eng': 'ft',
        'min': 0,
        'max': 8848,
        'title': 'Final Height',
        'desc': 'Final height above sea level.  "none" calculates the '
        'trajectory based on range, final time, or final velocity instead of '
        'when the projectile hits a specified altitude.'
    },
    'final_time': {
        'long': 'time',
        'short': 't',
        'units': 's',
        'method': 'direct',
        'title': 'Time of Flight',
        'desc': 'Duration of flight.'
    },
    'final_velocity': {
        'long': 'velocity',
        'short': 'f',
        'units': 'm/s',
        'eng': 'mi/h',
        'method': 'direct',
        'title': 'Final Velocity',
        'desc': 'Final velocity.'
    },
    'initial_angle': {
        'long': 'angle',
        'short': 'a',
        'units': 'deg',
        'min': 0.01,
        'max': 89.99,
        'method': 'scan',
        'step': 5,
        'title': 'Initial Angle',
        'desc': 'Initial angle from horizontal.'
    },
    'initial_height': {
        'long': 'initialheight',
        'short': 'i',
        'units': 'm',
        'eng': 'ft',
        'min': 0,
        'max': 8848,
        'title': 'Initial Height',
        'desc': 'Initial height above sea level.'
    },
    'initial_velocity': {
        'long': 'initialvelocity',
        'short': 'V',
        'units': 'm/s',
        'eng': 'mi/h',
        'min': 0.01,
        'max': 2000,
        'title': 'Initial Velocity',
        'desc': 'Initial velocity.'
    },
    'mass': {
        'long': 'mass',
        'short': 'm',
        'units': 'kg',
        'eng': 'lb',
        'min': 0.001,
        'max': 1000,
        'title': 'Mass',
        'desc': 'Mass of projectile.'
    },
    'material': {
        'long': 'material',
        'short': 'M',
        'units': 'string',
        'title': 'Material',
        'desc': 'Projectile material (see --materials for a list).  At least '
        'two of diameter, mass, and material should be specified.'
    },
    'material_density': {
        'long': 'density',
        'short': 'D',
        'units': 'kg/m/m/m',
        'eng': 'lb/in/in/in',
        'weak': True,
        'title': 'Material Density',
        'desc': 'Material density (mass per volume).'
    },
    'max_height': {
        'long': 'maxheight',
        'short': 'Y',
        'units': 'm',
        'eng': 'ft',
        'method': 'direct',
        'title': 'Maximum Height',
        'desc': 'Maximum height of trajectory above sea level.'
    },
    'power_factor': {
        'long': 'power',
        'short': 'p',
        'units': 'J/kg',
        'eng': 'ftton/lb',
        'min': 1e3,
        'max': 5e7,
        'title': 'Power per Mass',
        'desc': 'Power factor of the powder.  This is specified as '
        'enery/mass (such as J/kg, or cal/lb).'
    },
    'pressure': {
        'long': 'pressure',
        'units': 'Pa',
        'eng': 'inHg',
        'min': 0.2e5,
        'max': 1.1e5,
        'method': 'scan',
        'step': 0.01e5,
        'weak': True,
        'title': 'Atmospheric Pressure',
        'desc': 'Atmospheric pressure at sea level or at a specified altitude.'
    },
    'pressure_y0': {
        'long': 'pressurealtitude',
        'units': 'm',
        'eng': 'ft',
        'min': 0,
        'max': 8848,
        'weak': True,
        'title': 'Pressure Altitude',
        'desc': 'Altitude for the specified atmospheric pressure.'
    },
    'range': {
        'long': 'range',
        'short': 'r',
        'units': 'm',
        'eng': 'ft',
        'method': 'direct',
        'title': 'Range',
        'desc': 'Range when projectile reaches the final height or the final '
        'velocity.'
    },
    'rh': {
        'long': 'humidity',
        'short': 'H',
        'units': None,
        'min': 0,
        'max': 1,
        'method': 'scan',
        'step': 0.1,
        'weak': True,
        'title': 'Relative Humidity',
        'desc': 'Relative humidity.'
    },
    'time_delta': {
        'long': 'delta',
        'short': 'z',
        'units': 's',
        'method': None,
        'title': 'Time Step',
        'desc': 'Time step for calculations.  A small value such as 10ms is '
        'appropriate.  0.1s will be faster, but can affect accuracy.'
    },
    'T': {
        'long': 'temperature',
        'short': 'T',
        'units': 'K',
        'si': 'C',
        'eng': 'F',
        'min': '-50F',
        'max': '150F',
        'method': 'scan',
        'step': '10F',
        'weak': True,
        'title': 'Temperature',
        'desc': 'Ambient air temperature.'
    },
}


def acceleration(state, y=None, vx=None, vy=None):
    """Calculate total acceleration on a sphere.
    Enter: state: a dictionary of the current state.
           y: if not none, override the state's height in meters.
           vx: if not none, override the state's horizontal velocity in m/s
           vy: if not none, override the state's vertical velocity in m/s.
    Exit:  ax: horizontal acceleration in m/s/s.
           ay: vertical acceleration in m/s/s."""
    if y is not None:
        state['y'] = y
    if vx is not None:
        state['vx'] = vx
    if vy is not None:
        state['vy'] = vy
    (accel, ax, ay) = acceleration_from_drag(state)
    ay += acceleration_from_gravity(state)
    return (ax, ay)


def acceleration_from_drag(state):
    """Calculate the acceleration from drag in m/s/s.  The accelration due
     to drag is a function of the coefficient of drag, the atmospheric
     density, velocity, mass, and diameter.
    Enter: state: a dictionary of the current state.  See comment at the
                  top of the program.  This directly uses vx, vy, and mass,
                  and indirectly uses other parameters.
    Exit:  accel: magintude of total acceleration from drag in m/s/s.
           ax: acceleration in the x direction.
           ay: acceleration in the y direction."""
    # If we were told the pressure was zero, treat this as a vacuum with no
    # drag
    if state.get('pressure') == 0:
        return (0, 0, 0)
    density = atmospheric_density(state)
    cd = coefficient_of_drag(state, density)
    velocity_sq = state['vx']**2+state['vy']**2
    # acceleration due to drag is 1/2 * density * velocity^2 * area / mass
    area = 0.25*math.pi*state['diam']**2
    # Force of drag is 1/2*density*cd*velocity^2*area
    Fd = 0.5*cd*density*velocity_sq*area
    accel = Fd/state['mass']
    velocity = velocity_sq**0.5
    ax = -accel*state['vx']/velocity
    ay = -accel*state['vy']/velocity
    return (accel, ax, ay)


def acceleration_from_gravity(state):
    """Based on the altitude, calculate the acceleration due to gravity.
    Enter: state: a dictionary of the current state.  Only 'y' is
                  pertinent.
    Exit:  accel: acceleration from gravity in m/s/s.  This is always
                  negative."""
    y = state.get('y', 0)
    g0 = -9.80665  # at sea level
    # Mean radius of the earth from WGS-84
    re = 6371009
    # Note that we don't handle negative altitudes correctly, where the force of
    # gravity should decrease
    g = g0*(re/(re+y))**2
    return g


def atmospheric_density(state):
    """Calculate the astmospheric density in kg/(m^3).  This is based on
     temperature, pressure, and humidity.  See also Picard, A., R. S. Davis, M.
     Glaser, and K. Fujii. "Revised formula for the density of moist air
     (CIPM-2007)."  Metrologia. 45 (2008): 149-155.
    Enter: state: a dictionary of the current state.  See comment at the
                  top of the program.  This directly uses y, temp, rh,
                  pressure, and pressure_y0.
    Exit:  density: atmospheric density in kg/m/m/m."""
    if 'T' not in state:
        T = 288.15  # standard temperature at sea level
    else:
        T = state['T']
    y = state.get('y', 0)
    p_y = pressure_from_altitude(y)
    if 'pressure' in state:
        # if we are given a pressure, adjust it for our altitude.
        p_given_y0 = state['pressure']
        if 'pressure_y0' in state:
            p_y0 = pressure_from_altitude(state['pressure_y0'])
        else:
            p_y0 = pressure_from_altitude(0)
        p = p_given_y0*p_y/p_y0
    else:
        p = p_y
    # calculate the partial pressure of dry air and water vapor
    if 'rh' not in state:
        phi = 0
    else:
        phi = state['rh'] * 100.0  # relative humidity in [0-1]
    # From 'Revised formula for the density of moist air (CIPM-2007)'
    t = T-273.15  # convert to centigrade
    R = 8.314472  # J/(mol*K), universal gass constant, from CIPM-2007
    Ma = 0.02896546  # kg/mol, molar mass of dry air, from CIPM-2007
    Mv = 0.01801528  # kg/mol, molar mass of water vapor, from CIPM-2007
    # Calculate xv (from CIPM-2007)
    # psv is the vapor pressure at saturation
    A = 1.2378847e-5  # 1/(K^2)
    B = -1.9121316e-2  # 1/K
    C = 33.93711047
    D = -6.3431645e3  # K
    psv = 1*math.exp(A*T**2+B*T+C+D/T)
    # f is the enhancement factor
    alpha = 1.00062
    beta = 3.14e-8  # 1/Pa
    gamma = 5.6e-7  # 1/(K^2)
    f = alpha+beta*p+gamma*t**2
    # Now we can calculate xv, the mole fraction of water vapor
    h = phi*0.01  # convert relative humidity to the range 0-1
    xv = h*f*psv/p
    # Calculate Z, the compressibility factor (from CIPM-2007)
    a0 = 1.58123e-6  # K/Pa
    a1 = -2.9331e-8  # 1/Pa
    a2 = 1.1043e-10  # 1/(K Pa),
    b0 = 5.707e-6  # K/Pa,
    b1 = -2.051e-8  # 1/Pa,
    c0 = 1.9898e-4  # K/Pa,
    c1 = -2.376e-6  # 1/Pa,
    d = 1.83e-11  # (K/Pa)^2,
    e = -0.765e-8  # (K/Pa)^2
    Z = (1 - p/T * (a0 + a1*t + a2*t**2 + (b0+b1*t)*xv + (c0+c1*t)*xv**2) +
         p**2 / T**2*(d+e*xv**2))
    pa = p*Ma/(Z*R*T)*(1-xv*(1-Mv/Ma))
    # pressure Pa, mole fraction of water vapor, vapor pressure at saturation
    # Pa, absolute temperature K, relative humidity (0-1)
    state['density_data'] = {
        'pressure': p, 'xv': xv, 'psv': psv, 'T': T, 'h': h, 'density': pa,
        'y': y}
    return pa


def atmospheric_viscosity(state):
    """Calculate the astmospheric dynamic viscosity in kg/(m*s). This is
     based on temperature and humidity.  I've used a relatively simple
     equation to combine the viscosities of dry air and water vapor, as
     listed in Melling, Adrian, Stefan Noppenberger, Martin Still, and
     Holger Venzke.  "Interpolation Correlations for Fluid Properties of
     Humid Air in the Temperature Range 100 degC to 200 degC."  Journal of
     Physical and Chemical Reference Data.  26, no. 4 (1997): 1111-1123.
    Enter: state: a dictionary of the current state.  See comment at the
                  top of the program.
    Exit:  viscosity: atmospheric viscosity in kg/m/s."""
    if 'density_data' not in state:
        # This populates density_data with a variety of values we need,
        # including the pressure and the mole fraction of water vapor
        atmospheric_density(state)
    T = state['density_data']['T']
    density = state['density_data']['density']
    mua = viscosity_dry_air(T, density)
    if not state['density_data']['h']:
        state['viscosity_data'] = {'mua': mua, 'viscosity': mua}
        return mua
    muv = viscosity_water_vapor(T, density)
    Ma = 0.02896546  # kg/mol, molar mass of dry air, from CIPM-2007
    Mv = 0.01801528  # kg/mol, molar mass of water vapor, from CIPM-2007
    p = state['density_data']['pressure']
    pv = state['density_data']['psv']*state['density_data']['h']
    mu = (mua*(p-pv)*Ma**0.5+muv*pv*Mv**0.5)/((p-pv)*Ma**0.5+pv*Mv**0.5)
    state['viscosity_data'] = {'mua': mua, 'muv': muv, 'viscosity': mu}
    return mu


def coefficient_of_drag(state=None, density=None,  # noqa - mccabe
                        reynolds=None, mach=None, only_in_range=False):
    """Calculate the coefficient of drag.  This is based off of the
     Reynolds number, Mach number, and possibly other factors.
    Enter: state: a dictionary of the current state.  See comment at the
                  top of the program.  This directly uses vx, vy, and diam,
                  and indirectly uses other parameters.  If None, use the
                  specified Reynolds and Mach numbers.
             density: the atmospheric density.  If not specified and state is,
                      this is calculated.
             reynolds: if state is None, use this as the reynolds number.
             mach: if state is None, use this as the mach number.
             only_in_range: if True, return None if the values are outside of
                            what we can interpolate.
    Exit:  cd: the coefficient of drag."""
    if state:
        if density is None:
            density = atmospheric_density(state)
        viscosity = atmospheric_viscosity(state)
        velocity = (state['vx']**2+state['vy']**2)**0.5
        Re = density*velocity*state['diam']/viscosity
        sos = speed_of_sound(state)
        Mn = velocity/sos
        state['drag_data'] = {'Re': Re, 'sos': sos, 'Mn': Mn}
    else:
        Re = reynolds
        if mach is not None:
            Mn = mach
        else:
            Mn = 0
        state['drag_data'] = {'Re': Re, 'Mn': Mn}
    # Estimate the critical point based on Mach number
    crit_data = [(machnum, math.log10(crit))
                 for (machnum, reynolds_data, crit) in MnReCdDataTable]
    (critical_Re, in_range) = interpolate(Mn, crit_data, method='linear')
    critical_Re = 10**critical_Re
    state['drag_data']['critical_Re'] = critical_Re
    # Interpolate for the Reynolds number for each Mach number where we have
    # data.
    mach_data_oor = []
    mach_data = []
    for pos in xrange(len(MnReCdDataTable)):
        (mach, reynolds_data, crit) = MnReCdDataTable[pos]
        use = False
        if Mn <= 0.3 and mach <= 0.3:
            use = True
        if (pos+1 != len(MnReCdDataTable) and Mn >= mach and
                Mn <= MnReCdDataTable[pos+1][0]):
            use = True
        if pos and Mn >= MnReCdDataTable[pos-1][0] and Mn <= mach:
            use = True
        if pos+1 == len(MnReCdDataTable) and Mn >= mach:
            use = True
        if not use:
            continue
        # We functionally shift the point we are interpolating so that the
        # critical point looks sane and smooth on a graph
        adjusted_re = 10**(math.log10(Re) - math.log10(critical_Re) +
                           math.log10(crit))
        (cd, in_range) = interpolate(adjusted_re, reynolds_data, True)
        if in_range:
            mach_data.append((mach, cd))
        else:
            mach_data_oor.append((mach, cd))
    if (Mn > 0.3 and len(mach_data) < 2) or not len(mach_data):
        if only_in_range:
            return None
        if Verbose >= 3:
            warning(state, 'cod_outside',
                    'Warning: coefficient of drag for Re=%6.4g, Mn=%6.4f '
                    'outside of available data.\n' % (Re, Mn))
    if not len(mach_data):
        mach_data = mach_data_oor
        (cd, in_range) = interpolate(Mn, mach_data, method='linear')
        in_range = False
    else:
        (cd, in_range) = interpolate(Mn, mach_data, method='linear')
    state['drag_data']['cd'] = cd
    state['drag_data']['in_range'] = in_range
    if not in_range:
        if only_in_range:
            return None
        if Verbose >= 3:
            warning(state, 'cod_extrapolated',
                    'Warning: coefficient of drag for Re=%6.4g, Mn=%6.4f '
                    'extrapolated.\n' % (Re, Mn))
    return cd


def csv_row(data):
    """Convert a list to a single line of CSV.
    Enter: data: a list to convert.
    Exit:  output: a single string without any linefeeds or carriage
                   returns."""
    global csv, StringIO
    if csv is None:
        import csv
    if StringIO is None:
        import StringIO
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerow(data)
    return si.getvalue().strip('\r\n')


def cubic_roots(a, b, c, d):
    """Compute the roots of a cubic equation.  Only real roots are
     returned.  This works properly with lesser degree equations if the
     higher order coefficients are set to zero.
    Enter: a, b, c, d: coefficients of the cubic equation.  These are of
                       the form a*x^3+b*x^2+c*x+d=0.
    Exit:  roots: a list of zero to three real roots."""
    if a == 0:
        if b != 0:
            val = abs(c*c-4*b*d)**0.5/(2*b)
            return [-c+val, -c-val]
        if c != 0:
            return [-d/c]
        return []
    b /= -a
    c /= -a
    d /= -a
    n = b*b+3*c
    o = -(2*b*b*b+9*b*c+27*d)
    if n < 0:
        n = abs(n)
        sc = 0.5*o*n**-1.5
        t = 2*n**0.5/3
        if sc > 0:
            sign = 1
        elif sc < 0:
            sign = -1
        else:
            sign = 0
        s = math.log(abs(sc)+(sc*sc+1)**0.5)*sign/3
        return [b/3-t*0.5*(math.exp(s)-math.exp(-s))]
    elif n > 0:
        sc = 0.5*o*n**-1.5
        t = 2*n**0.5/3
        if sc < -1 or sc > 1:
            s = math.log(abs(sc)+(sc*sc-1)**0.5)/3
            return [t*0.5*(math.exp(s)+math.exp(-s))+b/3]
        else:
            s = math.asin(sc)/3
            return [t*math.sin(s-2*math.pi/3)+b/3,
                    t*math.sin(s)+b/3,
                    t*math.sin(s+2*math.pi/3)+b/3]
    else:
        return []


LastDisplayStatus = 0
DisplayStatusInterval = 1


def display_status(state, params={}, last=False):
    """Depending on the verbosity, display a line indicating the current
     status of the trajectory.
    Enter: state: a dictionary of the current state.  See comment at the
                  top of the program.
           params: parameters to override the current state.
           last: True if this is the last point."""
    global LastDisplayStatus
    if Verbose < 2:
        return
    time = params.get('time', state.get('time', 0))
    if (time and not last and
            time-LastDisplayStatus < DisplayStatusInterval and
            time > LastDisplayStatus):
        return
    LastDisplayStatus += DisplayStatusInterval
    if time < LastDisplayStatus:
        LastDisplayStatus = time
    if not time:
        print 'Time,x,y,vx,vy,ax,ay,cd,Re,Mn'
    if params and len(params):
        state = state.copy()
        for key in params:
            state[key] = params[key]
    drag = state.get('drag_data', {})
    print '%5.3f %3.1f,%3.1f %3.1f,%3.1f %3.1f,%3.1f %5.3f %1.0f %4.2f' % (
        time, state.get('x', 0), state.get('y', 0), state.get('vx', 0),
        state.get('vy', 0), state.get('ax', 0), state.get('ay', 0),
        drag.get('cd', 0), drag.get('Re', 0), drag.get('Mn', 0))


def find_unknown(initial_state, unknown, unknown_scan=None):  # noqa - mccabe
    """Based on an initial state and a specific unknown, try different
     values for the unknown until the computed trajectory matches to an
     acceptable level.
    Enter: initial_state: a dictionary of the initial state.  See comment
                          at the top of the program.
           unknown: name of the unknown value which will be varied.
           unknown_scan: if specified, override the factor's normal method and
                         use a scan with this step instead.
    Exit:  final_state: the final state of the projectile.  This includes
                        an 'error' item if there is insufficient data for
                        calculation.
           points: a list of points along the trajectory."""
    if unknown not in Factors:
        print 'Cannot solve for %s.' % unknown
        return (initial_state, [])
    if Factors[unknown].get('method', 'binary') is None:
        print 'Cannot solve for %s.' % unknown
        return (initial_state, [])
    if Factors[unknown].get('weak', False):
        if Verbose >= 1:
            print ('Trying to solve for %s is ill-conditioned; it may not ' +
                   'work.') % unknown
    direct_state = find_unknown_direct(unknown, initial_state)
    if direct_state:
        return direct_state, []
    method = Factors[unknown].get('method', 'binary')
    if unknown_scan:
        method = 'scan'
    if method == 'direct':
        (state, points) = trajectory(initial_state)
        return state, points
    minval = convert_units(Factors[unknown]['min'])
    maxval = convert_units(Factors[unknown]['max'])
    lastval = None
    if method == 'scan':
        step = convert_units(Factors[unknown].get('step')
                             if not unknown_scan else unknown_scan)
        lasterror = None
        val = minval
        while val < maxval + step:
            if val > maxval:
                val = maxval
            error = trajectory_error(initial_state, unknown, val)
            if Verbose >= 3:
                print 'Step %s: %g,%g' % (unknown, val, error)
            if error is None:
                return initial_state, []
            if lasterror and error and error*lasterror <= 0:
                minval = lastval
                maxval = val
                break
            lasterror = error
            lastval = val
            val += step
    minerror = trajectory_error(initial_state, unknown, minval)
    if Verbose >= 3:
        print '%s: %g,%g' % (unknown, minval, minerror)
    maxerror = trajectory_error(initial_state, unknown, maxval)
    x2 = y2 = None
    if Verbose >= 3:
        print '%s: %g,%g %g,%g' % (unknown, minval, minerror, maxval, maxerror)
    if minerror is None or maxerror is None:
        return initial_state, []
    if minerror*maxerror > 0:
        print 'Cannot solve for %s; conditions are too weak.' % unknown
        return initial_state, []
    if not minerror:
        foundval = minval
    elif not maxerror:
        foundval = maxval
    else:
        threshold = 10**(-PrecisionInDigits)
        while True:
            # value halfway between last two tests
            intval = midval = (minval+maxval)*0.5
            # If we have three points, use an inverse quadradic interpolation,
            # but only if it is between the last two points.
            if x2 is not None:
                x0, y0, x1, y1 = minval, minerror, maxval, maxerror
                intval = (x0 * y2*y1 / (y0-y2) / (y0-y1) +
                          x1 * y0*y2 / (y1-y0) / (y1-y2) +
                          x2 * y1*y0 / (y2-y1) / (y2-y0))
                # if it isn't between the last two points we should have picked
                # the otehr root.  Rather, just use the mid point.
                if ((minval > maxval and (
                        intval > minval or intval < maxval)) or (
                        minval < maxval and (
                        intval < minval or intval > maxval))):
                    intval = midval
            # weight them; this helps prevent only updating one side
            # repeatedly
            intval = (intval*99+midval)/100
            if maxval-minval < intval*threshold:
                foundval = intval
                break

            interror = trajectory_error(initial_state, unknown, intval)
            if not interror:
                foundval = intval
                if Verbose >= 3:
                    print '%s: %g,%g %g,%g %g,%g %3.1f' % (
                        unknown, minval, minerror, maxval, maxerror, intval,
                        interror, math.log10(intval/(maxval-minval)))
                break
            if interror*minerror > 0:
                minerror, y2 = interror, minerror
                minval, x2 = intval, minval
            else:
                maxerror, y2 = interror, maxerror
                maxval, x2 = intval, maxval
            if Verbose >= 3:
                print '%s: %g,%g %g,%g %g,%g %3.1f' % (
                    unknown, minval, minerror, maxval, maxerror, intval,
                    interror, math.log10(intval/(maxval-minval)))
    state = initial_state.copy()
    state[unknown] = foundval
    (state, points) = trajectory(state)
    return state, points


def find_unknown_direct(unknown, state):
    """Check if the unknown was given or can be solved directly.
    Enter: unknown: the unknown to solve for.
           state; the initial state.
    Exit:  solved_state: the answer state if solved, None if not.
    """
    if state.get(unknown):
        return state
    state = state.copy()
    state = determine_material(state, Verbose)
    # This could be extended to directly solve for any direct solution
    if (unknown == 'power_factor' and state.get('initial_velocity') and
            state.get('charge') and state.get('mass')):
        state[unknown] = ((state['initial_velocity']**2) * state['mass'] /
                          (2 * state['charge']))
        return state
    return None


def generate_output(state, user_params=None, comment=None):  # noqa - mccabe
    """Generate output for part of a csv or html5 table.  The parameters
     can be any internal, short, or long name of a factor to include it in
     the list.  ':'(unit) may be added to the name of any factor to output
     the factor in the specified units rather than the default units.
     'comment', 'comptime', 'method', and 'version' are treated as factors
     for this purpose.  Additionally, 'diff:(factor):(value)' lists the
     difference between the specified value and the specified factor.  If
     no factors are included in the parameter list, a default set is used.
     Additionally, the following are allowed as key=value:
       format: 'csv' (default), 'html', or 'wp'.
       header: 'none' (default), 'title', 'units', or 'all'.  All generates
     two lines, the first with the title and the second with the units.
       footer: same options as header.
       units: 'eng', 'si', or 'both' (default).  In both, two columns
     appear for each item.
       blank: the number of blank lines to insert after any header and
     before the data.
    Enter: state: the final state of the calculations that are used for
                  output.  If None, only generate headers and footers.
           user_params: a comma-separated list of parameters as above.
           comment: a comment that can be included in the output."""
    params = {'format': 'csv', 'header': 'none', 'footer': 'none',
              'units': 'both', 'blank': 0}
    params, other_params, items = parse_user_params(params, user_params)
    if not len(items):
        items = 'V,a,d,m,c,t,f,r,p,version,comment'.split(',')
    format = params.get('format', '')
    if format not in ('html', 'wp'):
        format = 'csv'
    header = params.get('header', '')
    if header not in ('title', 'units', 'all', 'titleunits'):
        header = 'none'
    footer = params.get('footer', '')
    if footer not in ('title', 'units', 'all', 'titleunits'):
        footer = 'none'
    units = params.get('units', '')
    if units not in ('eng', 'si'):
        units = 'both'
    factors = []
    for itemunit in items:
        parts = itemunit.split(':', 1)
        item = parts[0]
        if item in ('comment', 'comptime', 'method', 'version'):
            factors.append((item, None))
            continue
        diff = False
        if item in ('diff', 'adiff'):
            subparts = parts[1].split(':', 1)
            if len(subparts) != 2:
                continue
            difftype = item
            item = subparts[0]
            diff = subparts[1]
        for key in Factors:
            if (item in (key,
                         Factors[key].get('long', ''),
                         Factors[key].get('short', ''))):
                if len(parts) == 1:
                    lastuunits = None
                    for u in ('eng', 'si'):
                        if units in (u, 'both'):
                            uunits = Factors[key].get(u, Factors[key].get(
                                'units', None))
                            if (units == 'both' and u == 'si' and
                                    lastuunits == uunits):
                                continue
                            factors.append((key, uunits))
                            lastuunits = uunits
                elif diff:
                    factors.append((key, ('diff', convert_units(
                        diff, Factors[key].get('units', None)), difftype)))
                else:
                    factors.append((key, parts[1]))
                break
    if not state:
        state = {}
    data = []  # each item is a tuple of (title, units, value)
    for key, funit in factors:
        if key == 'comment':
            data.append(('Comment', None, comment))
            continue
        elif key == 'comptime':
            data.append(('Computation Time', 's', state.get(
                'computation_time', None)))
            continue
        elif key == 'method':
            data.append(('Numerical Method', None,
                         'Runge-Kutta' if UseRungeKutta else 'Simple'))
            continue
        elif key == 'version':
            data.append(('Program Version', None, __version__))
            continue
        title = Factors[key]['title']
        if key in state:
            value = state[key]
        elif key == 'final_velocity':
            value = (state.get('vx', 0)**2+state.get('vy', 0)**2)**0.5
        elif key == 'final_time':
            value = state.get('time', None)
        elif key == 'range':
            value = state.get('range', state.get('x', 0))
        else:
            value = None
        uval = value
        if isinstance(funit, tuple) and funit[0] == 'diff':
            if value is not None:
                uval = (value-funit[1])/funit[1]
            else:
                uval = None
            title = 'Relative Difference in %s' % title
            if format in ('html') and funit[2] == 'adiff':
                title += '\n'
            funit = None
        else:
            if funit and value is not None:
                uval = convert_units(value, funit)
        data.append((title, funit, uval))
    lines = []
    if header != 'none':
        lines.append(('headstart', []))
        if header in ('title', 'all'):
            lines.append(('head', ['' if ditem[0] is None else ditem[0]
                                   for ditem in data]))
        if header in ('units', 'all'):
            lines.append(('head', ['' if ditem[1] is None else ditem[1]
                                   for ditem in data]))
        if header in ('titleunits'):
            line = []
            for item in data:
                title = ''
                if item[0] is not None:
                    title = item[0]
                if item[1] is not None:
                    if title:
                        if format in ('html'):
                            title += '\n'
                        else:
                            title += ' '
                    title += '(%s)' % item[1]
                line.append(title)
            lines.append(('head', line))
        lines.append(('headend', []))
    for line in xrange(params['blank']):
        lines.append(('blank', ['' for item in data]))
    if state != {}:
        line = []
        for item in data:
            if item[2] is None:
                line.append('')
            elif type(item[2]) in (types.IntType, types.FloatType):
                line.append(('%8g' % item[2]).strip())
            else:
                line.append(str(item[2]))
        lines.append(('data', line))
    if footer != 'none':
        lines.append(('footstart', []))
        if footer in ('units', 'all'):
            lines.append(('foot', ['' if item[1] is None else item[1]
                                   for item in data]))
        if footer in ('title', 'all'):
            lines.append(('foot', ['' if item[0] is None else item[0]
                                   for item in data]))
        if footer in ('titleunits'):
            line = []
            for item in data:
                title = ''
                if item[0] is not None:
                    title = item[0]
                if item[1] is not None:
                    if title:
                        title += ' '
                    title += '(%s)' % item[1]
                line.append(title)
            lines.append(('foot', line))
        lines.append(('footend', []))
    for ltype, line in lines:
        if format == 'html':
            if ltype == 'headstart':
                print '<table class=\'results_table sortable\'><thead>'
            elif ltype == 'headend':
                print '</thead><tbody>'
            elif ltype == 'footstart':
                print '</tbody><tfoot>'
            elif ltype == 'footend':
                print '</tfoot></table>'
            else:
                tag = ltype in ('head', 'foot') and 'th' or 'td'
                out = ['<tr>']
                for item in line:
                    cls = ''
                    if '\n' in item and ltype == 'head':
                        if item.endswith('\n'):
                            cls = ' class=\'sorttable_absnumeric\''
                        else:
                            cls = ' class=\'sorttable_numeric\''
                    out.append('<%s%s>%s</%s>' % (
                        tag, cls, html_encode(item.strip()).replace(
                            '\n', '<BR/>'), tag))
                out.append('</tr>')
                print ''.join(out)
        elif format == 'wp':
            if ltype == 'headstart':
                print '[table class=\'results_table sortable\'][thead]'
            elif ltype == 'headend':
                print '[tbody]'
            elif ltype == 'footstart':
                print '[tfoot]'
            elif ltype == 'footend':
                print '[tableend]'
            else:
                tag = ltype in ('head', 'foot') and 'th' or 'td'
                print '[tr][%s]' % tag + ('[%s]' % tag).join([
                    html_encode(item) for item in line])
        else:  # csv
            if ltype in ('headstart', 'headend', 'footstart', 'footend'):
                continue
            print csv_row(line)


def get_cpu_time():
    """Return a time that should increase with cpu time.
    Exit:  time: the current time or a cpu-relative time."""
    if not GET_CPU_TIME:
        return time.time()
    global psutil
    if psutil is None:
        import psutil
    cpu_times = psutil.cpu_times()
    return cpu_times.user + cpu_times.system


def graph_coefficient_of_drag(user_params=None):
    """Generate a plot of the values we use for coefficient of drag.  The
     parameters are w (width in pixels), h (height in pixels), file (output
     file name), remin, remax (minimum and maximum Reynolds numbers to
     plot), mnmin, mnmax (min and max Mach numbers to plot), mnint (Mach
     number interval to plot).
    Enter: user_params: a comma separated list of parameters."""
    params = {'remin': 1.0e2, 'remax': 1.0e7, 'mnmin': 0.0, 'mnmax': 1.8,
              'mnint': 0.2}
    params, other_params, items = parse_user_params(params, user_params)
    global matplotlib, pyplot
    if not matplotlib:
        try:
            import matplotlib
            import matplotlib.pyplot as plt
        except Exception:
            sys.stderr.write('Cannot import matplotlib, cannot make a graph.\n')
            return
    remin = round(math.log10(params['remin'])-0.0499, 1)
    remax = round(math.log10(params['remax'])+0.05, 1)
    reint = 1.
    if remax-remin < 3:
        reint = 0.2
    if remax-remin < 10:
        reint = 0.5
    mnmin = params['mnmin']
    mnmax = params['mnmax']
    mnint = params['mnint']
    substep = 100
    for mni in xrange(int((mnmax-mnmin)/mnint)+1):
        mn = mni*mnint+mnmin
        datax = []
        datay = []
        for rei in xrange(int((remax-remin)/(reint/substep))+1):
            re = rei*reint/substep+remin
            cd = coefficient_of_drag(reynolds=10**re, mach=mn,
                                     only_in_range=True)
            if cd is not None:
                datax.append(re)
                datay.append(cd)
        plt.plot(datax, datay)
    for (mn, data, crit) in MnReCdDataTable:
        points = [val for val in data if val[0] >= 10**remin and
                  val[0] <= 10**remax]
        datax = [math.log10(val[0]) for val in points]
        datay = [val[1] for val in points]
        plt.plot(datax, datay, '--', label='%3.1f' % mn)
    plt.ylim(0, 1)
    plt.show()


def graph_trajectory(points, user_params=None):
    """Generate a plot of points from a trajectory.
    Enter: points: a list of points from a trajectory.  Each has x, y, vx,
           vy, ax, ay, and time.
           user_params: a comma separated list of parameters."""
    params = {}
    params, other_params, items = parse_user_params(params, user_params)
    global matplotlib, pyplot
    if not matplotlib:
        try:
            import matplotlib
            import matplotlib.pyplot as plt
        except Exception:
            sys.stderr.write('Cannot import matplotlib, cannot make a graph.\n')
            return
    datax = [point['x'] for point in points]
    datay = [point['y'] for point in points]
    plt.plot(datax, datay, '-')
    plt.axes().set_aspect('equal')
    plt.show()


def html_encode(text):
    """Encode <, >, ', and & to html entities.  This is intended to do what
     the php function htmlspecialchars does.
    Enter: text: text to encode.
    Exit:  encoded_text: encoded text."""
    return text.replace('&', '&amp;').replace('\'', '&quot;').replace(
        '<', '&lt;').replace('>', '&gt;')


def interpolate(xi, data, logx=False, method='tension'):  # noqa -mccabe
    """Interpolate a value from a set of points.  The points are a list of
     two-tuples of the form (x, y).  If there is only one point in the
     list, the sole y value is returned.  For two points, a linear
     interpolation or extrapolation is used.  For three points, a quadratic
     interpolation is used.  For more than three, a cubic interpolation of
     the closest four points is used.
       There are several methods for interpolation.  They are:
       'natural': perform a natural cubic spline interpolation
       'binatural': perform a natural cubic spline interpolation where the
     splines are separate for x and y.  This should be funcitonally
     identical to 'natural'.
       'cubic': perform a cubic interpolation.  This will be discontinuous
     when there are more than four points.
       'parabolic': perform a piecewise averaged parabolic interpolation.
       'hermitic': perform a hermitic spline interpolation.
       'tension': perform a tensioned hermitic spline interpolation.
       'quadratic': perform a parabolic interpolation.  This will be
     discontinuous where then are more than three points.
       'linear': perform a linear interpolation.
    Enter: xi: x value to interpolate from.
           data: a list of (x, y) pairs that are used for the
                 interpolation.
           logx: if True, perform the interpolations on the log values of
                 the x data.
           method: the method used for the interpolation.  Choices are
                   listed above.
    Exit:  yi: the interpolated y value.  0 if the data list is empty.
           in_range: True if x is interpolated, False if it is
                     extrapolated."""
    if method == 'natural':
        ncdata = natural_cubic_prep(data, logx, simple=True)
        return natural_cubic(xi, ncdata)
    elif method == 'binatural':
        nbcdata = natural_bicubic_prep(data, logx, simple=True)
        return natural_bicubic(xi, nbcdata)
    if logx:
        xi = math.log10(xi)
    # Make sure our data has distinct x values in ascending order
    ddict = {}
    for (x, y) in data:
        if logx:
            ddict[math.log10(x)] = y
        else:
            ddict[x] = y
    xy = [(key, ddict[key]) for key in ddict]
    xy.sort()
    pos = 0
    for pos in xrange(len(xy)):
        if xi == xy[pos][0]:
            return (xy[pos][1], True)
        if xi < xy[pos][0]:
            break
    minpos = max(0, pos-2)
    maxpos = min(pos+2, len(xy))
    if method == 'linear':
        minpos = max(0, pos-1)
        maxpos = min(pos+1, len(xy))
    elif method == 'quadratic':
        if pos >= 1 and abs(xi-xy[pos-1][0]) < abs(xi-xy[pos][0]):
            maxpos = min(pos+1, len(xy))
        else:
            minpos = max(0, pos-1)
    xy = xy[minpos:maxpos]
    x = [item[0] for item in xy]
    y = [item[1] for item in xy]
    num_points = len(x)
    if not num_points:
        yi = 0
        in_range = False
    elif num_points == 1:
        yi = y[0]
        in_range = (xi == x[0])
    elif num_points == 2:
        # linear interpolation
        yi = (y[1]-y[0])*(xi-x[0])/(x[1]-x[0])+y[0]
        in_range = (xi >= x[0] and xi <= x[1])
    elif num_points == 3:
        # parabolic interpolation
        den = x[0]**2*(x[1]-x[2])+x[1]**2*(x[2]-x[0])+x[2]**2*(x[0]-x[1])
        A = (x[0]*(y[2]-y[1])+x[1]*(y[0]-y[2])+x[2]*(y[1]-y[0]))/den
        B = (A*(x[0]**2-x[1]**2)+(y[1]-y[0]))/(x[1]-x[0])
        C = y[0]-(A*x[0]**2+B*x[0])
        yi = A*xi**2+B*xi+C
        in_range = (xi >= x[0] and xi <= x[2])
    else:
        # For the cubic case, I used a symbolic algebra program; it could be
        # made more efficient
        if method == 'cubic':  # a cubic interpolation
            den = (
                x[0]*(x[1]**2*(x[3]**3-x[2]**3)-x[2]**2*x[3]**3 +
                      x[2]**3*x[3]**2+x[1]**3*(x[2]**2-x[3]**2)) +
                x[1]*(x[2]**2*x[3]**3-x[2]**3*x[3]**2)+x[0]**2*(
                    x[2]*x[3]**3+x[1]*(x[2]**3-x[3]**3)+x[1]**3*(x[3]-x[2]) -
                    x[2]**3*x[3])+x[1]**2*(x[2]**3*x[3]-x[2]*x[3]**3) +
                x[0]**3*(x[1]*(x[3]**2-x[2]**2)-x[2]*x[3]**2 +
                         x[2]**2*x[3]+x[1]**2*(x[2]-x[3])) +
                x[1]**3*(x[2]*x[3]**2-x[2]**2*x[3]))
            A = ((x[0]*(x[1]**2*(y[3]-y[2])-x[2]**2*y[3]+x[3]**2*y[2]+(x[2]**2-x[3]**2)*y[1])+x[1]*(x[2]**2*y[3]-x[3]**2*y[2])+x[0]**2*(x[2]*y[3]+x[1]*(y[2]-y[3])-x[3]*y[2]+(x[3]-x[2])*y[1])+x[1]**2*(x[3]*y[2]-x[2]*y[3])+(x[2]*x[3]**2-x[2]**2*x[3])*y[1]+(x[1]*(x[3]**2-x[2]**2)-x[2]*x[3]**2+x[2]**2*x[3]+x[1]**2*(x[2]-x[3]))*y[0])/den)  # noqa
            B = -((x[0]*(x[2]**3-x[1]**3)-x[1]*x[2]**3+x[1]**3*x[2]+x[0]**3*(x[1]-x[2]))*A+x[1]*y[2]+x[0]*(y[1]-y[2])-x[2]*y[1]+(x[2]-x[1])*y[0])/(x[0]*(x[2]**2-x[1]**2)-x[1]*x[2]**2+x[1]**2*x[2]+x[0]**2*(x[1]-x[2]))  # noqa
            C = -((x[0]**2-x[1]**2)*B+(x[0]**3-x[1]**3)*A+y[1]-y[0])/(x[0]-x[1])
            D = -x[0]*C-x[0]**2*B-x[0]**3*A+y[0]
            yi = A*xi**3+B*xi**2+C*xi+D
        elif method == 'parabolic':  # piecewise parabolic interpolation
            den = x[0]**2*(x[1]-x[2])+x[1]**2*(x[2]-x[0])+x[2]**2*(x[0]-x[1])
            A = (x[0]*(y[2]-y[1])+x[1]*(y[0]-y[2])+x[2]*(y[1]-y[0]))/den
            B = (A*(x[0]**2-x[1]**2)+(y[1]-y[0]))/(x[1]-x[0])
            C = y[0]-(A*x[0]**2+B*x[0])
            yi0 = A*xi**2+B*xi+C
            den = x[1]**2*(x[2]-x[3])+x[2]**2*(x[3]-x[1])+x[3]**2*(x[1]-x[2])
            A = (x[1]*(y[3]-y[2])+x[2]*(y[1]-y[3])+x[3]*(y[2]-y[1]))/den
            B = (A*(x[1]**2-x[2]**2)+(y[2]-y[1]))/(x[2]-x[1])
            C = y[1]-(A*x[1]**2+B*x[1])
            yi1 = A*xi**2+B*xi+C
            yi = (yi0+yi1)*0.5
        else:  # Hermite or tensioned-hermitic cubic interpolation
            if method == 'tension':
                tension = 0.5
            else:
                tension = 0
            m1 = (1-tension)*(y[2]-y[0])/(x[2]-x[0])
            m2 = (1-tension)*(y[3]-y[1])/(x[3]-x[1])
            h = x[2]-x[1]
            d = (y[2]-y[1])/h
            c0 = y[1]
            c1 = m1
            c2 = (-2*m1+3*d-m2)/h
            c3 = (m1-2*d+m2)/h/h
            c2 -= x[1]*c3
            c1 -= x[1]*c2
            c0 -= x[1]*c1
            c2 -= x[1]*c3
            c1 -= x[1]*c2
            c2 -= x[1]*c3
            yi = c3*xi**3+c2*xi**2+c1*xi+c0
        in_range = (xi >= x[0] and xi <= x[3])
    return (yi, in_range)


def natural_bicubic(xi, data):
    """Interpolate a value from a set of points.  The points must have been
     prepared with natural_bicubic_prep.
    Enter: xi: x value to interpolate from.
           data: the tuple of (x, y, Dx, Dy, logx) as returned from
                 natural_bicubic_prep.
    Exit:  yi: the interpolated y value.  0 if the data list is empty.
           in_range: True if x is interpolated, False if it is
                     extrapolated."""
    (x, y, Dx, Dy, logx) = data
    if not len(x):
        return (0, False)
    if len(x) == 1:
        return (y[0], x[0] == xi)
    if logx:
        xi = math.log10(xi)
    in_range = (xi >= x[0] and xi <= x[-1])
    pos = 0
    while x[pos+1] < xi:
        pos += 1
        if pos+2 == len(x):
            break
    # We know that we need to interpolate between pos and pos+1, but the exact
    # position is not directly known, as we have both x and y as a function of t
    d = x[pos]
    c = Dx[pos]
    b = 3*(x[pos+1]-x[pos])-2*Dx[pos]-Dx[pos+1]
    a = 2*(x[pos]-x[pos+1])+Dx[pos]+Dx[pos+1]
    troots = cubic_roots(a, b, c, d-xi)
    if not len(troots):  # fall back to interpolation
        t = (xi-x[pos])/(x[pos+1]-x[pos])
    elif len(troots) == 1:
        t = troots[0]
    else:
        if in_range:
            tlist = [(abs(0.5-t), t) for t in troots]
        elif pos == 0:
            tlist = [(abs(-t), t) for t in troots]
        else:
            tlist = [(abs(t-1), t) for t in troots]
        tlist.sort()
        t = tlist[0][1]
    d = y[pos]
    c = Dy[pos]
    b = 3*(y[pos+1]-y[pos])-2*Dy[pos]-Dy[pos+1]
    a = 2*(y[pos]-y[pos+1])+Dy[pos]+Dy[pos+1]
    yi = a*t**3+b*t**2+c*t+d
    return (yi, in_range)


def natural_bicubic_prep(data, logx=False):
    """Prepare the derivatives needs to each point so that we can use a
     natural cubic function for interpolation.
    Enter: data: a list of two-tuples ((x, y) pairs).
           logx: if True, perform the interpolations on the log values of
                 the x data.
    Exit:  x: a list of the x values used for the interpolation.
           y: a list of the y values used for the interpolation.
           Dx: a list of derivatives for the x values.
           Dy: a list of derivatives for the y values.
           logx: the value specified for input."""
    ddict = {}
    for (x, y) in data:
        if logx:
            ddict[math.log10(x)] = y
        else:
            ddict[x] = y
    xy = [(key, ddict[key]) for key in ddict]
    xy.sort()
    x = [float(item[0]) for item in xy]
    y = [float(item[1]) for item in xy]
    w = len(x)+1
    h = len(x)
    n = len(x)-1
    if h < 2:
        return (x, y, [0]*len(x), [0]*len(x), logx)
    for axis in ('x', 'y'):
        if axis == 'x':
            p = x
        else:
            p = y
        a = [0]*w*h
        a[0  ] = 2  # noqa
        a[1  ] = 1  # noqa
        a[n+1] = 3*(p[1]-p[0])
        for i in xrange(1, n, 1):
            a[i*w+i-1] = 1
            a[i*w+i  ] = 4  # noqa
            a[i*w+i+1] = 1
            a[i*w+n+1] = 3*(p[i+1]-p[i-1])
        a[n*w+n-1] = 1
        a[n*w+n  ] = 2  # noqa
        a[n*w+n+1] = 3*(p[n]-p[n-1])
        result = rowreduce(w, h, a)
        D = [result[2][j*w+w-1] for j in xrange(h)]
        if axis == 'x':
            Dx = D
        else:
            Dy = D
    return (x, y, Dx, Dy, logx)


def natural_cubic(xi, data):
    """Interpolate a value from a set of points.  The points must have been
     prepared with natural_cubic_prep.
    Enter: xi: x value to interpolate from.
           data: the tuple of (x, y, D, logx) as returned from
                 natural_cubic_prep.
    Exit:  yi: the interpolated y value.  0 if the data list is empty.
           in_range: True if x is interpolated, False if it is
                     extrapolated."""
    (x, y, D, logx) = data
    if not len(x):
        return (0, False)
    if len(x) == 1:
        return (y[0], x[0] == xi)
    if logx:
        xi = math.log10(xi)
    in_range = (xi >= x[0] and xi <= x[-1])
    pos = 1
    while x[pos] < xi:
        pos += 1
        if pos+1 == len(x):
            break
    t = (xi-x[pos-1])/(x[pos]-x[pos-1])
    a = D[pos-1]*(x[pos]-x[pos-1])-(y[pos]-y[pos-1])
    b = -D[pos]*(x[pos]-x[pos-1])+(y[pos]-y[pos-1])
    yi = (1-t)*y[pos-1]+t*y[pos]+t*(1-t)*(a*(1-t)+b*t)
    return (yi, in_range)


def natural_cubic_prep(data, logx=False, simple=False):
    """Prepare the derivatives needs to each point so that we can use a
     natural cubic function for interpolation.
    Enter: data: a list of two-tuples ((x, y) pairs).
           logx: if True, perform the interpolations on the log values of
                 the x data.
           simple: if True, don't actually use a natural cubic; rather, use
                   a simple weighted calculation for the derivatives.
    Exit:  x: a list of the x values used for the interpolation.
             y: a list of the y values used for the interpolation.
             D: a list of derivatives for each point.
             logx: the value specified for input."""
    ddict = {}
    for (x, y) in data:
        if logx:
            ddict[math.log10(x)] = y
        else:
            ddict[x] = y
    xy = [(key, ddict[key]) for key in ddict]
    xy.sort()
    x = [float(item[0]) for item in xy]
    y = [float(item[1]) for item in xy]
    w = len(x)+1
    h = len(x)
    n = len(x)-1
    if h < 2:
        return (x, y, [0]*len(x), logx)
    if simple:
        D = [0]*(n+1)
        D[0] = (y[1]-y[0])/(x[1]-x[0])
        for i in xrange(1, n, 1):
            D[i] = ((y[i]-y[i-1])/(x[i]-x[i-1])+(y[i+1]-y[i])/(x[i+1]-x[i]))*0.5
            # D[i] = (y[i+1]-y[i-1])/(x[i+1]-x[i-1])
        D[n] = (y[n]-y[n-1])/(x[n]-x[n-1])
        return (x, y, D, logx)
    a = [0]*w*h
    for i in xrange(1, n, 1):
        a[i*w+i-1] = 1/(x[i]-x[i-1])
        a[i*w+i  ] = 2*(1/(x[i]-x[i-1])+1/(x[i+1]-x[i]))  # noqa
        a[i*w+i+1] = 1/(x[i+1]-x[i])
        a[i*w+n+1] = (3*((y[i]-y[i-1])/(x[i]-x[i-1])**2+(y[i+1]-y[i]) /
                      (x[i+1]-x[i])**2))
    a[    0  ] = 2*(x[1]-x[0])    # noqa
    a[    1  ] =   (x[1]-x[0])    # noqa
    a[    n+1] = 3*(y[1]-y[0])    # noqa
    a[n*w+n-1] =   (x[n]-x[n-1])  # noqa
    a[n*w+n  ] = 2*(x[n]-x[n-1])  # noqa
    a[n*w+n+1] = 3*(y[n]-y[n-1])
    result = rowreduce(w, h, a)
    D = [result[2][j*w+w-1] for j in xrange(h)]
    return (x, y, D, logx)


def next_point(state, dt):
    """Compute the next position of a sphere using a Runge-Kutta
     interpolation.
    Enter: state: the current state of the projectile, including position,
                  velocity, and other properties.
           dt: time delta in seconds.
    Exit:  newstate: the updated state."""
    newstate = state.copy()
    x = state.get('x', 0)
    y = state.get('y', 0)
    vx = state.get('vx', 0)
    vy = state.get('vy', 0)
    # we use the acceleration, if it is stored
    if 'ax' not in state or 'ay' not in state:
        (ax, ay) = acceleration(state, y, vx, vy)
    else:
        ax = state['ax']
        ay = state['ay']
    if Verbose >= 2:
        display_status(state, {'ax': ax, 'ay': ay})
    if UseRungeKutta is True:
        dx1 = dt*vx
        dy1 = dt*vy
        dvx1 = dt*ax
        dvy1 = dt*ay
        (ax1, ay1) = acceleration(state, y+0.5*dy1, vx+0.5*dvx1, vy+0.5*dvy1)

        dx2 = dt*(vx+0.5*dvx1)
        dy2 = dt*(vy+0.5*dvy1)
        dvx2 = dt*ax1
        dvy2 = dt*ay1
        (ax2, ay2) = acceleration(state, y+0.5*dy2, vx+0.5*dvx2, vy+0.5*dvy2)

        dx3 = dt*(vx+0.5*dvx2)
        dy3 = dt*(vy+0.5*dvy2)
        dvx3 = dt*ax2
        dvy3 = dt*ay2
        (ax3, ay3) = acceleration(state, y+dy3, vx+dvx3, vy+dvy3)

        dx4 = dt*(vx+dvx3)
        dy4 = dt*(vy+dvy3)
        dvx4 = dt*ax3
        dvy4 = dt*ay3

        newstate['x'] = x+(dx1+dx2*2+dx3*2+dx4)/6
        newstate['y'] = y+(dy1+dy2*2+dy3*2+dy4)/6
        newstate['vx'] = vx+(dvx1+dvx2*2+dvx3*2+dvx4)/6
        newstate['vy'] = vy+(dvy1+dvy2*2+dvy3*2+dvy4)/6
    else:
        newstate['x'] = vx*dt+x
        newstate['y'] = vy*dt+y
        newstate['vx'] = vx+ax*dt
        newstate['vy'] = vy+ay*dt
    # All methods advance the same amount of time
    newstate['time'] = state.get('time', 0)+dt
    # store the acceleration for the next step
    (ax4, ay4) = acceleration(newstate)
    newstate['ax'] = ax4
    newstate['ay'] = ay4
    return newstate


def parse_arguments(argv, allowUnknownParams=False):  # noqa
    """Parse command line arguments, read in the config file, and read in
    environment configuration.
    Enter: argv: command line arguments (excluding the program -- usually this
                 is sys.argv[1:]).
           allowUnknownParams: if False, ask for help if an unknown parameter
                               is specified.
    Exit:  params: program parameters.
           state: initial calculation state.
           help: True if the help must be shown."""
    global PrecisionInDigits, UseRungeKutta, Verbose

    state = {'final_height': 0}
    params = {}
    help = False
    argv[0:0] = read_config()
    argv[0:0] = read_config_env()
    i = 0
    while i < len(argv):
        arg = argv[i]
        i += 1
        if arg.startswith('--cdgraph='):
            params['cdgraph'] = (params.get('cdgraph', '') + ',' +
                                 arg.split('=', 1)[1]).strip(',')
        elif arg.startswith('--comment='):
            params['comment'] = arg.split('=', 1)[1]
        elif arg.startswith('--config='):
            argv[i:i] = read_config(arg.split('=', 1)[1])
        elif arg == '--graph':
            params['graph'] = ''
        elif arg.startswith('--graph='):
            params['graph'] = arg.split('=', 1)[1]
        elif arg == '--materials':
            params['materials'] = True
        elif arg.startswith('--materials='):
            params['materials'] = arg.split('=', 1)[1]
        elif arg.startswith('--method='):
            method = arg.split('=', 1)[1]
            UseRungeKutta = (method != 'simple')
        elif arg == '--nounknown':
            if 'unknown' in params:
                del params['unknown']
        elif arg == '--output':
            if 'output' not in params:
                params['output'] = ''
        elif arg.startswith('--output='):
            params['output'] = (params.get('output', '') + ',' +
                                arg.split('=', 1)[1]).strip(',')
        elif arg.startswith('--precision='):
            PrecisionInDigits = float(arg.split('=', 1)[1])
        elif arg.startswith('--scan='):
            params['unknown_scan'] = arg.split('=', 1)[1]
        elif arg == '--units':
            params['units'] = True
        elif arg.startswith('--units='):
            params['units'] = arg.split('=', 1)[1]
        elif arg == '-v':
            Verbose += 1  # noqa
        elif arg == '--version':
            params['version'] = True
        else:
            value = None
            for key in Factors:
                fac = Factors[key]
                if arg.startswith('--%s=' % key):
                    value = arg.split('=', 1)[1]
                elif 'long' in fac and arg.startswith('--%s=' % fac['long']):
                    value = arg.split('=', 1)[1]
                elif ('short' in fac and arg == '-'+fac['short'] and
                        i < len(argv)):
                    value = argv[i]
                    i += 1
                elif ('short' in fac and arg.startswith('-'+fac['short']) and
                        len(arg) > 1+len(fac['short'])):
                    value = arg.split('-'+fac['short'], 1)[1]
                if value is not None:
                    if (value == '?' and
                            fac.get('method', 'binary') is not None):
                        params['unknown'] = key
                    elif len(value) == 0 and key in state:
                        del state[key]
                    else:
                        state[key] = convert_units(value, to=fac.get(
                            'units', None), from_units=fac.get('units', None))
                    break
            if value is None and not allowUnknownParams:
                help = True
    if not help:
        help = True
        for key in ('cdgraph', 'materials', 'output', 'units', 'unknown',
                    'version'):
            if key in params:
                help = False
    return params, state, help


def parse_user_params(default_params={}, user_params=None):
    """Parse a comma-separated list of key=value parameters, and populate a
     dictionary with the values.
    Enter: default_params: a dictionary with the default values.  Only
                           parameters listed in the dictionary are set.
                           Other parameters and value-less parameters are
                           returned separately.  Values within the default
                           dictionary are kept the same type as the
                           default.
           user_params: a comma-separated key=value list of parameters.
    Exit:  params: a dictionary with the user parameters combined with the
                   default parameters.
           other_params: a dictionary of parameters that were not present
                         in the default dictionary.
           items: a list of keys without values."""
    params = default_params.copy()
    other_params = {}
    items = []
    if user_params:
        for param in user_params.split(','):
            try:
                key, value = param.split('=', 1)
                if key not in params:
                    params[key] = value
                    continue
                if isinstance(params[key], int):
                    params[key] = int(value)
                elif isinstance(params[key], float):
                    params[key] = float(value)
                else:
                    params[key] = value
            except Exception:
                if param.strip():
                    items.append(param.strip())
    return (params, other_params, items)


def pressure_from_altitude(y):
    """Calculate standard atmospheric pressure based on an altitude in m.
     The basic formula can be found many places.  For instance, Munson,
     Young, and Okiishi, 'Fundmanetals of Fluid Mechanics', p. 51.
    Enter: y: altitude in m.
    Exit:  p: pressure in N/m/m."""
    p0 = 101325  # Pa, standard pressure at sea level
    L = 0.0065   # K/m, temperature lapse rate
    T0 = 288.15  # K, reference temperature at sea level
    g = 9.80655  # m/s/s, gravity at sea level
    # I've used the more authoritative values from CIPM-2007 for these constants
    M = 0.02896546  # kg/mol, molar mass of dry air, from CIPM-2007
    R = 8.314472  # J/(mol*K), universal gass constant, from CIPM-2007
    p = p0*(1-L*y/T0)**(g*M/(R*L))
    return p


def read_config(config_file=None):
    """Read a config file and treat it as a series of command line
     arguments at the point in the command line where the config file
     appears.  Any line that begins with # is treated as a comment and
     ignored.  If a lines does not contain an = but does contain a space,
     then it is treated as two parameters split on the first space.
    Enter: config_file: name of the config file to read.  None to read
                        'ballistics.conf'.
    Exit:  arguments: a list of the arguments to insert as if on the
                      command line."""
    args = []
    if config_file is None:
        config_file = os.path.splitext(os.path.abspath(__file__))[0]+'.conf'
    if not os.path.exists(config_file):
        if Verbose >= 4:
            sys.stderr.write('Can\'t find config file: %s\n' % config_file)
        return args
    try:
        fptr = open(config_file, 'r')
    except Exception:
        if Verbose >= 4:
            sys.stderr.write('Can\'t open config file: %s\n' % config_file)
        return args
    for line in fptr:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        if '=' in line or ' ' not in line:
            args.append(line)
        else:
            args.extend(line.split(' ', 1))
    fptr.close()
    return args


def read_config_env():
    """Check if there is an environment variable called BALLISTICS_CONF.
     If so, read the value and split it on spaces.
    Exit:  arguments: a list of the arguments to insert as if on the
                      command line."""
    args = []
    env = os.getenv('BALLISTICS_CONF')
    if not env:
        return args
    args = env.strip().split(' ')
    return args


def rowreduce(w, h, matrix):  # noqa - mccabe
    """Row reduce a matrix.  The matrix must be at least as wide as it is
     high.  The main diagonal is changed to 1, and all other elements in
     the main square are changed to zero.  If the process fails due to an
     undetermined value, the matrix is only partially row reduced.  Note
     that this first converts the matrix into an upper triangular matrix,
     then finishes reducing that.
    Enter: w: width of the matrix
             h: height of the matrix
             matrix: an array of w*h float values.
    Exit:  w: width of the matrix
             h: height of the matrix
             matrix: an array of w*h float values."""
    if w < h:
        return (w, h, matrix)
    a = [float(val) for val in matrix]
    for i in xrange(h):
        for j in xrange(i, h, 1):
            if a[j*w+i]:
                break
        if j == h:
            return (w, h, a)
        if j != i:
            for k in xrange(i, w, 1):
                temp = a[i*w+k]
                a[i*w+k] = a[j*w+k]
                a[j*w+k] = temp
        for j in xrange(w-1, i, -1):
            a[i*w+j] /= a[i*w+i]
        a[i*w+i] = 1.0
        for j in xrange(i+1, h, 1):
            temp = a[j*w+i]
            if temp:
                for k in xrange(i, w, 1):
                    a[j*w+k] -= a[i*w+k]*temp
    for i in xrange(h-1, -1, -1):
        for j in xrange(i+1, h, 1):
            temp = a[i*w+j]
            if temp:
                for k in xrange(h, w, 1):
                    a[i*w+k] -= a[j*w+k]*temp
                a[i*w+j] = 0.0
    return (w, h, a)


def speed_of_sound(state):
    """Calculate the speed of sound in m/s based on the temperature and
     humidity.  Taken from Bohn, Dennis A.  "Environmental Effects on the
     Speed of Sound."  Journal of the Audio Engineering Society.  36, no. 4
     (April, 1988): 223-231.
    Enter: state: a dictionary of the current state.  See comment at the
                  top of the program.
    Exit:  speed_of_sound: the speed of sound in m/s."""
    if 'density_data' not in state:
        # This populates density_data with a variety of values we need,
        # including the mole fraction of water vapor and the temperature
        atmospheric_density(state)
    T = state['density_data']['T']
    xv = state['density_data']['xv']  # mole fraction of water
    gammaw = (7.+xv)/(5.+xv)
    Ma = 0.02896546  # kg/mol, molar mass of dry air, from CIPM-2007
    Mv = 0.01801528  # kg/mol, molar mass of water vapor, from CIPM-2007
    Mw = Ma*(1-xv)+Mv*xv
    gammaa = 7./5.
    sos = 331.45*(T/273.15)**0.5*((gammaw/Mw)/(gammaa/Ma))**0.5
    return sos


def trajectory(state):  # noqa - mccabe
    """Compute the trajectory of the specified sphere.
    Enter: state: a dictionary of the initial state.  See comment at the
                  top of the program.
    Exit:  final_state: the final state of the projectile.  This includes
                        an 'error' item if there is insufficient data for
                        calculation.
           points: a list of points along the trajectory."""
    state = state.copy()
    # Set up the initial conditions
    state['time'] = 0
    state['x'] = 0
    state['y'] = state.get('initial_height', 0)
    if state['y'] is None:
        state['y'] = 0
    state['max_height'] = state['y']
    # determine the third of material, diameter, and mass if two are known
    state = determine_material(state, Verbose)
    v = state.get('initial_velocity', 0)
    if not v:
        try:
            v = (2*state['charge']*state['power_factor']/state['mass'])**0.5
            state['initial_velocity'] = v
        except Exception:
            state['error'] = ('Failed - no initial velocity or no charge, '
                              'power factor, or mass.')
            return (state, [])
    if 'charge' not in state and 'power_factor' in state:
        state['charge'] = state['mass']*v**2/(2*state['power_factor'])
    if 'power_factor' not in state and 'charge' in state:
        state['power_factor'] = state['mass']*v**2/(2*state['charge'])
    angle = math.pi/180*state.get('initial_angle', 45.)
    state['vx'] = v*math.cos(angle)
    state['vy'] = v*math.sin(angle)
    (ax, ay) = acceleration(state)
    state['ax'] = ax
    state['ay'] = ay
    delta = state.get('time_delta', 0.01)
    final_y = state.get('final_height', None)
    max_range = state.get('range', None)
    max_time = state.get('final_time', None)
    min_velocity = state.get('final_velocity', None)
    if (final_y is None and max_range is None and max_time is None and
            min_velocity is None):
        state['error'] = ('Failed - at least one of final_height, range, '
                          'final_time, or final_velocity must be specified '
                          'to compute the trajectory.')
        return (state, [])
    # Now compute the trajectory in a series of steps until the end condition is
    # reached.
    laststate = None
    points = []
    while True:
        proceed = 'check'
        if final_y is not None:
            offset = state['y']-final_y
            if state['vy'] >= 0:
                proceed = True
        elif max_range is not None:
            offset = max_range-state['x']
        elif max_time is not None:
            offset = time-state['time']
        elif min_velocity is not None:
            offset = (state['vx']**2+state['vy']**2)**0.5-min_velocity
        if offset < 0 and proceed == 'check':
            break
        if state['y'] > state['max_height']:
            state['max_height'] = state['y']
        if (not len(points) or
                state['time']-points[-1]['time']+delta*0.5 > MinPointInterval):
            point = {}
            for key in ('x', 'y', 'vx', 'vy', 'ax', 'ay', 'time'):
                point[key] = state[key]
            points.append(point)
        laststate = state
        lastoffset = offset
        state = next_point(state, delta)
        if Verbose >= 4:
            pprint.pprint(state)
    final_state = state.copy()
    if laststate:
        a = offset/(offset-lastoffset)
        if a > 2:
            a = 2
        if a < -1:
            a = -1
        b = 1-a
        for key in ('x', 'y', 'vx', 'vy', 'ax', 'ay', 'time'):
            final_state[key] = b*state[key]+a*laststate[key]
        if final_y is not None:
            final_state['y'] = final_y
        elif max_range is not None:
            final_state['x'] = max_range
        elif max_time is not None:
            final_state['time'] = max_time
        point = {}
        for key in ('x', 'y', 'vx', 'vy', 'ax', 'ay', 'time'):
            point[key] = final_state[key]
        points.append(point)
    if Verbose >= 2:
        display_status(final_state, last=True)
    return (final_state, points)


def trajectory_error(initial_state, unknown, unknown_value):
    """Determine how far off the results of a trajectory calculation are
     from the expected outcome.
    Enter: initial_state: a dictionary of the initial state.  See comment
                          at the top of the program.
           unknown: the parameter within the state to set.  The value is
                    never the tested value.
           unknown_value: the value to set the unknown parameter to when
                          calculating the trajectory.
    Exit:  error: a metric of how far off the trajectory is from the
                    expected outcome."""
    global Verbose
    state = initial_state.copy()
    state[unknown] = unknown_value
    Verbose -= 2
    (state, points) = trajectory(state)
    Verbose += 2
    if Verbose >= 5:
        pprint.pprint(state)
    if state is None:
        print 'Cannot calculate trajectory error - trajectory is None'
        return None
    if (unknown != 'final_velocity' and
            initial_state.get('final_velocity', None) is not None):
        v0 = initial_state['final_velocity']
        v = (state['vx']**2+state['vy']**2)**0.5
        return v-v0
    if unknown != 'range' and initial_state.get('range', None) is not None:
        x0 = initial_state['range']
        x = state['x']
        return x-x0
    if (unknown != 'final_time' and
            initial_state.get('final_time', None) is not None):
        t0 = initial_state['final_time']
        t = state['time']
        return t-t0
    if (unknown != 'max_height' and
            initial_state.get('max_height', None) is not None):
        y0 = initial_state['max_height']
        y = state['max_height']
        return y-y0
    print 'Cannot calculate trajectory error - nothing to solve for'
    return None


def version_check():
    """If the program was run directly from the py file AND we can identify
     the py file source, calculate the md5sum of the entire program EXCEPT
     the program signature.  If the program signature differs from the
     current value, increment the version number, calculate a new program
     signature, and save the file."""
    path = os.path.abspath(__file__)
    if Verbose >= 4:
        sys.stderr.write('Program file path: %s\n' % path)
    if not path.endswith('.py'):
        return
    # I use vim, and if I have the source file open, don't update the version
    # number
    if os.path.exists(os.path.join(os.path.dirname(path),
                                   '.'+os.path.basename(path)+'.swp')):
        return
    try:
        src = open(path, 'rb').read()
    except Exception:
        sys.stderr.write('Can\'t read source file to determine version.\n')
        return
    # If I've left a debug comment in the source, don't update the version
    if ('DWM' + '::') in src:
        return
    sigstart = 'PROGRAM_SIGNATURE = \''
    sigpos = src.find(sigstart)
    if sigpos < 0:
        sys.stderr.write('Can\'t find program signature.\n')
        return
    sigpos += len(sigstart)
    sigend = src.find('\'', sigpos)
    if sigend < 0:
        sys.stderr.write('Can\'t find program signature.\n')
        return
    sig = md5.new(src[:sigpos]+src[sigend:]).hexdigest()
    if sig == src[sigpos:sigend]:
        return
    verstart = '__version__ = \''
    verpos = src.find(verstart)
    if verpos < 0:
        sys.stderr.write('Can\'t find program version.\n')
        return
    verpos += len(verstart)
    verend = src.find('\'', verpos)
    if verend < 0:
        sys.stderr.write('Can\'t find program version.\n')
        return
    build = int(src[verpos:verend].split('v')[1])
    newver = time.strftime('%Y-%m-%d')+'v%d' % (build+1)
    global __version__
    __version__ = newver
    if Verbose >= 1:
        sys.stderr.write('Updating program version to %s\n' % newver)
    newsrc = src[:verpos]+newver+src[verend:]
    if sigpos > verpos:
        sigpos += len(newver)-(verend-verpos)
        sigend += len(newver)-(verend-verpos)
    newsig = md5.new(newsrc[:sigpos]+newsrc[sigend:]).hexdigest()
    newsrc = newsrc[:sigpos]+newsig+newsrc[sigend:]
    tmppath = path+'.tmp'
    open(tmppath, 'wb').write(newsrc)
    shutil.move(tmppath, path)


def viscosity_dry_air(T, density):
    """Calculate the viscosity of dry air based on a function of absolute
     temperature and density.  Taken from Kadoya, K., N. Matsunaga, and A.
     Nagashima.  "Viscosity and Thermal Conductivity of Dry Air in the
     Gaseous Phase."  Journal of Physical and Chemical Reference Data.  14,
     no. 4 (1985): 947-970.
    Enter: T: temperature in K
           density: density in kg/(m^3)
    Exit:  viscosity_air: viscosity in kg/m/s (Pa*s)"""
    A = [(1, 0.128517), (0.5, 2.60661), (0, -1.00000), (-1, -0.709661),
         (-2, 0.662534), (-3, -0.197846), (-4, 0.00770147)]
    scaledT = T/132.5
    eta0 = 0
    for (i,  Ai) in A:
        eta0 += Ai*scaledT**i
    scaledRho = density/314.3
    B = [(1, 0.465601), (2, 1.26469), (3, -0.511425), (4, 0.274600)]
    delta_eta = 0
    for (i, Bi) in B:
        delta_eta += Bi*scaledRho**i
    eta = 6.16090e-6*(eta0+delta_eta)
    return eta


def viscosity_water_vapor(T, density):
    """Calculate the viscosity of water vapor based on a function of
     absolute temperature and density.  Taken from Sengers, J. V. and B.
     Kamgar-Parsi.  "Representative Equations for the Viscosity of Water
     Substance."  Journal of Physical and Chemical Reference Data.  13, no. 1
     (1984): 185-205.
    Enter: T: temperature in K
           density: density in kg/(m^3)
    Exit:  viscosity_vapor: viscosity in kg/m/s (Pa*s)"""
    scaledT = T/647.27
    mu0 = 1e-6*scaledT**0.5/(0.0181583+0.0177624/scaledT +
                             0.0105287/(scaledT**2)-0.0036744/(scaledT**3))
    scaledRho = density/317.763
    bij = [[0.501938, 0.162888, -0.130356, 0.907919, -0.551119, 0.146543],
           [0.235622, 0.789383, 0.673665, 1.207552, 0.0670665, -0.0843370],
           [-0.274637, -0.743539, -0.959456, -0.687343, -0.497089, 0.195286],
           [0.145831, 0.263129, 0.347247, 0.213486, 0.100754, -0.032932],
           [-0.0270448, -0.0253093, -0.0267758, -0.0822904, 0.0602253,
            -0.0202595]]
    factor = 0
    for j in xrange(len(bij)):
        for i in xrange(len(bij[0])):
            factor += bij[j][i]*(1/scaledT-1)**i*(scaledRho-1)**j
    mu = mu0*math.exp(scaledRho*factor)
    return mu


def warning(state, tag, message):
    """Show a warning message and mark that it was shown so it doesn't get
     shown a second time.
    Enter: state: state to record that the warning was given.
           tag: a distinct key for this warning.
           message: the actual warning message.
    """
    if 'warning' not in state:
        state['warning'] = {}
    if tag in state['warning']:
        return
    state['warning'][tag] = True
    sys.stderr.write(message)


if __name__ == '__main__':  # noqa - mccabe
    argv = sys.argv[1:]
    params, state, help = parse_arguments(argv)
    version_check()
    if help:
        print """Ballistics analysis.

Syntax:  ballistics.py --cdgraph=(params) --comment=(comment) --config=(file)
    --graph[=(params)] --help --materials[=full] --method=(method)
    --nounknown --output[=(params)] --precision=(digits) --scan=(value)
    --units[=full] -v --version (factors)

If the environment variable 'BALLISTICS_CONF' is set, the value is treated as
 if it is on the command line prior to everything else.  The value is split on
 spaces, just like the actual command line.  If there is a file in the same
 directory as the program called 'ballistics.conf', it is read and included
 after the environment variable and prior to any command line arguments.  See
 read_config for details on the file format.
--cdgraph generates a graph of the coefficient of drag based on Reynolds number
 and Mach number.  This takes a comma-separated list of parameters: remin,
 remax (minimum and maximum Reynolds numbers to plot), mnmin, mnmax (min and
 max Mach numbers to plot), mnint (Mach number interval to plot).  Example:
 '--cdgraph=remin=1e3,remax=1e7,mnmin=0,mnmax=1.5,mnint=0.25'.
--comment adds a comment that can be included as a column in the output.
--config specifies a configuration file.  A configuration file is a list of
 parameters such as would be included on the command line.  Any line that
 begins with # is a comment.  Otherwise, each line is treated as a single
 command line argument.  See the comments in read_config for more details.
--graph graphs the trajectory.  This accepts a comma separated list of
 parameters.
--help lists this help.
--materials shows a list of known materials.  If 'full' is specified, a more
 verbose list is shown.
--method specifies the numerical method to use.  The choices are 'runge' to use
 the Runge-Kutta method (the default) or 'simple' to use the simplest possible
 method.
--nounknown clears the parameter that has been specified for a solution with ?.
 This allows overriding a conf file or the environmental variable.
--output outputs the results in either a csv, html table format, or a special
 WordPress customer short-tag format.  This takes a comma-separated list of
 parameters: format (csv, html, or wp), header (none, title, units, all, or
 titleunits), units (eng, si, or both), footer (same options as header), blank
 (a number of blank lines to add before the data and after any header).  The
 factors that should be output can be listed; these may be the internal name,
 the long factor name, or the short factor name, optionally followed by
 :(units) to explicitly choose the units.  Besides the factors, you can
 include:
    comment - the comment specified on the command line
    comptime - total computation time in seconds
    method - the numerical method
    version - the program version
    diff:(factor):(value) - the difference between that factor and the specified
        value (which may include units)
    adiff:(factor):(value) - the same as diff except that html output can be
        sorted by absolute value.
 If no factors are listed, this is V,a,d,m,c,t,f,r,p,version,comment.  Example:
 '--output=format=csv,header=all,blank=1,units=both,range,p:Cal/oz,comment'.
--precision specifies the precision of the answer in number of digits.  I.e.,
 the error is expected to be less than 1x10^(-(# of digits))*(value).
--scan requires that a scan of the solution space be performed using the
 specified value (which can include units) as the step.   Otherwise, many
 factors are solved using a simple binary search.
--units shows a list of known units.  If 'full' is specified, a more verbose
 list is shown.  In addition to the listed units, most SI units can be prefixed
 with standand SI prefixes.
-v increases verbosity.
--version displays the program version.

Any factor can be specified with units.  See --units.  For example, '-c 2oz',
'--temperature=62F', or '--mass=20 lb 7 oz'.  Most factors can be solved for by
specifying '?' as the factor.  Note that a maximum of two of initial velocity,
power factor, and charge should be specified.  If only initial velocity is
specified, power factor and charge will not be determined.  Factors:"""
        factors = [(Factors[key]['long'].lower(), Factors[key]['long'], key)
                   for key in Factors]
        factors.sort()
        for (ll, lc, key) in factors:
            fac = Factors[key]
            full_desc = ''
            full_desc += '--%s' % fac['long']
            if 'short' in fac:
                full_desc += ' or -%s' % fac['short']
            full_desc += ' (%s): %s' % (key, fac['desc'])
            full_desc = line_break(full_desc, 79, 1)
            for line in full_desc:
                print line
        sys.exit(0)
    if 'cdgraph' in params:
        graph_coefficient_of_drag(params['cdgraph'])
    if 'materials' in params:
        list_materials(params['materials'])
    if 'units' in params:
        list_units(params['units'])
    if 'version' in params:
        print 'Version: '+__version__
    if 'unknown' not in params:
        if 'output' in params:
            generate_output(None, params['output'], None)
        sys.exit(0)
    if Verbose >= 2:
        pprint.pprint(state)
    starttime = get_cpu_time()
    (newstate, points) = find_unknown(
        state, params['unknown'], params.get('unknown_scan'))
    newstate['computation_time'] = get_cpu_time()-starttime
    if Verbose >= 1:
        pprint.pprint(newstate)
    if 'graph' in params:
        graph_trajectory(points, params['graph'])
    if 'output' in params:
        generate_output(newstate, params['output'], params.get('comment', None))
