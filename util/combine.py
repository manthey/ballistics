"""
This compares all of the results files and collapses them into a simple array.
"""

import csv
import json
import math
import os
import sys
import traceback
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir)))

from ballistics import cod_adjusted  # noqa


Groups = {}
GroupsRe = {}
GroupsGrid = {}


def combine(opts):  # noqa
    """
    Combine all of the results and references, output one file with all the
    references and one with all the results.  The results are flattened into a
    single array of objects with no subobjects.

    Enter: opts: a dictionary of options for processing.
    Exit:  ReMnGrid: a grid  indicating which Mach and Reynolds number were
                     used in computation.
    """
    total = []
    trajectories = []

    references = yaml.safe_load(open('data/references.yml'))['references']
    references = {item['key']: item for item in references}

    basedir = 'data'
    for file in sorted(os.listdir(basedir)):  # noqa
        if not file.endswith('.yml') or file in (
                'template.yml', 'references.yml'):
            continue
        path = os.path.join(basedir, file)
        try:
            data = yaml.safe_load(open(path))
        except Exception:
            print('Failed to parse file %s' % path)
            continue
        references.setdefault(data['key'], {})
        for key in ('key', 'ref', 'cms', 'summary', 'link', 'details'):
            if key in data:
                references[data['key']][key] = data[key]

    ReMnGrid = {}

    basedir = opts.get('results', 'results')
    sources = 0
    for file in sorted(os.listdir(basedir)):  # noqa
        path = os.path.join(basedir, file)
        try:
            data = json.load(open(path))
        except Exception:
            print('Failed to parse file %s' % path)
            continue
        sources += 1
        references.setdefault(data['key'], {})
        for key in ('key', 'ref', 'cms', 'summary', 'link', 'details'):
            if key in data:
                references[data['key']][key] = data[key]
        for entry in data['results']:
            try:
                item = {}
                for key in data:
                    if key not in ('data', 'results', 'summary', 'details',
                                   'cms', 'link'):
                        item[key] = data[key]
                for key in entry:
                    if key not in ('conditions', 'points', 'results'):
                        item[key] = entry[key]
                for key in entry['conditions']:
                    item['given_' + key] = entry['conditions'][key]
                for key in entry['results']:
                    if not key.endswith('_data'):
                        item[key] = entry['results'][key]
                    else:
                        for subkey in entry['results'][key]:
                            item['final_%s_%s' % (key.rsplit(
                                '_data', 1)[0], subkey)] = entry[
                                    'results'][key][subkey]
                item['date'] = str(item.get('given_date', item['date']))
                item['year'] = int(item['date'].split('-')[0])
                item['date_filled'] = '-'.join((item['date'].split('-') +
                                                ['01', '01'])[:3])
                for basekey in ('ref', 'desc'):
                    for i in range(0, 10):
                        for prefix in ('', 'given_'):
                            if i:
                                key = '%s%s%d' % (prefix, basekey, i)
                            else:
                                key = '%s%s' % (prefix, basekey)
                            if item.get(key):
                                if item[key] not in item.get(basekey, ''):
                                    if item.get(basekey):
                                        item[basekey] += (
                                            '  ' if item[basekey].endswith('.')
                                            else ', ')
                                    else:
                                        item[basekey] = ''
                                    item[basekey] += item[key]
                                del item[key]
                if entry.get('points'):
                    traj = {'key': item['key'], 'idx': item['idx']}
                    for key in entry['points']:
                        traj['trajectory_' + key] = entry['points'][key]
                        if opts.get('points', False):
                            item['trajectory_' + key] = entry['points'][key]
                    trajectories.append(traj)
                if 'given_technique' in item:
                    item['technique'] = item['given_technique']
                for key in ('date', 'power_factor', 'technique', 'ref'):
                    if item.get(key) is None:
                        raise Exception('Missing parameter %s' % key)
                if opts.get('fields'):
                    item = {key: item[key] for key in item
                            if key in opts['fields']}
                total.append(item)
                if opts.get('grid') or opts.get('adjust'):
                    compile_grid(ReMnGrid, entry, opts, item)
            except Exception:
                print('Failed on %s: %d\n%r' % (file, entry.get('idx', 0),
                                                entry.get('conditions')))
                print(traceback.format_exc().strip())
    out = opts.get('out', 'client/static')
    if opts.get('json', True):
        destpath = os.path.join(out, 'totallist.json')
        json.dump(total, open(destpath, 'wt'), sort_keys=True, indent=1,
                  separators=(',', ': '))
    if opts.get('csv'):
        csv_dump(total, os.path.join(out, 'totallist.csv'))
    if opts.get('json', True):
        refpath = os.path.join(out, 'trajectories.json')
        json.dump(trajectories, open(refpath, 'wt'), sort_keys=True, indent=1,
                  separators=(',', ': '))
    if opts.get('csv'):
        csv_dump(trajectories, os.path.join(out, 'trajectories.csv'))
    print('%d samples from %d sources' % (len(total), sources))
    if opts.get('json', True):
        refpath = os.path.join(out, 'references.json')
        json.dump(references, open(refpath, 'wt'), sort_keys=True, indent=1,
                  separators=(',', ': '))
    if opts.get('csv'):
        csv_dump(references, os.path.join(out, 'references.csv'))
    print('%d references' % len(references))
    params = parameter_summary(total)
    if opts.get('json', True):
        refpath = os.path.join(out, 'parameters.json')
        json.dump(params, open(refpath, 'wt'), sort_keys=True, indent=1,
                  separators=(',', ': '))
    if opts.get('csv'):
        csv_dump(params, os.path.join(out, 'parameters.csv'))
    print('%d parameters' % len(params))
    return ReMnGrid


