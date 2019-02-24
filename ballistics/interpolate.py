import functools
import math


def cubic_roots(a, b, c, d):
    """
    Compute the roots of a cubic equation.  Only real roots are returned.
    This works properly with lesser degree equations if the higher order
    coefficients are set to zero.

    Enter: a, b, c, d: coefficients of the cubic equation.  These are of
                       the form a*x^3+b*x^2+c*x+d=0.
    Exit:  roots: a list of zero to three real roots.
    """
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


@functools.lru_cache(maxsize=100)
def data_to_sorted_xy(data, logx):
    """
    Return a list of (x, y) pairs with distinct x values and sorted by x value.

    Enter: data: a list of (x, y) or [x, y] values.
           logx: True to return (log10(x), y) for each entry.
    Exit:  data: the sorted list with unique x values.
    """
    if logx:
        return sorted({math.log10(x): y for x, y in data}.items())
    return sorted(dict(data).items())


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
     splines are separate for x and y.  This should be functionally
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
    xy = data_to_sorted_xy(tuple(data), logx)
    for pos, (x, y) in enumerate(xy):
        if xi <= x:
            break
    if xi == x:
        return y, True
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
    x, y = zip(*xy[minpos:maxpos])
    num_points = len(x)
    if not num_points:
        yi = 0
        in_range = False
    elif num_points == 1:
        yi = y[0]
        in_range = False  # since (xi == x[0]) is always False
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
                m1 = 0.5*(y[2]-y[0])/(x[2]-x[0])
                m2 = 0.5*(y[3]-y[1])/(x[3]-x[1])
            else:
                m1 = (y[2]-y[0])/(x[2]-x[0])
                m2 = (y[3]-y[1])/(x[3]-x[1])
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
    """
    Interpolate a value from a set of points.  The points must have been
    prepared with natural_bicubic_prep.

    Enter: xi: x value to interpolate from.
           data: the tuple of (x, y, Dx, Dy, logx) as returned from
                 natural_bicubic_prep.
    Exit:  yi: the interpolated y value.  0 if the data list is empty.
           in_range: True if x is interpolated, False if it is
                     extrapolated.
    """
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
    """
    Prepare the derivatives needs to each point so that we can use a
    natural cubic function for interpolation.

    Enter: data: a list of two-tuples ((x, y) pairs).
           logx: if True, perform the interpolations on the log values of
                 the x data.
    Exit:  x: a list of the x values used for the interpolation.
           y: a list of the y values used for the interpolation.
           Dx: a list of derivatives for the x values.
           Dy: a list of derivatives for the y values.
           logx: the value specified for input.
    """
    xy = data_to_sorted_xy(tuple(data), logx)
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
        for i in range(1, n, 1):
            a[i*w+i-1] = 1
            a[i*w+i  ] = 4  # noqa
            a[i*w+i+1] = 1
            a[i*w+n+1] = 3*(p[i+1]-p[i-1])
        a[n*w+n-1] = 1
        a[n*w+n  ] = 2  # noqa
        a[n*w+n+1] = 3*(p[n]-p[n-1])
        result = rowreduce(w, h, a)
        D = [result[2][j*w+w-1] for j in range(h)]
        if axis == 'x':
            Dx = D
        else:
            Dy = D
    return (x, y, Dx, Dy, logx)


def natural_cubic(xi, data):
    """
    Interpolate a value from a set of points.  The points must have been
    prepared with natural_cubic_prep.

    Enter: xi: x value to interpolate from.
           data: the tuple of (x, y, D, logx) as returned from
                 natural_cubic_prep.
    Exit:  yi: the interpolated y value.  0 if the data list is empty.
           in_range: True if x is interpolated, False if it is
                     extrapolated.
    """
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
    """
    Prepare the derivatives needs to each point so that we can use a natural
    cubic function for interpolation.

    Enter: data: a list of two-tuples ((x, y) pairs).
           logx: if True, perform the interpolations on the log values of
                 the x data.
           simple: if True, don't actually use a natural cubic; rather, use
                   a simple weighted calculation for the derivatives.
    Exit:  x: a list of the x values used for the interpolation.
             y: a list of the y values used for the interpolation.
             D: a list of derivatives for each point.
             logx: the value specified for input.
    """
    xy = data_to_sorted_xy(tuple(data), logx)
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
        for i in range(1, n, 1):
            D[i] = ((y[i]-y[i-1])/(x[i]-x[i-1])+(y[i+1]-y[i])/(x[i+1]-x[i]))*0.5
            # D[i] = (y[i+1]-y[i-1])/(x[i+1]-x[i-1])
        D[n] = (y[n]-y[n-1])/(x[n]-x[n-1])
        return (x, y, D, logx)
    a = [0]*w*h
    for i in range(1, n, 1):
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
    D = [result[2][j*w+w-1] for j in range(h)]
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
    for i in range(h):
        for j in range(i, h, 1):
            if a[j*w+i]:
                break
        if j == h:
            return (w, h, a)
        if j != i:
            for k in range(i, w, 1):
                temp = a[i*w+k]
                a[i*w+k] = a[j*w+k]
                a[j*w+k] = temp
        for j in range(w-1, i, -1):
            a[i*w+j] /= a[i*w+i]
        a[i*w+i] = 1.0
        for j in range(i+1, h, 1):
            temp = a[j*w+i]
            if temp:
                for k in range(i, w, 1):
                    a[j*w+k] -= a[i*w+k]*temp
    for i in range(h-1, -1, -1):
        for j in range(i+1, h, 1):
            temp = a[i*w+j]
            if temp:
                for k in range(h, w, 1):
                    a[i*w+k] -= a[j*w+k]*temp
                a[i*w+j] = 0.0
    return (w, h, a)
