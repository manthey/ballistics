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

"""
Unit conversion functions and units definitions.
"""

import math
import sys

from .formattext import line_break

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
# Smith, 1779, entry on Foot, gives 1 French foot = 1.068 English feet
ParisFootInMeters = StatuteFootInMeters * 144 / 135
# Clarke, p. 67, gives 20.228 in.  Captain Thompson (d'Antoni, 1789) gives
# 20.23457 in., seemingly with better justification.
SardiniaFootInMeters = StatuteFootInMeters * 20.23457 / 12
# Clarke, p. 62, gives 12.357 in = 1 Prussian foot
# Stone gives 11 Paris inches 7 Paris lines = 1 Rhine foot
# Smith, 1779 gives 1 Rhine foot = 12 1/3 in
RhineFootInMeters = StatuteFootInMeters * 12.357 / 12

AvoirdupoisPoundInKilograms = 0.45359237
TroyPoundInKilograms = AvoirdupoisPoundInKilograms * 5760 / 7000
# Robertson, p. 140-141, gives 1 lb English = 0.926 lb French
# Smith, 1779, entry on Weights, gives 100 lb English = 91 lb 8 oz French
ParisPoundInKilograms = AvoirdupoisPoundInKilograms / 0.926
# Captain Thompson (d'Antoni, 1789) gives 0.82.  Clarke gives 0.81332.
PeidmontPoundInKilograms = AvoirdupoisPoundInKilograms * 0.81332
# Clarke, p. 62, gives 1 pfund = 1.03118 lb English
RhinePoundInKilograms = AvoirdupoisPoundInKilograms * 1.03118

SIGravity = 9.806650

