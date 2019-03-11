#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright David Manthey
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

import math
from .interpolate import interpolate

# This table consists of a list of tuples of the form (Mach number, [List of
# (Reynolds Number, Coefficient of Drag)], critical Reynolds number).  The data
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
    # (0, ((1e-1, 124.9), (2e-1, 106.3), (4e-1, 54.95), (5e-1, 45.71),
    #      (1, 24.93), (5, 6.607), (10, 3.920), (50, 1.502), (100, 1.047),
    #      (500, 0.5012), (1e3, 0.4105), (2e3, 0.3743), (5e3, 0.3801),
    #      (1e4, 0.3890), (5e4, 0.4105), (1e5, 0.4169), (2e5, 0.3890),
    #      (4e5, 0.09261), (5e5, 0.08912), (6e5, 0.1063), (8e5, 0.1359),
    #      (1e6, 0.1622), (5e6, 0.3114), (1e7, 0.3388)), 5e5),
    # data for Mach 0 modified from Munson to match the expected values from
    # Miller at Re>1e4, and truncated to ignore values above 1e6 as they seem
    # weak
    (0, ((1e-1, 124.9), (2e-1, 106.3), (4e-1, 54.95), (5e-1, 45.71),
         (1, 24.93), (5, 6.607), (10, 3.920), (50, 1.502), (100, 1.047),
         (500, 0.5012), (1e3, 0.4105), (2e3, 0.3743), (5e3, 0.3801),
         (1e4, 0.3890), (3.2e4, 0.431), (7.1e4, 0.453), (1.5e5, 0.462),
         (2.3e5, 0.458), (3e5, 0.438), (3.5e5, 0.373), (3.954e5, 0.0916),
         (4.21e5, 0.0785), (5e5, 0.08912), (7.6e5, 0.158),
         (1e6, 0.20)), 4.21e5),
    (0.1, ((1e4, 0.3983), (3.093e4, 0.4352), (4.65e4, 0.4495)), 2e5),
    (0.2, ((1e4, 0.3995), (2.75e4, 0.4376), (4.874e4, 0.4590),
           (8.306e4, 0.4732), (1.484e5, 0.4792), (1.877e5, 0.4780)), 4.21e5),
    (0.3, ((1e4, 0.4126), (3.191e4, 0.4542), (7.101e4, 0.4768),
           (1.472e5, 0.4851), (2.302e5, 0.4816), (2.958e5, 0.4614),
           (3.488e5, 0.3960), (3.954e5, 0.0916), (4.21e5, 0.0785),
           (4.886e5, 0.0892), (7.58e5, 0.1593)), 4.21e5),
    (0.6, ((1e4, 0.4435), (2.369e4, 0.4685), (5.791e4, 0.4994),
           (1.137e5, 0.5220), (2.394e5, 0.5279), (3.571e5, 0.5113),
           (4.625e5, 0.4709), (5.082e5, 0.4031), (5.368e5, 0.2212),
           (5.583e5, 0.2117), (5.852e5, 0.2164), (7.232e5, 0.2580),
           (9.15e5, 0.3032), (1.323e6, 0.3591)), 5.583e5),
    (0.7, ((1e4, 0.4602), (1.613e4, 0.4709), (4.436e4, 0.5089),
           (8.984e4, 0.5375), (1.819e5, 0.5565), (3.2e5, 0.5577),
           (4.277e5, 0.5375), (5.082e5, 0.5030), (6.846e5, 0.4031),
           (8.394e5, 0.3520), (9.078e5, 0.3496), (1.054e6, 0.3650),
           (1.419e6, 0.4304), (1.927e6, 0.4875), (2.596e6, 0.5279),
           (3.552e6, 0.5517)), 9.078e5),
    (0.8, ((1e4, 0.4982), (1.691e4, 0.5137), (4.99e4, 0.5624),
           (1.405e5, 0.6052), (3.328e5, 0.6231), (5.244e5, 0.6231),
           (6.329e5, 0.6088), (7.404e5, 0.5743), (8.198e5, 0.5303),
           (9.742e5, 0.5054), (1.087e6, 0.5054), (1.476e6, 0.5363),
           (2.496e6, 0.5743), (3.842e6, 0.5945)), 9.963e5),
    (0.9, ((1e4, 0.5529), (1.704e4, 0.5672), (3.069e4, 0.5933),
           (5.029e4, 0.6219), (7.925e4, 0.6528), (1.722e5, 0.7075),
           (2.982e5, 0.7313), (8.798e5, 0.7384), (4.601e6, 0.7384)), 1e6),
    (1.0, ((1e4, 0.7146), (1.626e4, 0.7158), (3.618e4, 0.7408),
           (1.068e5, 0.7967), (2.413e5, 0.8300), (4.773e5, 0.8419),
           (5.257e6, 0.8407)), 1e6),
    (1.1, ((1e4, 0.7753), (1.917e4, 0.7895), (4.836e4, 0.8240),
           (1.076e5, 0.8656), (2.451e5, 0.8954), (5.162e5, 0.9061),
           (5.776e6, 0.9025)), 1e6),
    (1.2, ((1e4, 0.8193), (1.902e4, 0.8276), (5.313e4, 0.8609),
           (1.259e5, 0.8989), (3.276e5, 0.9298), (7.761e5, 0.9417),
           (7.194e6, 0.9417)), 1e6),
    (1.4, ((1e4, 0.8954), (1.815e4, 0.8906), (3.913e4, 0.9084),
           (8.571e4, 0.9394), (1.952e5, 0.9679), (3.832e5, 0.9834),
           (8.134e5, 0.9857), (1e7, 0.9810)), 1e6),
    (1.8, ((1e4, 0.9453), (1.412e4, 0.9382), (3.166e4, 0.9394),
           (7.74e4, 0.9572), (1.543e5, 0.9738), (2.651e5, 0.9822),
           (6.686e5, 0.9857), (1e7, 0.9810)), 1e6),
    (2.0, ((1e4, 0.9575), (2.15e4, 0.9391), (1e5, 0.9592), (1e6, 0.992),
           (1e7, 0.9932)), 1e6),
    (2.5, ((1e4, 0.9663), (3.3e4, 0.9288), (1e5, 0.9473), (1e6, 0.9691),
           (1e7, 0.973)), 1e6),
    (3.0, ((1e4, 0.9663), (3.3e4, 0.9288), (1e5, 0.9329), (1e6, 0.9485),
           (1e7, 0.9494)), 1e6),
    # Mach 4.5 is from Munson, fig 11.2, p. 709
    (4.5, ((1e4, 0.906), (1e7, 0.906)), 1e6),
]
MnReCdDataTableLog10Crit = [
    (machnum, math.log10(crit)) for (machnum, reynolds_data, crit) in MnReCdDataTable]


