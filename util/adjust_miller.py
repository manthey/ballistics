import copy
import concurrent.futures
import json
import math
import os
import psutil
import random
import sys
import time

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
    cod_miller.replace_table(newTable)
    args = ['--power=?'] + case
    params, state, help = ballistics.parse_arguments(args)
    newstate, points = ballistics.find_unknown(
        state, params['unknown'], params.get('unknown_scan'))
    return newstate['power_factor']


def recalc_groups_pool(groups, newTable):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        priorityLevel = (psutil.BELOW_NORMAL_PRIORITY_CLASS
                         if sys.platform == 'win32' else 10)
        parent = psutil.Process()
        parent.nice(priorityLevel)
        for child in parent.children():
            child.nice(priorityLevel)

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
    cod_miller.replace_table(newTable)
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


def main(opts):  # noqa
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
        if 'time' in entry and opts.get('recalc'):
            case = ['--time_delta=%f' % (min(0.2, entry['time'] / 25))] + case
        groups[key]['entries'].append(entry)
        groups[key]['cases'].append(case)
        groups[key]['pf'].append(entry['power_factor'])
    for key in list(groups):
        if len(groups[key]['cases']) < 2:
            del groups[key]
    print(len(groups), sum(len(entry['cases']) for entry in groups.values()))
    # bestTable = cod_miller.table_as_array()
    # # extend table to 1e9
    # for _mn, entries, _crit in bestTable:
    #     if entries[-1][0] == 1e7:
    #         entries.extend([[1e8, entries[-1][1]], [1e9, entries[-1][1]]])
    cod_miller.extend_drag_table()
    bestTable = [[mn, [[10**entry[0], entry[1]] for entry in entries
                       if not mn or entry[0] >= 3], crit]
                 for mn, entries, crit in cod_miller.ExtendedMnLogReCdDataTable]
    bestError = calc_error(groups)
    print('err %10.8f param %d' % (bestError, sum(len(entries) for mn, entries, crit in bestTable)))
    if opts.get('recalc'):
        starttime = time.time()
        recalc_groups_pool(groups, bestTable)
        bestError = calc_error(groups)
        print('err %10.8f param %d %3.1fs  ' % (
            bestError, sum(len(entries) for mn, entries, crit in bestTable),
            time.time() - starttime))
    minErrorDelta = 1e-7
    src = opts.get('src', opts['dest'])
    if os.path.exists(src):
        print('read %s' % src)
        newTable = json.load(open(src))
        recalc_groups_pool(groups, newTable)
        newError = calc_error(groups)
        if newError < bestError - minErrorDelta:
            bestError = newError
            bestTable = newTable
        print('err %10.8f param %d' % (
            bestError, sum(len(entries) for mn, entries, crit in bestTable)))
    adjustCount = sum([len(entries) for mn, entries, crit in bestTable])
    loopBestError = None
    maxmag = opts.get('maxmag', 0.0064)
    minmag = opts.get('minmag', 0.0001)
    while loopBestError is None or bestError < loopBestError:
        loopBestError = bestError
        mag = maxmag
        while mag >= minmag or mag == maxmag:
            for pos in range(adjustCount):
                for dir in (-1, 1):
                    starttime = time.time()
                    newTable = copy.deepcopy(bestTable)
                    couldAdjust = [(mn, entry) for mn, entries, crit
                                   in newTable for entry in entries][::-1]
                    if opts.get('random'):
                        entry = random.choice(couldAdjust)
                        adjustment = random.random() ** 2 * 0.01 * (
                            -1 if random.random() >= 0.5 else 1)
                    else:
                        entry = couldAdjust[pos]
                        adjustment = mag * dir
                    print('adjusting %6.4f %r' % (adjustment, entry))
                    entry[1][1] += adjustment
                    recalc_groups_pool(groups, newTable)
                    newError = calc_error(groups)
                    print('new %10.8f best %10.8f %3.1fs  ' % (
                        newError, bestError, time.time() - starttime))
                    if newError < bestError - minErrorDelta:
                        bestError = newError
                        bestTable = newTable
                        with open(opts['dest'], 'w') as fp:
                            json.dump(bestTable, fp)
            mag /= 2


if __name__ == '__main__':
    help = False
    opts = {'verbose': 0}
    for arg in sys.argv[1:]:
        if arg.startswith('--dest='):
            opts['dest'] = arg.split('=', 1)[1]
        elif arg.startswith('--maxmag='):
            opts['maxmag'] = float(arg.split('=', 1)[1])
        elif arg.startswith('--minmag='):
            opts['minmag'] = float(arg.split('=', 1)[1])
        elif arg == '--random':
            opts['random'] = True
        elif arg == '--recalc':
            opts['recalc'] = True
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
