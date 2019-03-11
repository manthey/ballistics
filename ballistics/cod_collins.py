#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Converted from the javascript code located at
# http://arc.id.au/CannonballDrag.html
#
# Original comment:
#
# SphereDrag
# Calculation of aerodynamic drag coefficient for a sphere at
# speeds near the speed of sound.
# Free to use. Please give credit to A.R.Collins [www.arc.id.au]
# last rev: 08Mar16

import math


def bezier4pt(x, x1, y1, x2, y2, x3, y3, x4, y4, dx=0):
    """
    Finds approximate y from cubic Bezier given x worst case y(x + xerr) is
    returned (where xerr is optional parm) assumes fn is well behaved (i.e.,
    single valued for all x).  Adapted from
    [http://antigrain.com/research/adaptive_bezier/]
    """
    # Calculate mid-points of line segments
    x12 = (x1 + x2) / 2
    y12 = (y1 + y2) / 2
    x23 = (x2 + x3) / 2
    y23 = (y2 + y3) / 2
    x34 = (x3 + x4) / 2
    y34 = (y3 + y4) / 2
    x123 = (x12 + x23) / 2
    y123 = (y12 + y23) / 2
    x234 = (x23 + x34) / 2
    y234 = (y23 + y34) / 2
    x1234 = (x123 + x234) / 2
    y1234 = (y123 + y234) / 2
    xerr = dx or 0.0005  # acceptable x error

    if x <= x1:
        return y1

    if x >= x4:
        return y4

    # x1234, y1234 is on the curve and between x1 and x4
    if x >= x1234:  # x is on new shorter curve between x1234 and x4
        if (x-x1234) > xerr:
            return bezier4pt(x, x1234, y1234, x234, y234, x34, y34, x4, y4)
        else:
            return y1234
    else:           # x is on new shorter curve between x1 and x1234
        if (x1234-x) > xerr:
            return bezier4pt(x, x1, y1, x12, y12, x123, y123, x1234, y1234)
        else:
            return y1234


def SphereDragVsRe(Re):
    """
    Return the Reynolds number for flow past a sphere from "Data Correlation
    for Drag Coeff for Sphere" F.A.Morrison [chem.mtu.edu]
    """
    def log10(val):
        return math.log(val) / math.log(10)

    if Re > 2E6:
        Cd = 0.15
    if Re > 1.2E6:
        Cd = 0.19 - 8E4 / Re
    elif Re > 4.77E5:
        Cd = -0.485 + 0.1 * log10(Re)
    else:
        Cd = (24/Re + (2.6*(Re/5))/(1+math.pow(Re/5, 1.52)) +
              (0.411*math.pow(Re/263000, -7.94)) /
              (1+math.pow(Re/263000, -8)) + math.pow(Re, 0.8) / 461000)

    return Cd


def SphereDrag(v, d):  # speed, diameter
    """
    Modifies Morrison drag coeff v Reynolds number for speeds near Mach 1 to
    match experiment data summarised in 'Sphere Drag at Mach Numbers from 0.3
    to 2.0' Miller & Bailey [J.Fluid Mech, 1979].
    """
    # Imperial units
    SSpd = 1116  # sound speed at sea level (340.2 m/s)
    rho = 0.074  # density of air    (1.225 kg/m^3)
    eta = 3.75E-7  # viscosity of air (1.81E-5 kg/m.s)
    Mn = v / SSpd  # Mach number

    if Mn < 0.2:
        Mn = 0.2
    if Mn > 1.5:
        Mn = 1.5
    Re = v * d * rho / eta  # Reynolds number
    k = 1.0 if Mn >= 1.5 else bezier4pt(
        Mn, 0.1, 0.00, 0.95, 0.0, 0.55, 0.95, 1.5, 1.0)
    t = 0.0 if Mn > 1.0 else bezier4pt(
        Mn, 0.0, 1.1, 0.85, 1.1, 0.57, 0.05, 1.0, 0.0)
    sf = 0.78 + 0.22 * math.atan(-12 * (Mn - 0.23))
    Cd = k + t * SphereDragVsRe(sf * Re)

    return Cd


def coefficient_of_drag_collins(state, only_in_range=False):
    """
    Calculate the coefficient of drag using the graph from Miller that I
    digitized.

    Enter: state: a dictionary of the current state.  Includes Reynolds and
                  mach numbers.
           only_in_range: if True, return None if the values are outside of
                          what we can interpolate.
    Exit:  cd: the coefficient of drag.
    """
    Re = state['drag_data']['Re']
    Mn = state['drag_data']['Mn']
    if Mn < 0.2:
        Mn = 0.2
    if Mn > 1.5:
        Mn = 1.5
    k = 1.0 if Mn >= 1.5 else bezier4pt(
        Mn, 0.1, 0.00, 0.95, 0.0, 0.55, 0.95, 1.5, 1.0)
    t = 0.0 if Mn > 1.0 else bezier4pt(
        Mn, 0.0, 1.1, 0.85, 1.1, 0.57, 0.05, 1.0, 0.0)
    sf = 0.78 + 0.22 * math.atan(-12 * (Mn - 0.23))
    Cd = k + t * SphereDragVsRe(sf * Re)
    state['drag_data']['cd'] = Cd
    return Cd
