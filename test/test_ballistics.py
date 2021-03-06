import json
import os
import pytest
try:
    import matplotlib
except ImportError:
    matplotlib = None

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
    assert 414000 < result['power_factor'] < 416000


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


def testGetHelp(capsys):
    ballistics.main(['--help'])
    output = capsys.readouterr().out
    assert 'Syntax' in output


def testGetVersion(capsys):
    ballistics.main(['--version'])
    output = capsys.readouterr().out
    assert 'Version:' in output


def testGetMaterials(capsys):
    ballistics.main(['--materials'])
    output = capsys.readouterr().out
    assert 'castiron' in output
    assert 'See castiron' not in output
    ballistics.main(['--materials=full'])
    output = capsys.readouterr().out
    assert 'See castiron' in output


def testGetUnits(capsys):
    ballistics.main(['--units'])
    output = capsys.readouterr().out
    assert 'Joules' in output
    assert 'See cal' not in output
    ballistics.main(['--units=full'])
    output = capsys.readouterr().out
    assert 'See cal' in output


@pytest.mark.skipif(matplotlib is None, reason='matplotlib is required')
def testCdGraph(capsysbinary):
    images = set()
    for method in ['adjusted', 'collins', 'henderson', 'miller', 'morrison']:
        ballistics.main([
            '--cdgraph=w=6,h=4,dpi=100,mnmin=0,mnmax=2.5,mnint=0.25,method=%s,'
            'remax=2e7,oor=1,out=-' % method])
        output = capsysbinary.readouterr().out
        assert output[:4] == b'\x89PNG'
        assert output not in images
        images.add(output)
