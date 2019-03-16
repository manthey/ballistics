"""
This compares force from drag on a 2 inch projectile at a variety of
velocities using a variety of formulas.
"""

import math
import sys

import ballistics

Hutton = {  # Hutton, 1812, Vol. III, p. 318
    5: 0.006,
    10: 0.026,
    15: 0.058,
    20: 0.103,
    25: 0.163,
    30: 0.237,
    40: 0.427,
    50: 0.676,
    100: 2.78,
    200: 11.34,
    300: 25.8,
    400: 46.5,
    500: 74.4,
    600: 110.4,
    700: 156.0,
    800: 212.0,
    900: 280.3,
    1000: 362.1,
    1100: 456.9,
    1200: 564.4,
    1300: 683.3,
    1400: 811.5,
    1500: 947.1,
    1600: 1086.9,
    1700: 1228.4,
    1800: 1368.6,
    1900: 1505.7,
    2000: 1637.8,
}

methods = ['hutton', 'miller', 'collins', 'henderson', 'morrison',
           'adjusted']
results = {}
for vel in Hutton:
    results[vel] = {'hutton': Hutton[vel]}
for method in methods[1:]:
    for vel in sorted(Hutton):
        state = {
            'vy': 0,
            'vx': ballistics.convert_units('%d ft/s' % vel),
            'diam': ballistics.convert_units('2 in'),
            'material': 'iron',
            'settings': {'drag_method': method},
        }

        ballistics.determine_material(state)
        acc = ballistics.acceleration_from_drag(state)[0]

        accgrav = -ballistics.acceleration_from_gravity(state)
        kgforce = state['mass'] * acc / accgrav

        ozforce = ballistics.convert_units(kgforce, to='oz')
        results[vel][method] = ozforce
        results[vel]['Mn'] = state['drag_data']['Mn']
        results[vel]['Re'] = state['drag_data']['Re']
sys.stdout.write('Velocity ')
for method in methods:
    sys.stdout.write(' %9s' % method.capitalize()[:9])
sys.stdout.write('      Mn  ^Re\n')
for vel in sorted(Hutton):
    sys.stdout.write('%4d ft/s' % vel)
    for method in methods:
        sys.stdout.write('  %8.3f' % results[vel][method])
    sys.stdout.write(' ozf %4.2f %3.1f\n' % (
        results[vel]['Mn'], math.log10(results[vel]['Re'])))
