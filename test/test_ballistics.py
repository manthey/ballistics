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
