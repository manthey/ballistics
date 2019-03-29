import copy
import concurrent.futures
import json
import math
import os
import random
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir)))

import ballistics  # noqa
from ballistics import cod_miller  # noqa


def calc_error(groups):
    sum2err = 0
    for entry in groups.values():
        avg = sum(val for val in entry['pf']) / len(entry['pf'])
        err2 = sum(math.log10(val / avg)**2 for val in entry['pf']) / len(entry['pf'])
        sum2err += err2
    err = 10 ** ((sum2err / len(groups)) ** 0.5) - 1
    return err


def recalc_case(case, newTable):
    cod_miller.MnReCdDataTable[:] = [
        (e1[0], tuple(tuple(e2) for e2 in e1[1]), e1[2]) for e1 in newTable]
    cod_miller.ExtendedMnReCdDataTable[:] = []
    args = ['--power=?'] + case
    params, state, help = ballistics.parse_arguments(args)
    newstate, points = ballistics.find_unknown(
        state, params['unknown'], params.get('unknown_scan'))
    return newstate['power_factor']


def recalc_groups_pool(groups, newTable):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for groupkey in sorted(groups):
            entry = groups[groupkey]
            for idx, case in enumerate(entry['cases']):
                future = executor.submit(recalc_case, case, newTable)
                future._info = (entry, idx)
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            entry, idx = future._info
            power_factor = future.result()
            entry['pf'][idx] = power_factor
            sys.stdout.write('%s %d %3.1f %3.1f %3.1f  \r' % (
                entry['key'], idx, power_factor,
                entry['entries'][idx]['power_factor'],
                power_factor - entry['entries'][idx]['power_factor']))
            sys.stdout.flush()


def recalc_groups(groups, newTable):
    cod_miller.MnReCdDataTable[:] = [
        (e1[0], tuple(tuple(e2) for e2 in e1[1]), e1[2]) for e1 in newTable]
    cod_miller.ExtendedMnReCdDataTable[:] = []
    for groupkey in sorted(groups):
        entry = groups[groupkey]
        for idx, case in enumerate(entry['cases']):
            args = ['--power=?'] + case
            params, state, help = ballistics.parse_arguments(args)
            newstate, points = ballistics.find_unknown(
                state, params['unknown'], params.get('unknown_scan'))
            entry['pf'][idx] = newstate['power_factor']
            sys.stdout.write('%s %d %3.1f %3.1f %3.1f  \r' % (
                entry['key'], idx, newstate['power_factor'],
                entry['entries'][idx]['power_factor'],
                newstate['power_factor'] - entry['entries'][idx]['power_factor']))
            sys.stdout.flush()
            # print('\n%r' % case)


def main(opts):
    opts = opts or {}
    pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    fulldata = json.load(open(os.path.join(pardir, 'client', 'static', 'totallist.json')))
    groups = {}
    for entry in fulldata:
        if not entry.get('given_group') or entry.get('technique') in {
                'time', 'theory', 'gun_pendulum'}:
            continue
        key = '%s:%s' % (entry['key'], entry['given_group'])
        groups.setdefault(key, {'key': key, 'entries': [], 'cases': [], 'pf': []})
        case = ['--%s=%s' % (k[6:], entry[k])
                for k in entry if k.startswith('given_') and
                k not in {'given_group', 'given_technique', 'given_date'} and
                not k.endswith('_note')]
        groups[key]['entries'].append(entry)
        groups[key]['cases'].append(case)
        groups[key]['pf'].append(entry['power_factor'])
    for key in list(groups):
        if len(groups[key]['cases']) < 2:
            del groups[key]
    print(len(groups), sum(len(entry['cases']) for entry in groups.values()))
    origMnReCdDataTable = copy.deepcopy(cod_miller.MnReCdDataTable)
    bestTable = [[mn, [list(entry) for entry in entries], crit]
                 for mn, entries, crit in origMnReCdDataTable]
    bestError = calc_error(groups)
    print('err %10.8f param %d' % (bestError, sum(len(entries) for mn, entries, crit in bestTable)))
    # recalc_groups(groups, bestTable)
    src = opts.get('src', opts['dest'])
    if os.path.exists(src):
        print('read %s' % src)
        newTable = json.load(open(src))
        recalc_groups_pool(groups, newTable)
        newError = calc_error(groups)
        if newError < bestError:
            bestError = newError
            bestTable = newTable
        print('err %10.8f param %d' % (
            bestError, sum(len(entries) for mn, entries, crit in bestTable)))
    while True:
        newTable = copy.deepcopy(bestTable)
        couldAdjust = [(mn, entry) for mn, entries, crit in newTable for entry in entries]
        entry = random.choice(couldAdjust)
        adjustment = random.random() ** 2 * 0.01 * (-1 if random.random() >= 0.5 else 1)
        print('adjusting %6.4f %r' % (adjustment, entry))
        entry[1][1] += adjustment
        recalc_groups_pool(groups, newTable)
        newError = calc_error(groups)
        print('new %10.8f best %10.8f  ' % (newError, bestError))
        if newError < bestError:
            bestError = newError
            bestTable = newTable
        json.dump(bestTable, open(opts['dest'], 'w'))


if __name__ == '__main__':
    help = False
    opts = {'verbose': 0}
    for arg in sys.argv[1:]:
        if arg.startswith('--dest='):
            opts['dest'] = arg.split('=', 1)[1]
        elif arg.startswith('--src='):
            opts['src'] = arg.split('=', 1)[1]
        elif arg == '-v':
            opts['verbose'] += 1
        elif arg.startswith('-'):
            help = True
        elif 'src' not in opts:
            opts['src'] = arg
        elif 'dest' not in opts:
            opts['dest'] = arg
        else:
            help = True
    opts.setdefault('dest', 'miller_table.json')
    main(opts)