def compile_grid(grid, entry, opts, item):  # noqa
    """
    Compile the usage of grid and reynolds numbers from a grid, always
    excluding theoretical values and possibly non-group values.

    Enter: grid: collected grid information.  Modified.
           entry: the individual entry to add to the grid.
           opts: program options for how to collate the grid.
           item: the individual item that is being processed.
    """
    if item['technique'] == 'theory':
        return
    group = entry['conditions'].get('group')
    groupset = False
    if group and group not in Groups:
        Groups[group] = item['power_factor']
        groupset = True
    if (not entry.get('points') or 'Re' not in entry['points'] or
            'Mn' not in entry['points']):
        return
    if opts.get('group') and not group:
        return
    ReList = json.loads(entry['points']['Re'])
    MnList = json.loads(entry['points']['Mn'])
    if len(ReList) != len(MnList):
        return
    res = int(opts.get('gridres', 10))
    for i in range(len(ReList)):
        Re = ReList[i]
        Mn = MnList[i]
        re = int(round(math.log10(Re) * res))
        mn = int(round(Mn * res))
        if mn not in grid:
            grid[mn] = {}
        grid[mn][re] = grid[mn].get(re, 0) + 1
    if groupset:
        GroupsRe[group] = {'re': ReList, 'mn': MnList}
    if (group and not groupset and
            0.5 < item['power_factor'] / Groups[group] < 2):
        factor = 1 if item['power_factor'] < Groups[group] else -1
        for i in range(len(ReList)):
            Re = ReList[i]
            Mn = MnList[i]
            re = int(round(math.log10(Re) * res))
            mn = int(round(Mn * res))
            if mn not in GroupsGrid:
                GroupsGrid[mn] = {}
            GroupsGrid[mn][re] = GroupsGrid[mn].get(re, 0) + factor
        if group in GroupsRe:
            factor *= -1
            for i in range(len(GroupsRe[group]['re'])):
                Re = GroupsRe[group]['re'][i]
                Mn = GroupsRe[group]['mn'][i]
                re = int(round(math.log10(Re) * res))
                mn = int(round(Mn * res))
                if mn not in GroupsGrid:
                    GroupsGrid[mn] = {}
                GroupsGrid[mn][re] = GroupsGrid[mn].get(re, 0) + factor


