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

import math

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


def coefficient_of_drag_miller(state, only_in_range=False):
    """Calculate the coefficient of drag using the graph from Miller that I
     digitized.
    Enter: state: a dictionary of the current state.  Includes Reynolds and
                  mach numbers.
           only_in_range: if True, return None if the values are outside of
                          what we can interpolate.
    Exit:  cd: the coefficient of drag."""
    Re = state['drag_data']['Re']
    Mn = state['drag_data']['Mn']
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
            state['drag_data']['in_range'] = False
            return None
    if not len(mach_data):
        mach_data = mach_data_oor
        (cd, in_range) = interpolate(Mn, mach_data, method='linear')
        in_range = False
    else:
        (cd, in_range) = interpolate(Mn, mach_data, method='linear')
    state['drag_data']['cd'] = cd
    state['drag_data']['in_range'] = in_range
    if not in_range and only_in_range:
        return None
    return cd


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
