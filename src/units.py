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
Unit conversion functions and units definitions.
"""

import math
import sys

from formattext import line_break

#   References:
# Robertson, John, *A Treatise of Mathematical Instruments*, originally
#   published London: printed for J. Nourse, 1775, reprinted by Arlington, VA:
#   The Invisible College Press, 2002.
# Stone, Edmund, *The Construction and Principal Uses of Mathematical
#   Instruments, translated from the French of M. Bion*, originally published
#   Lonndon: printed for J. Richardson, 1758, reprinted by Mendham, NJ:
#   Astragal Press, 1995.
# Clarke, F. W.  *Weights, Measures, and Money, of All Nations*,  New York:
#   D. Appleton and Company: 1891.

StatuteFootInMeters = 0.3048
# Stone, p. 87.  Stone (Bion) has many conversions from the Foot Royal of
# Paris to various other linear measurements.
# Robertson, p. 140-141, gives it as 1 English foot = 0.9386 French feet
ParisFootInMeters = StatuteFootInMeters * 144 / 135
# Clarke, p. 67, gives 20.228 in.  Captain Thompson (d'Antoni, 1789) gives
# 20.23457 in., seemingly with better justification.
SardiniaFootInMeters = StatuteFootInMeters * 20.23457 / 12

AvoirdupoisPoundInKilograms = 0.45359237
TroyPoundInKilograms = AvoirdupoisPoundInKilograms * 5760 / 7000
# From Robertson, p. 140-141.
ParisPoundInKilograms = AvoirdupoisPoundInKilograms / 0.926
# Captain Thompson (d'Antoni, 1789) gives 0.82.  Clarke gives 0.81332.
PeidmontPoundInKilograms = AvoirdupoisPoundInKilograms * 0.81332

# The units table is a list of tuples, each of which is ([list of names and
# abbreviations], prefixes allowed, factor to SI, description).  The factor can
# be a single number if the conversion has the same zero-point, or can be a
# pair where the first number is the scale and the second is the offset.  If
# prefixes are allowed, the standard SI prefixes for powers of ten can be added
# to the unit names as needed.
UnitsTable = [
    # Distance (reference is meter)
    (['in', 'inch', 'inches'], False, StatuteFootInMeters / 12,
     'Statute inch (British and American inch)'),
    (['lk', 'link', 'links'], False, 0.66 * StatuteFootInMeters,
     'Link (1/100th of a chain or 1/25 of a rod)'),
    (['ft', 'foot', 'feet'], False, StatuteFootInMeters,
     'Statute foot (British and American foot)'),
    (['yd', 'yard', 'yards', 'yds'], False, 3 * StatuteFootInMeters,
     'Statute yard (British and American yard)'),
    (['m', 'meter', 'meters'], True, 1.0, 'SI meter'),
    (['ch', 'chain', 'chains'], False, 66 * StatuteFootInMeters,
     'Chain (100 links or 66 statute feet)'),
    (['mi', 'mile', 'miles'], False, 5280 * StatuteFootInMeters,
     'Statute mile (British and American mile)'),

    (['ftfr', 'parisfoot', 'frenchfoot', 'parisfeet', 'frenchfeet'], False,
     ParisFootInMeters, 'Paris foot'),
    (['infr', 'parisinch', 'frenchinch', 'parisinches', 'frenchinches'], False,
     ParisFootInMeters / 12, 'Paris foot'),
    (['toise', 'toises', 'frenchfathom', 'frenchfathoms'], False,
     ParisFootInMeters * 6, 'Paris toise (fathom)'),

    (['ftit', 'italianfoot', 'sardiniafoot', 'italianfeet', 'sardiniafeet',
      'pieliprando'], False, SardiniaFootInMeters,
     'Sardinia foot (pie liprando)'),
    (['init', 'italianinch', 'sardiniainch', 'italianinches', 'sardiniainches',
      'oncia', 'oncie'], False, SardiniaFootInMeters / 12,
     'Sardinia inch (oncia)'),
    (['italianline', 'sardinialine', 'italianlines', 'sardinialines', 'punto',
      'punti'], False, SardiniaFootInMeters / 144, 'Sardinia line (punto)'),
    (['italianatomi', 'sardiniaatomi', 'atomi'], False,
     SardiniaFootInMeters / 1728, 'Sardinia atomi (1/12 line or punto)'),
    (['trabucco', 'trabucchi', 'trabucci', 'italianfathom', 'italianfathoms'],
     False, SardiniaFootInMeters * 6, 'Sardinia trabucco (fathom)'),

    # Mass (reference is kg)
    (['gr', 'grain', 'grains'], False, AvoirdupoisPoundInKilograms / 7000,
     'Grain (1/7000th of a avoirdupois pound)'),
    (['g', 'gram', 'grams'], True, 0.001, 'SI grams'),
    (['dr', 'dram', 'drams'], False, AvoirdupoisPoundInKilograms / 256,
     'International avoirdupois dram (1/16 ounce)'),
    (['oz', 'ounce', 'ounces'], False, AvoirdupoisPoundInKilograms / 16,
     'International avoirdupois ounce'),
    (['dwt', 'troypennyweight', 'pennyweight'], False,
     TroyPoundInKilograms / 240, 'Troy pennyweight (24 grains)'),
    (['drt', 'troydram', 'troydrams'], False, TroyPoundInKilograms / 96,
     'Troy dram (1/8 ounce or 60 grains)'),
    (['ozt', 'troyounce', 'troyounces'], False, TroyPoundInKilograms / 12,
     'Troy ounce'),
    (['lb', 'pound', 'pounds', 'lbs'], False, AvoirdupoisPoundInKilograms,
     'International avoirdupois pound'),
    (['lbt', 'troypound', 'troypounds'], False, TroyPoundInKilograms,
     'Troy pound'),
    (['kg', 'kilogram', 'kilograms'], False, 1.0, 'SI kilogram'),

    (['lbfr', 'parispound', 'frenchpound', 'parispounds', 'frenchpounds',
      'livre', 'livres'], False, ParisPoundInKilograms,
     'Paris livre (pound)'),
    (['ozfr', 'parisounce', 'frenchounce', 'parisounces', 'frenchounces'],
     False, ParisPoundInKilograms / 16, 'Paris ounce'),

    (['lbit', 'italianpound', 'piedmontesepound', 'italianpounds',
      'piedmontesepounds', 'libbre'], False, PeidmontPoundInKilograms,
     'Peidmont libbre (pound)'),
    (['ozit', 'italianounce', 'piedmonteseounce', 'italianounces',
      'piedmonteseounces'], False, PeidmontPoundInKilograms / 12,
     'Peidmont once (ounce)'),
    (['italiandenari', 'piedmontesedenari', 'denari'], False,
     PeidmontPoundInKilograms / 12 / 24, 'Peidmont denari (dram)'),

    # Energy (reference is J)
    (['J', 'Joule', 'Joules'], True, 1.0, 'SI Joule (kg*m*m/s/s)'),
    # calorie could be 4.201681 J, 4.184 J (thermochemical cal), 4.204 (4 deg
    # cal), or other values.
    (['cal', 'calorie', 'calories'], True, 4.184, 'gram calorie'),
    (['Cal', 'kcal', 'Calorie', 'Calories'], False, 4184.0,
     'kilogram Calorie'),
    (['ftlb', 'footpound', 'footpounds'], False, 1.355818,
     'Foot-pound'),
    (['ftton', 'footton', 'foottons', 'footlongton', 'footlongtons'], False,
     3037.03232, 'Foot-ton, using the long ton (2240 lb)'),
    (['kilogrammeter', 'kilogrammeters'], False, 9.806650,
     'Kilogram-meter (energy)'),

    # Angle (reference is radian)
    (['deg', 'degree', 'degrees'], False, math.pi / 180, 'Degree (angle)'),
    (['arcmin', 'arcminute', 'arcminutes'], False, math.pi / 180 / 60,
     'Minutes (angle)'),
    (['arcsec', 'arcsecond', 'arcseconds'], False, math.pi / 180 / 60 / 60,
     'Seconds (angle)'),
    (['rad', 'radian', 'radians'], False, 1.0, 'Radian'),
    (['tangent'], False, (lambda x: math.atan(x), lambda x: math.tan(x)),
     'Tangent of angle'),
    (['%slope', 'percentslope'], False, (
     lambda x: math.atan(x * 0.01), lambda x: math.tan(x) * 100),
     'Percent slope'),

    # Time (reference is second)
    (['third', 'thirds'], False, 1.0 / 60, 'Third (time)'),
    (['s', 'sec', 'second', 'seconds'], True, 1.0, 'Second (time)'),
    (['min', 'minute', 'minutes'], False, 60.0, 'Minute (time)'),
    (['h', 'hour', 'hours'], False, 3600.0, 'Hour (time)'),

    # Temperature (reference is K)
    (['F', 'degF'], False, (5.0 / 9.0, 459.67), 'Degree Fahrenheit'),
    (['Ra', 'Rankine'], False, 5.0 / 9.0, 'Rankine (temperature)'),
    (['C', 'degC'], False, (1.0, 273.15), 'Degree Centigrade'),
    (['K', 'Kelvin'], False, 1.0, 'Kelvin (temperature)'),

    # Percent
    (['%', 'percent'], False, 0.01, 'Percent'),

    # Pressure (reference is Pa)
    (['Pa', 'Pascal', 'Pascals'], True, 1.0,
     'SI Pascal (1 N/m/m or 1 kg/m/s/s)'),
    (['bar'], False, 10.0e5, 'Pressure bar (100000 Pa)'),
    (['atm', 'atmosphere', 'atmospheres'], False, 101325.0,
     'Standard atmospheric pressure (101,325 Pa)'),
    (['psi'], False, 689.48, 'Pounds of force per square inch'),
    (['mmHg'], False, 133.322387415, 'Pressure in millimeters of mercury'),
    (['mHg'], True, 133322.387415, 'Pressure in meters of mercury'),
    (['inHg'], False, 3386.388, 'Pressure in inches of mercury'),
    (['initHg'], False, 3386.388 * SardiniaFootInMeters / StatuteFootInMeters,
     'Pressure in Italian inches of mercury'),
    ]


def convert_units(value, to=None, from_units=None):  # noqa - mccabe
    """Convert a value from one set of units to another.  The value is
     specified as (number)[ ]*(units), and the units is any unit
     abbreviation or name combined with '*' and '/' without any spaces.
     Note that unit names NEVER have ., +, -, or numerals in them.
    Enter: value: the value to convert.  If this includes units, from_unit
                  is ignored.  If this does not have units and from_units
                  is also None, it is assumed that this is in SI units.
             to: a string with the units to convert to.  If None, convert to
                 SI units.  If 'string', do not try to convert units.
             from_units: if specified, a string with the units to convert
                         from.  This is ignored if the value includes units.
    Exit:  value: the value in the 'to' units.  If no units are specified,
                  None is returned."""
    remainder = None
    value = str(value).strip()
    if to == 'string':
        return value
    lastpos = None
    for k in xrange(len(value)):
        if value[k] in '0123456789.+-':
            lastpos = k+1
        elif value[k] == 'e' and value[k+1:k+2] in '0123456789.+-':
            lastpos = k+1
        else:
            break
    try:
        units = value[lastpos:].strip()
        value = float(value[:lastpos].strip())
    except Exception:
        return None
    if not units:
        units = from_units
    if units:
        firstpos = None
        for k in xrange(len(units)):
            if units[k] in '0123456789.+-':
                firstpos = k
                break
        if firstpos:
            remainder = units[firstpos:].strip()
            units = units[:k].strip()
    for fromto in ['from', 'to']:
        if fromto == 'to':
            units = to
        if units is None:
            continue
        mode = 'mul'
        lastpos = 0
        for pos in xrange(len(units)):
            if units[pos] in '*/':
                factor = convert_units_factor(units[lastpos:pos])
                if factor is None:
                    return None
                value = convert_units_apply(value, factor, fromto, mode)
                if units[pos] == '/':
                    mode = 'div'
                else:
                    mode = 'mul'
                lastpos = pos+1
        factor = convert_units_factor(units[lastpos:])
        if factor is None:
            return None
        value = convert_units_apply(value, factor, fromto, mode)
    if remainder is not None:
        value += convert_units(remainder, to, from_units)
    return value


def convert_units_apply(value, factor, fromto='from', mode='mul'):
    """Apply a conversion factor to a value.  For plain factors, if ('from'
     and 'mul') or ('to' and 'div'), the value is multipled by the factor,
     otherwise the value is divided by the factor.
    Enter: value: a floating point value to adjust.
           factor: a factor to adjust it by.  This is either a number or a
                   two tuple of (factor, offset).
           fromto: 'from' or 'to'.  See above.
           mode: 'mul' or 'div'.  See above.
    Exit:  value: the converted value."""
    offset = 0
    if isinstance(factor, tuple):
        if callable(factor[0]):
            if (fromto, mode) in (('from', 'mul'), ('to', 'div')):
                return factor[0](value)
            else:
                return factor[1](value)
        (factor, offset) = factor
    if (fromto, mode) in (('from', 'mul'), ('to', 'div')):
        value = (value+offset)*factor
    else:
        value = value/factor-offset
    return value


def convert_units_factor(unitname):
    """Return the factor associated with a specific unit name.
    Enter: unitname: the name of the unit.  It must be in the UnitsTable.
    Exit:  factor: the factor for the unit, or None if not found."""
    for unit in UnitsTable:
        for name in unit[0]:
            if name == unitname:
                return unit[2]
    # prefixes = {
    #     'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12, 'G': 1e9,
    #     'M': 1e6, 'k': 1e3, 'h': 1e2, 'da': 1e1, 'd': 1e-1, 'c': 1e-2,
    #     'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15,
    #     'a': 1e-18, 'z': 1e-21, 'y': 1e-22}
    prefixes = {
        'T': 1e12, 'G': 1e9, 'M': 1e6, 'k': 1e3, 'h': 1e2, 'd': 1e-1,
        'c': 1e-2, 'm': 1e-3, 'u': 1e-6, 'n': 1e-9
    }
    if unitname[:1] in prefixes:
        factor = prefixes[unitname[:1]]
        base = unitname[1:]
        for unit in UnitsTable:
            if unit[1]:
                for name in unit[0]:
                    if name == base:
                        return factor*unit[2]
    sys.stderr.write('Unknown unit "%s"\n' % unitname)
    return None


def list_units(full=False):
    """List all of the units in the units table.  This also checks to make
     sure all unit names are valid and distinct.
    Enter: full: if True, print all alternate names on their own line."""
    units = {}
    for (names, prefix, factor, desc) in UnitsTable:
        for name in names:
            if name in units:
                print 'Duplicate unit: %s' % name
                return
            for k in name:
                if not k.isalpha():
                    print 'Invalid unit name: %s' % name
                    return
            if name == names[0]:
                units[name] = (factor, desc, names[1:])
            elif full == 'full':
                units[name] = (None, 'See %s.' % names[0], [])
    names = units.keys()
    names.sort()
    nlen = max([len(name) for name in names])
    print ('%-'+str(nlen)+'s Description (factor to SI)') % 'Name'
    for name in names:
        desc = units[name][1]
        if len(units[name][2]):
            desc += '  Also called '+', '.join(units[name][2])+'.'
        factor = units[name][0]
        if factor is not None:
            if isinstance(factor, tuple):
                desc += '  '+str(factor)
            else:
                desc += '  (%g)' % factor
        lines = line_break(('%-'+str(nlen)+'s %s') % (name, desc), 79, nlen+2)
        for line in lines:
            print line
