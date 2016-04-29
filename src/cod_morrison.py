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


def coefficient_of_drag_morrison(state, only_in_range=False):
    """Calculate the coefficient of drag using the equation provided from
     http://www.chem.mtu.edu/~fmorriso/DataCorrelationForSphereDrag2013.pdf
    Enter: state: a dictionary of the current state.  Includes Reynolds and
                  mach numbers.
           only_in_range: if True, return None if the values are outside of
                          what we can interpolate.
    Exit:  cd: the coefficient of drag."""
    Re = state['drag_data']['Re']
    cd = (24.0 / Re +
          (2.6 * (Re / 5.0)) / (1 + (Re / 5.0) ** 1.52) +
          (0.411 * (Re / 263000) ** -7.94) / (1 + (Re / 263000) ** -8.00) +
          (Re ** 0.80) / 461000)
    state['drag_data']['cd'] = cd
    state['drag_data']['in_range'] = (Re < 1.0e6)
    if not state['drag_data']['in_range'] and only_in_range:
        return None
    return cd