def coefficient_of_drag_miller(state, only_in_range=False):
    """
    Calculate the coefficient of drag using the graph from Miller that I
    digitized.

    Enter: state: a dictionary of the current state.  Includes Reynolds and
                  mach numbers.
           only_in_range: if True, return None if the values are outside of
                          what we can interpolate.
    Exit:  Cd: the coefficient of drag.
    """
    Re = state['drag_data']['Re']
    Mn = state['drag_data']['Mn']
    # Estimate the critical point based on Mach number
    (critical_Re, in_range) = interpolate(Mn, MnReCdDataTableLog10Crit, method='linear')
    critical_Re = 10**critical_Re
    state['drag_data']['critical_Re'] = critical_Re
    # Interpolate for the Reynolds number for each Mach number where we have
    # data.
    mach_data_oor = []
    mach_data = []
    for pos, (mach, reynolds_data, crit) in enumerate(MnReCdDataTable):
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
        (Cd, in_range) = interpolate(adjusted_re, reynolds_data, True)
        if in_range:
            mach_data.append((mach, Cd))
        else:
            mach_data_oor.append((mach, Cd))
    if (Mn > 0.3 and len(mach_data) < 2) or not len(mach_data):
        if only_in_range:
            state['drag_data']['in_range'] = False
            return None
    if not len(mach_data):
        mach_data = mach_data_oor
        (Cd, in_range) = interpolate(Mn, mach_data, method='linear')
        in_range = False
    else:
        (Cd, in_range) = interpolate(Mn, mach_data, method='linear')
    state['drag_data']['cd'] = Cd
    state['drag_data']['in_range'] = in_range
    if not in_range and only_in_range:
        return None
    return Cd
