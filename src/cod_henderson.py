#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 ( the "License" ); you may
# not use this file except in compliance with the License.  You may obtain a
# copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   See the
# License for the specific language governing permissions and limitations
# under the License.


import math


def coefficient_of_drag_henderson(state, only_in_range=False):
    """Calculate the coefficient of drag using the equations provided from
     Henderson, Charles B.  "Drag Coefficients of Spheres in Continuum and
     Rarefied Flows."  AIAA Journal.  14, no. 6 (1976): 707-708.
    Enter: state: a dictionary of the current state.  Includes Reynolds and
                  mach numbers.
           only_in_range: if True, return None if the values are outside of
                          what we can interpolate.
    Exit:  cd: the coefficient of drag."""
    Re = state['drag_data']['Re']
    Mn = state['drag_data']['Mn']

    Tw = T = state.get('T', 288.15)

    SHair = 1.020
    SHtable = {'lead': 0.160, 'brass': 0.380}
    SH = SHtable.get(state.get('material'), 0.444)
    gamma = SH / SHair
    S = Mn * (gamma / 2) ** 0.5

    Cdlow = (
        24 * (Re + S * (4.33 + (
            (3.65 - 15.3 * Tw / T) / (1 + 0.353 * Tw / T)) *
            math.exp(-0.247 * Re / S))) ** -1 +
        math.exp(-0.5 * Mn / (Re ** 0.5)) *
        ((4.5 + 0.38 * (0.003 * Re + 0.48 * Re ** 0.5)) /
            (1 + 0.003 * Re + 0.48 * Re ** 0.5) +
            0.1 * Mn ** 2 + 0.2 * Mn ** S) +
        (1 - math.exp(-Mn / Re)) * 0.6 * S)
    Cdhigh = (
        (0.9 + 0.34 / (Mn ** 2) + 1.86 * ((Mn / Re) ** 0.5) *
         (2 + 2 / S ** 2 + 1.058 / S * (Tw / T) ** 0.5 - 1 / S ** 4)) /
        (1 + 1.86 * (Mn / Re) ** 0.5))
    if Mn <= 1:
        Cd = Cdlow
    elif Mn >= 1.75:
        Cd = Cdhigh
    else:
        f = (Mn - 1) / 0.75
        Cd = (1 - f) * Cdlow + f * Cdhigh
        print Cdlow, Cdhigh, f, Cd
    state['drag_data']['cd'] = Cd
    return Cd