# Each entry in the units table contains:
#   names: a list of names and abbreviations
#   prefix: (optional) True if standard prefixes are allowed, in which case the
#     standard SI prefixes for powers of ten can be added to the unit names as
#     needed.
#   value: factor to SI.  The value can be a single number if the conversion
#     has the same zero-point, or can be a two-tuple where the first number is
#     the scale and the second is the offset, or can be a two-tuple of
#     functions that convert to and from the standard.
#   desc: description.
UnitsTable = [{
    # Distance (reference is meter)
    'names': ['m', 'meter', 'meters'],
    'prefix': True,
    'value': 1.0,
    'desc': 'SI meter',
}, {
    # -- Statute distances
    'names': ['in', 'inch', 'inches'],
    'value': StatuteFootInMeters / 12,
    'desc': 'Statute inch (British and American inch)',
}, {
    'names': ['lk', 'link', 'links'],
    'value': 0.66 * StatuteFootInMeters,
    'desc': 'Link (1/100th of a chain or 1/25 of a rod)',
}, {
    'names': ['ft', 'foot', 'feet'],
    'value': StatuteFootInMeters,
    'desc': 'Statute foot (British and American foot)',
}, {
    'names': ['yd', 'yard', 'yards', 'yds'],
    'value': 3 * StatuteFootInMeters,
    'desc': 'Statute yard (British and American yard)',
}, {
    'names': ['ch', 'chain', 'chains'],
    'value': 66 * StatuteFootInMeters,
    'desc': 'Chain (100 links or 66 statute feet)',
}, {
    'names': ['mi', 'mile', 'miles'],
    'value': 5280 * StatuteFootInMeters,
    'desc': 'Statute mile (British and American mile)',
}, {
    'names': ['singlepace', 'singlepaces'],
    'value': 2.5 * StatuteFootInMeters,
    'desc': 'Common pace (2.5 feet)',
}, {
    'names': ['pace', 'paces', 'doublepace', 'doublepaces'],
    'value': 5 * StatuteFootInMeters,
    'desc': 'Geometrical pace (5 feet)',
}, {
    # -- Paris distances
    'names': ['ftfr', 'parisfoot', 'frenchfoot', 'parisfeet', 'frenchfeet'],
    'value': ParisFootInMeters,
    'desc': 'Paris foot',
}, {
    'names': ['infr', 'parisinch', 'frenchinch', 'parisinches', 'frenchinches', 'pouce', 'pouces'],
    'value': ParisFootInMeters / 12,
    'desc': 'Paris inch',
}, {
    'names': ['linefr', 'parisline', 'frenchline', 'parislines', 'frenchlines', 'ligne', 'lignes'],
    'value': ParisFootInMeters / 12 / 12,
    'desc': 'Paris line',
}, {
    'names': ['ptfr', 'pointfr', 'parispoint', 'frenchpoint', 'parispoints', 'frenchpoints'],
    'value': ParisFootInMeters / 12 / 12 / 12,
    'desc': 'Paris point',
}, {
    'names': ['toise', 'toises', 'frenchfathom', 'frenchfathoms'],
    'value': ParisFootInMeters * 6,
    'desc': 'Paris toise (fathom)',
}, {
    # -- Italian distances
    'names': ['ftit', 'italianfoot', 'sardiniafoot', 'italianfeet', 'sardiniafeet', 'pieliprando'],
    'value': SardiniaFootInMeters,
    'desc': 'Sardinia foot (pie liprando)',
}, {
    'names': ['init', 'italianinch', 'sardiniainch', 'italianinches',
              'sardiniainches', 'oncia', 'oncie'],
    'value': SardiniaFootInMeters / 12,
    'desc': 'Sardinia inch (oncia)',
}, {
    'names': ['italianline', 'sardinialine', 'italianlines', 'sardinialines', 'punto', 'punti'],
    'value': SardiniaFootInMeters / 144,
    'desc': 'Sardinia line (punto)',
}, {
    'names': ['italianatomi', 'sardiniaatomi', 'atomi'],
    'value': SardiniaFootInMeters / 1728,
    'desc': 'Sardinia atomi (1/12 line or punto)',
}, {
    'names': ['trabucco', 'trabucchi', 'trabucci', 'italianfathom', 'italianfathoms'],
    'value': SardiniaFootInMeters * 6,
    'desc': 'Sardinia trabucco (fathom)',
}, {

    # Mass (reference is kg)
    'names': ['g', 'gram', 'grams'],
    'prefix': True,
    'value': 0.001,
    'desc': 'SI grams',
}, {
    'names': ['kg', 'kilogram', 'kilograms'],
    'value': 1.0,
    'desc': 'SI kilogram',
}, {
    'names': ['tonne', ],
    'value': 1000.0,
    'desc': 'SI megagram',
}, {
    # -- Avoirdupois
    'names': ['gr', 'grain', 'grains'],
    'value': AvoirdupoisPoundInKilograms / 7000,
    'desc': 'Grain (1/7000th of a avoirdupois pound)',
}, {
    'names': ['dr', 'dram', 'drams'],
    'value': AvoirdupoisPoundInKilograms / 256,
    'desc': 'International avoirdupois dram (1/16 ounce)',
}, {
    'names': ['oz', 'ounce', 'ounces'],
    'value': AvoirdupoisPoundInKilograms / 16,
    'desc': 'International avoirdupois ounce',
}, {
    'names': ['lb', 'pound', 'pounds', 'lbs'],
    'value': AvoirdupoisPoundInKilograms,
    'desc': 'International avoirdupois pound',
}, {
    'names': ['qtr', 'quarterhundredweight', 'qtrs', 'quarterhundredweights'],
    'value': AvoirdupoisPoundInKilograms * 28,
    'desc': 'Hundredweight (112 avoirdupois pounds)',
}, {
    'names': ['cwt', 'hundredweight', 'cwts', 'hundredweights'],
    'value': AvoirdupoisPoundInKilograms * 112,
    'desc': 'Hundredweight (112 avoirdupois pounds)',
}, {
    # -- Troy
    'names': ['dwt', 'troypennyweight', 'pennyweight'],
    'value': TroyPoundInKilograms / 240,
    'desc': 'Troy pennyweight (24 grains)',
}, {
    'names': ['drt', 'troydram', 'troydrams'],
    'value': TroyPoundInKilograms / 96,
    'desc': 'Troy dram (1/8 ounce or 60 grains)',
}, {
    'names': ['ozt', 'troyounce', 'troyounces'],
    'value': TroyPoundInKilograms / 12,
    'desc': 'Troy ounce',
}, {
    'names': ['lbt', 'troypound', 'troypounds'],
    'value': TroyPoundInKilograms,
    'desc': 'Troy pound',
}, {
    # -- Paris
    'names': ['lbfr', 'parispound', 'frenchpound', 'parispounds',
              'frenchpounds', 'livre', 'livres'],
    'value': ParisPoundInKilograms,
    'desc': 'Paris livre (pound)',
}, {
    'names': ['ozfr', 'parisounce', 'frenchounce', 'parisounces', 'frenchounces'],
    'value': ParisPoundInKilograms / 16,
    'desc': 'Paris ounce',
}, {
    # -- Italian
    'names': ['lbit', 'italianpound', 'piedmontesepound', 'italianpounds',
              'piedmontesepounds', 'libbre'],
    'value': PeidmontPoundInKilograms,
    'desc': 'Peidmont libbre (pound)',
}, {
    'names': ['ozit', 'italianounce', 'piedmonteseounce', 'italianounces', 'piedmonteseounces'],
    'value': PeidmontPoundInKilograms / 12,
    'desc': 'Peidmont once (ounce)',
}, {
    'names': ['italiandenari', 'piedmontesedenari', 'denari'],
    'value': PeidmontPoundInKilograms / 12 / 24,
    'desc': 'Peidmont denari (dram)',
}, {

    # Energy (reference is J)
    'names': ['J', 'Joule', 'Joules'],
    'prefix': True,
    'value': 1.0,
    'desc': 'SI Joule (kg*m*m/s/s)',
}, {
    # calorie could be 4.201681 J, 4.184 J (thermochemical cal), 4.204 (4 deg
    # cal), or other values.
    'names': ['cal', 'calorie', 'calories'],
    'prefix': True,
    'value': 4.184,
    'desc': 'gram calorie',
}, {
    'names': ['Cal', 'kcal', 'Calorie', 'Calories'],
    'value': 4184.0,
    'desc': 'kilogram Calorie',
}, {
    'names': ['kilogrammeter', 'kilogrammeters'],
    'value': SIGravity,
    'desc': 'Kilogram(force)-meter (energy)',
}, {
    'names': ['tonnemeter', 'tonnemeters'],
    'value': 1000.0 * SIGravity,
    'desc': 'Megagram(force)-meter (energy)',
}, {
    # -- Statute
    'names': ['ftlb', 'footpound', 'footpounds'],
    'value': StatuteFootInMeters * SIGravity * AvoirdupoisPoundInKilograms,
    'desc': 'Foot-pound',
}, {
    'names': ['ftton', 'footton', 'foottons', 'footlongton', 'footlongtons'],
    'value': StatuteFootInMeters * SIGravity * AvoirdupoisPoundInKilograms * 2240,
    'desc': 'Foot-ton, using the long ton (2240 lb)',
}, {

    # Force (reference is N)
    'names': ['N', 'Newton', 'Newtons'],
    'prefix': True,
    'value': 1.0,
    'desc': 'SI Newton (kg*m/s/s)',
}, {
    'names': ['gf', 'gramforce', 'gramsforce', 'pond', 'ponds'],
    'prefix': True,
    'value': 0.001 * SIGravity,
    'desc': 'Grams of force',
}, {
    'names': ['kgf', 'kp', 'kilogramforce', 'kilogramsforce', 'kilopond', 'kiloponds'],
    'value': SIGravity,
    'desc': 'Kilograms of force (kiloponds)',
}, {
    'names': ['Mgf', 'Mp', 'tonneforce', 'tonnesforce', 'megapond', 'megaponds'],
    'value': 1000.0 * SIGravity,
    'desc': 'Megagrams of force (megaponds)',
}, {
    # -- Avoirdupois
    'names': ['lbf', 'poundforce', 'poundsforce'],
    'value': AvoirdupoisPoundInKilograms * SIGravity,
    'desc': 'Pounds of force',
}, {
    'names': ['pdl', 'poundal', 'poundals'],
    'value': AvoirdupoisPoundInKilograms * StatuteFootInMeters,
    'desc': 'Poundals of force (lb*ft/s/s)',

}, {
    # Angle (reference is radian)
    'names': ['rad', 'radian', 'radians'],
    'value': 1.0,
    'desc': 'Radian',
}, {
    'names': ['deg', 'degree', 'degrees'],
    'value': math.pi / 180,
    'desc': 'Degree (angle)',
}, {
    'names': ['arcmin', 'arcminute', 'arcminutes'],
    'value': math.pi / 180 / 60,
    'desc': 'Minutes (angle)',
}, {
    'names': ['arcsec', 'arcsecond', 'arcseconds'],
    'value': math.pi / 180 / 60 / 60,
    'desc': 'Seconds (angle)',
}, {
    'names': ['tangent'],
    'value': (lambda x: math.atan(x), lambda x: math.tan(x)),
    'desc': 'Tangent of angle',
}, {
    'names': ['%slope', 'percentslope'],
    'value': (lambda x: math.atan(x * 0.01), lambda x: math.tan(x) * 100),
    'desc': 'Percent slope',
}, {
    'names': ['grad', 'gradian', 'gradians', 'gon', 'degreescentesimaux', 'degcent'],
    'value': math.pi / 200,
    'desc': 'Gradian (gon)',
}, {
    'names': ['quadpt', 'quadrantpoint', 'quadrantpoints'],
    'value': math.pi / 24,
    'desc': 'Gunners quadrant point (12 points in a quarter circle)',
}, {
    # Time (reference is second)

    'names': ['s', 'sec', 'second', 'seconds'],
    'prefix': True,
    'value': 1.0,
    'desc': 'Second (time)',
}, {
    'names': ['third', 'thirds'],
    'value': 1.0 / 60,
    'desc': 'Third (time)',
}, {
    'names': ['min', 'minute', 'minutes'],
    'value': 60.0,
    'desc': 'Minute (time)',
}, {
    'names': ['h', 'hour', 'hours'],
    'value': 3600.0,
    'desc': 'Hour (time)',
}, {

    # Temperature (reference is K)
    'names': ['K', 'Kelvin'],
    'value': 1.0,
    'desc': 'Kelvin (temperature)',
}, {
    'names': ['C', 'degC'],
    'value': (1.0, 273.15),
    'desc': 'Degree Centigrade',
}, {
    'names': ['F', 'degF'],
    'value': (5.0 / 9.0, 459.67),
    'desc': 'Degree Fahrenheit',
}, {
    'names': ['Ra', 'Rankine'],
    'value': 5.0 / 9.0,
    'desc': 'Rankine (temperature)',
}, {

    # Percent
    'names': ['%', 'percent'],
    'value': 0.01,
    'desc': 'Percent',
}, {

    # Pressure (reference is Pa)
    'names': ['Pa', 'Pascal', 'Pascals'],
    'prefix': True,
    'value': 1.0,
    'desc': 'SI Pascal (1 N/m/m or 1 kg/m/s/s)',
}, {
    'names': ['bar'],
    'value': 1.0e5,
    'desc': 'Pressure bar (100000 Pa)',
}, {
    'names': ['atm', 'atmosphere', 'atmospheres'],
    'value': 101325.0,
    'desc': 'Standard atmospheric pressure (101,325 Pa)',
}, {
    'names': ['psi'],
    'value': 689.48,
    'desc': 'Pounds of force per square inch',
}, {
    'names': ['mmHg'],
    'value': 133.322387415,
    'desc': 'Pressure in millimeters of mercury',
}, {
    'names': ['mHg'],
    'prefix': True,
    'value': 133322.387415,
    'desc': 'Pressure in meters of mercury',
}, {
    'names': ['inHg'],
    'value': 3386.388,
    'desc': 'Pressure in inches of mercury',
}, {
    'names': ['initHg'],
    'value': 3386.388 * SardiniaFootInMeters / StatuteFootInMeters,
    'desc': 'Pressure in Italian inches of mercury',
}]


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
    for k in range(len(value)):
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
        for k in range(len(units)):
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
        for pos in range(len(units)):
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
    """
    Apply a conversion factor to a value.  For plain factors, if ('from' and
    'mul') or ('to' and 'div'), the value is multipled by the factor,
    otherwise the value is divided by the factor.

    Enter: value: a floating point value to adjust.
           factor: a factor to adjust it by.  This is either a number or a
                   two tuple of (factor, offset).
           fromto: 'from' or 'to'.  See above.
           mode: 'mul' or 'div'.  See above.
    Exit:  value: the converted value.
    """
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
    """
    Return the factor associated with a specific unit name.

    Enter: unitname: the name of the unit.  It must be in the UnitsTable.
    Exit:  factor: the factor for the unit, or None if not found.
    """
    for unit in UnitsTable:
        for name in unit['names']:
            if name == unitname:
                return unit['value']
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
            if unit.get('prefix'):
                for name in unit['names']:
                    if name == base:
                        return factor*unit['value']
    sys.stderr.write('Unknown unit "%s"\n' % unitname)
    return None


def list_units(full=False):
    """
    List all of the units in the units table.  This also checks to make sure
    all unit names are valid and distinct.

    Enter: full: if True, print all alternate names on their own line.
    """
    units = {}
    for unit in UnitsTable:
        for name in unit['names']:
            if name in units:
                print('Duplicate unit: %s' % name)
                return
            for k in name:
                if not k.isalpha() and k != '%':
                    print('Invalid unit name: %s' % name)
                    return
            if name == unit['names'][0]:
                units[name] = (unit['value'], unit['desc'], unit['names'][1:])
            elif full == 'full':
                units[name] = (None, 'See %s.' % unit['names'][0], [])
    names = list(units.keys())
    names.sort()
    nlen = max([len(name) for name in names])
    print(('%-'+str(nlen)+'s Description (factor to SI)') % 'Name')
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
            print(line)
