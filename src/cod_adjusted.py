#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 David Manthey
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

import json
import math
import os

import cod_collins


Resolution = 10


MnReBaseTable = {}

Adjustments = None
MnReAdjustments = {}


def cd_from_mn_re(mn, re):
    if Adjustments is None:
        load_adjustments()
    if mn not in MnReBaseTable:
        MnReBaseTable[mn] = {}
    if re not in MnReBaseTable[mn]:
        MnReBaseTable[mn][re] = cod_collins.coefficient_of_drag_collins(
            {'drag_data': {'Mn': float(mn) / Resolution,
                           'Re': math.pow(10, float(re) / Resolution)}})
    return MnReBaseTable[mn][re] + MnReAdjustments.get(mn, {}).get(re, 0)


def coefficient_of_drag_adjusted(state, only_in_range=False):
    """Calculate the coefficient of drag.  The drag is calculated by a bilinear
     interpolation from values spaced evenly through Mach values and log10
     Reynolds numbers.  These values were initially computed from cod_collins,
     but some values have been adjusted based on real-world data.
    Enter: state: a dictionary of the current state.  Includes Reynolds and
                  mach numbers.
           only_in_range: if True, return None if the values are outside of
                          what we can interpolate.
    Exit:  Cd: the coefficient of drag."""
    Re = state['drag_data']['Re']
    Mn = state['drag_data']['Mn']
    re = math.log10(Re) * Resolution
    rel = math.floor(re)
    reh = math.ceil(re)
    ref = (re - rel) / (reh - rel) if rel != reh else 1
    mn = Mn * Resolution
    mnl = math.floor(mn)
    mnh = math.ceil(mn)
    mnf = (mn - mnl) / (mnh - mnl) if mnl != mnh else 1
    Cd = ((cd_from_mn_re(mnl, rel) * (1 - mnf) +
           cd_from_mn_re(mnh, rel) * mnf) * (1 - ref) +
          (cd_from_mn_re(mnl, reh) * (1 - mnf) +
           cd_from_mn_re(mnh, reh) * mnf) * ref)
    return Cd


def load_adjustments():
    global Adjustments, MnReAdjustments

    if Adjustments is not None:
        return
    Adjustments = {}
    path = os.path.splitext(os.path.abspath(__file__))[0]+'.json'
    if os.path.exists(path):
        Adjustments = json.load(open(path))
        table = {}
        for mn in Adjustments['table']:
            table[int(mn)] = {}
            for re in Adjustments['table'][mn]:
                table[int(mn)][int(re)] = Adjustments['table'][mn][re]
        MnReAdjustments = table