def csv_dump(data, path):
    """
    Write to a csv file.  Data is sorted by key and idx.

    Enter: data: list or dictionary to write.
           path: path to write.
    """
    if isinstance(data, dict):
        data = [data[key] for key in sorted(data.keys())]
    else:
        data = [val[-1] for val in sorted([(
            row.get('key'), row.get('idx'), row) for row in data])]
    keys = {}
    for entry in data:
        keys.update(entry)
    keys = [val[-1] for val in sorted([(
        key != 'key', key != 'idx', key != 'power_factor', key)
        for key in keys])]
    with open(path, 'wt', newline='') as csvfile:
        # Quote all non-numeric fields to preserve datatypes.
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(keys)
        for entry in data:
            row = [entry.get(key) for key in keys]
            row = [val.encode('utf8') if isinstance(val, bytes) else val
                   for val in row]
            writer.writerow(row)


def parameter_summary(data):
    """
    Make a dictionary of all known parameters.  Each includes how many entries
    used that parameter.  If the parameter is numeric, the mininum and maximum
    are recorded.

    Enter: data: list of dictionaries of data.
    Exit:  params: a dictionary of used parameters.
    """
    maxval = 25
    params = {}
    for entry in data:
        for key in entry:
            if entry[key] is None or entry[key] == '':
                continue
            if key not in params:
                params[key] = {'key': key, 'count': 0, 'values': {}}
            params[key]['count'] += 1
            params[key]['values'][entry[key]] = params[key]['values'].get(entry[key], 0) + 1
            if isinstance(entry[key], (int, float)):
                if 'min' not in params[key]:
                    params[key]['numeric'] = 0
                    params[key]['min'] = params[key]['max'] = entry[key]
                params[key]['numeric'] += 1
                params[key]['min'] = min(params[key]['min'], entry[key])
                params[key]['max'] = max(params[key]['max'], entry[key])
    for key in params:
        params[key]['unique'] = len(params[key]['values'])
        if params[key]['unique'] > maxval or key.endswith('_note'):
            del params[key]['values']
    return params


def show_grid(grid, opts, usemin=True):
    """
    Output a collected grid to stdout.

    Enter: grid: the collected grid information.
           opts: program options for how the grid was collated.
           usemin: if True, use the minimum points option.  If False, show all
                   points.
    """
    res = int(opts.get('gridres', 10))
    gridmin = int(opts.get('gridmin', 2))
    if gridmin and usemin:
        for mn in list(grid.keys()):
            for re in list(grid[mn].keys()):
                if grid[mn][re] < gridmin:
                    del grid[mn][re]
            if not len(grid[mn]):
                del grid[mn]
    minmn = min(grid.keys())
    maxmn = max(grid.keys())
    minre = maxre = min(grid[minmn].keys())
    for mn in grid:
        minre = min(minre, min(grid[mn].keys()))
        maxre = max(maxre, max(grid[mn].keys()))
    d = len('%g' % (1.0 / res))
    sys.stdout.write('%*s' % (d, ' '))
    for re in range(minre, maxre + 1):
        sys.stdout.write(' %0.*f' % (d - 2, (float(re) / res)))
    sys.stdout.write('\n')
    nonzero = 0
    for mn in range(minmn, maxmn + 1):
        sys.stdout.write('%0.*f' % (d - 2, (float(mn) / res)))
        for re in range(minre, maxre + 1):
            if grid.get(mn, {}).get(re) is None:
                sys.stdout.write(' %*s' % (d, ' '))
            else:
                nonzero += 1
                val = '%d' % grid[mn][re]
                if len(val) > (d if usemin or grid[mn][re] < 0 else d - 1):
                    if usemin:
                        val = '9' * d
                    elif grid[mn][re] < 0:
                        val = '-' + '9' * (d - 1)
                    else:
                        val = '+' + '9' * (d - 1)
                sys.stdout.write(' %*s' % (d, val))
        sys.stdout.write('\n')
    sys.stdout.write('%d filled\n' % nonzero)


