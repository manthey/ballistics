import json
import os

import ballistics


def testFindUnknown():
    state = {
        'final_height': 0,
        'initial_angle': 45.0,
        'charge': 0.0311034768,
        'mass': 11.070488780312502,
        'material': 'brass',
        'range': 229.13035200000002,
        'time_delta': 0.05,
    }
    unknown = 'power_factor'
    result, _points = ballistics.find_unknown(state, unknown)
    assert 407000 < result['power_factor'] < 409000


def testCombinations():
    testDir = os.path.dirname(os.path.realpath(__file__))
    combinations = json.load(open(os.path.join(testDir, 'combinations.json')))
    for entry in combinations:
        args = ['--%s=%s' % (k, v if v is not None else '')
                for k, v in entry['conditions'].items()]
        args.append('--power=?')
        args.append('--time_delta=%g' % max(0.0001, min(
            0.2, entry['time'] * 0.049 if entry['time'] else 100)))
        params, state, _ = ballistics.parse_arguments(args)
        print(args)
        result, _ = ballistics.find_unknown(state, params['unknown'], params.get('unknown_scan'))
        assert 0.99 < result['power_factor'] / entry['power_factor'] < 1.01
