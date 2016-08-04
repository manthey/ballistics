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
Materials definitions and functions.
"""

import math
import sys

from formattext import line_break
from units import convert_units


# The materials table is a list of tuples, each of which is ([list of names and
# abbreviations], typical density in kg/m^3, minimum density, maximum density,
# description).  Some data was taken from http://www.engineeringtoolbox.com/
# metal-alloys-densities-d_50.html
#  This could be expanded if necessary.  Davies, 1748 gives a greater range for
# each material's density as well as values for steel, copper, and others.
MaterialsTable = [
    # Brass - Robertson: 8104, Natco: 8441
    (['brass'], 8520, 8100, 8700, 'Brass'),
    # Copper
    (['copper', 'cuivre'], 8940, 8800, 8950, 'Copper'),
    # Cast Iron - Robertson: 7135, Natco: 7208
    (['castiron', 'cast', 'iron'], 7450, 6800, 7800, 'Cast iron'),
    # Lead - Robertson: 11313, Natco: 11366
    (['lead'], 11340, 11310, 11370, 'Lead'),
    ]


def determine_material(state, verbosity=0):
    """Determine the material, diameter, or mass, provided the other two
     are known.  If all three are known or less than two are known, this
     does nothing.  If material is given, but not material_density,
     material_density is taken from the Materials table.  If mass and diam are
     provided, projectile_density is computed and the closest material is
     listed as a match (though it may not be).
    Enter: state: a dictionary of the current state.  Possibly modified.
           verbosity: if high enough, log additional information.
    Exit:  state: the state with the third value added, if appropriate."""
    if ('material' in state and 'material_density' not in state and
            ('diam' not in state or 'mass' not in state) and
            ('diam' in state or 'mass' in state)):
        # determine mass or diameter
        for (names, dens, mindens, maxdens, desc) in MaterialsTable:
            for name in names:
                if state['material'] == name:
                    state['material_density'] = dens
                    break
        if 'material_density' not in state:
            if verbosity >= 2:
                sys.stderr.write('Cannot determine material density.\n')
            return state
    if ('material_density' in state and
            ('diam' not in state or 'mass' not in state) and
            ('diam' in state or 'mass' in state)):
        if 'diam' in state:
            state['mass'] = (4./3 * math.pi * (state['diam']*0.5)**3 *
                             state['material_density'])
        else:
            state['diam'] = 2 * (float(state['mass']) / (
                state['material_density'] * 4./3 * math.pi))**(1./3)
    if 'material' not in state and 'diam' in state and 'mass' in state:
        # determine material
        state['projectile_density'] = float(state['mass'])/(
            4./3 * math.pi * (state['diam']*0.5)**3)
        density_delta = None
        for (names, dens, mindens, maxdens, desc) in MaterialsTable:
            if (state['projectile_density'] >= mindens and
                    state['projectile_density'] <= maxdens):
                delta = abs(state['projectile_density']-dens)
                if density_delta is None or delta < density_delta:
                    density_delta = delta
                    state['material'] = names[0]
    return state


def list_materials(full=False):
    """List all of the materials in the materials table.  This also checks
     to make sure all material names are valid and distinct.
    Enter: full: if True, print all alternate names on their own line."""
    materials = {}
    for (names, dens, mindens, maxdens, desc) in MaterialsTable:
        for name in names:
            if name in materials:
                print 'Duplicate material: %s' % name
                return
            if name == names[0]:
                materials[name] = (dens, desc, names[1:])
            elif full == 'full':
                materials[name] = (None, 'See %s.' % names[0], [])
    names = materials.keys()
    names.sort()
    nlen = max([len(name) for name in names])
    print ('%-'+str(nlen)+'s Description (typical density)') % 'Name'
    for name in names:
        desc = materials[name][1]
        if len(materials[name][2]):
            desc += '  Also called '+', '.join(materials[name][2])+'.'
        dens = materials[name][0]
        if dens is not None:
            desc += '  (%1.0f kg/m^3, %1.0f lb/ft^3)' % (
                dens, convert_units(dens, 'lb/ft/ft/ft'))
        lines = line_break(('%-'+str(nlen)+'s %s') % (name, desc), 79, nlen+2)
        for line in lines:
            print line