if __name__ == '__main__':  # noqa - mccabe
    help = False
    opts = {'json': True}
    for arg in sys.argv[1:]:
        if arg == '--adjust':
            opts['adjust'] = True
        elif arg == '--csv':
            opts['csv'] = True
        elif arg == '--grid':
            opts['grid'] = True
        elif arg == '--group':
            opts['group'] = True
        elif arg == '--json':
            opts['json'] = True
        elif arg == '--limit':
            opts['fields'] = [
                'date_filled', 'power_factor', 'desc', 'ref', 'date',
                'technique', 'key', 'idx']
        elif arg.startswith('--limit='):
            opts['fields'] = arg.split('=', 1)[1].split(',')
        elif arg.startswith('--min='):
            opts['gridmin'] = int(arg.split('=', 1)[1])
        elif arg == '--nocsv':
            opts['csv'] = False
        elif arg == '--nojson':
            opts['json'] = False
        elif arg in ('--nopoints', '--notraj', '--notrajectory'):
            opts['points'] = False
        elif arg.startswith('--out='):
            opts['out'] = arg.split('=', 1)[1]
        elif arg in ('--points', '--traj', '--trajectory'):
            opts['points'] = True
        elif arg.startswith('--res='):
            opts['gridres'] = float(arg.split('=', 1)[1])
        elif arg.startswith('--results='):
            opts['results'] = arg.split('=', 1)[1]
        else:
            help = True
    if help:
        print("""Combine results into a single file plus a references file.

Syntax:  combine.py --grid --points|--nopoints --res=(grid resolution)
    --min=(grid min) --group --csv|--nocsv --json|--nojson --adjust
    --limit[=(fields)] --results=(results directory) --out=(output directory)
--adjust adjusts the json file used with cod_adjusted.
--csv outputs csv files in the output directory.
--grid outputs a grid of used Re/Mn values to stdout.
--group outputs only the grid for groups that are present.
--json outputs json files to the output directory (default).
--limit reduces the fields output to the comma-separated list of fields.  If no
  fields are given, a common subset of fields is used instead.
--min specified how many points are required before a grid is output (default
  2).
--out is the directory where json and csv files are stored.  Default is
  'built'.
--points includes trajectory information in the main output.
--res indicates the group resolution (default 10).  This is the inverse of the
  increment between Mach values and between base-10 powers of the Reynolds
  number.
--results is the directory where output from the process script is located.
  Default is 'results'.
""")
        sys.exit(0)
    if opts.get('adjust'):
        opts['gridres'] = cod_adjusted.Resolution
    grid = combine(opts)
    if opts.get('grid'):
        show_grid(grid, opts)
        show_grid(GroupsGrid, opts, False)
    if opts.get('adjust'):
        path = 'ballistics/cod_adjusted.json'
        if os.path.exists(path):
            adjust = json.load(open(path))
        else:
            adjust = {'version': 0, 'table': {}}
        table = adjust.get('table', {}).copy()
        total = count = weight = absweight = 0
        for mn in GroupsGrid:
            if str(mn) not in table:
                table[str(mn)] = {}
            for re in GroupsGrid[mn]:
                factor = GroupsGrid[mn][re] / max(abs(GroupsGrid[mn][re]), 1)
                total += factor
                weight += GroupsGrid[mn][re]
                absweight += abs(GroupsGrid[mn][re])
                count += 1
                factor *= 0.001
                if factor:
                    factor *= max(1, min(50 - adjust.get('version', 0),
                                         abs(GroupsGrid[mn][re])))
                table[str(mn)][str(re)] = (
                    table[str(mn)].get(str(re), 0) - factor)  # ##DWM:: +factor?
        if len(adjust.get('table', {})):
            adjust['table_%d' % adjust.get('version', 0)] = adjust['table']
        adjust['version'] = adjust.get('version', 0) + 1
        adjust['table'] = table
        adjust['resolution'] = cod_adjusted.Resolution

        adjust = {'version': adjust['version'], 'table': table}

        json.dump(adjust, open(path, 'wb'), sort_keys=True, indent=1,
                  separators=(',', ': '))
        print('Adjustment: delta %d  weight %d |%d|  groups %d  version %d' % (
            total, weight, absweight, count, adjust['version']))
