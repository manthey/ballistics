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

GivenCombinations = {}


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
            raise
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
            raise
        sources += 1
        references.setdefault(data['key'], {})
        for key in ('key', 'ref', 'cms', 'summary', 'link', 'details'):
            if key in data:
                references[data['key']][key] = data[key]
        for entry in data['results']:
            try:
                item = {}
                for key in data:
                    if (key not in ('data', 'results', 'summary', 'details',
                                    'cms', 'link') and
                            not key.endswith('_note') and not key.startswith('__')):
                        item[key] = data[key]
                for key in entry:
                    if key not in ('conditions', 'points', 'results'):
                        item[key] = entry[key]
                GivenCombinations.setdefault(tuple(sorted([
                    key for key in entry['conditions']
                    if not key.startswith('desc') and
                    not key.startswith('ref') and
                    not key.endswith('_note') and
                    key not in ('date', 'technique', 'group')])), entry)
                for key in entry['conditions']:
                    item['given_' + key] = entry['conditions'][key]
                for key in entry['results']:
                    if key == 'settings':
                        item.update(entry['results']['settings'])
                    elif not key.endswith('_data'):
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
                for key in ('date', 'technique', 'ref'):
                    if item.get(key) is None:
                        raise Exception('Missing parameter %s' % key)
                skip = False
                for key in ('power_factor', ):
                    if item.get(key) is None:
                        print('Missing parameter %s for %s:%d.  Entry excluded.' % (
                            key, item['key'], item['idx']))
                        skip = True
                if opts.get('fields'):
                    item = {key: item[key] for key in item
                            if key in opts['fields']}
                if not skip:
                    total.append(item)
                if opts.get('grid') or opts.get('adjust'):
                    compile_grid(ReMnGrid, entry, opts, item)
            except Exception:
                print('Failed on %s: %d\n%r' % (file, entry.get('idx', 0),
                                                entry.get('conditions')))
                print(traceback.format_exc().strip())
    output_files(total, 'totallist', opts)
    output_files(trajectories, 'trajectories', opts)
    print('%d samples from %d sources' % (len(total), sources))
    output_files(references, 'references', opts)
    print('%d references' % len(references))
    params = parameter_summary(total)
    output_files(params, 'parameters', opts)
    print('%d parameters' % len(params))
    combo = [{
        'conditions': {param: GivenCombinations[key]['conditions'][param] for param in key},
        'power_factor': GivenCombinations[key]['results']['power_factor'],
        'time': GivenCombinations[key]['results'].get('time'),
    } for key in sorted(GivenCombinations)]
    output_files(combo, 'combinations', opts, maycsv=False)
    print('%d combinations' % len(combo))
    return ReMnGrid


def compile_grid(grid, entry, opts, item):
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
    if group:
        group = item['key'] + ':' + group
    # Don't include time technique in groups; it isn't accuracte enough
    if item['technique'] in ('time', 'gun_pendulum'):
        group = None
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
    last_re, last_mn = None, None
    for i in range(len(ReList)):
        Re = ReList[i]
        Mn = MnList[i]
        re = int(math.floor(math.log10(Re) * res))
        mn = int(math.floor(Mn * res))
        if re != last_re or mn != last_mn:
            if mn not in grid:
                grid[mn] = {}
            grid[mn][re] = grid[mn].get(re, 0) + 1
        last_re, last_mn = re, mn
    if group is not None:
        if group not in Groups:
            Groups[group] = []
        Groups[group].append({
            'group': group,
            'power_factor': item['power_factor'],
            're': ReList,
            'mn': MnList
        })


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


def make_groups_grid(opts):
    """
    Using the group values, make the groups grid.

    Enter: opts: program options for how to collate the grid.
    Exit:  GroupsGrid: an array of arrays indicating which mn/re combinations
                       need to be adjusted.
    """
    res = int(opts.get('gridres', 10))
    GroupsGrid = {}
    for group in Groups.values():
        if len(group) < 2:
            continue
        avg_pf = sum(entry['power_factor'] for entry in group) / len(group)
        for entry in group:
            factor = -1 if entry['power_factor'] > avg_pf else 1
            ReList = entry['re']
            MnList = entry['mn']
            last_re, last_mn = None, None
            for i in range(len(ReList)):
                Re = ReList[i]
                Mn = MnList[i]
                re = int(math.floor(math.log10(Re) * res))
                mn = int(math.floor(Mn * res))
                if re != last_re or mn != last_mn:
                    if mn not in GroupsGrid:
                        GroupsGrid[mn] = {}
                    GroupsGrid[mn][re] = GroupsGrid[mn].get(re, 0) + factor
                last_re, last_mn = re, mn
    return GroupsGrid


def output_files(data, basename, opts, mayjson=True, maycsv=True):
    """
    Output json and csv files for some data based on current options.

    Enter: data: the data to output
           basename: the base file name.  .json or .csv is added.
           opts: program options indicating which formats to output and the
                 destination path.
           mayjson: if False, never output json.
           maycsv: if False, never output csv.
    """
    out = opts.get('out', 'client/static')
    if opts.get('json', True) and mayjson:
        outpath = os.path.join(out, basename + '.json')
        try:
            with open(outpath, 'wt') as fp:
                json.dump(data, fp, sort_keys=True, indent=1,
                          separators=(',', ': '))
        except TypeError:
            with open(outpath, 'wt') as fp:
                json.dump(data, fp, sort_keys=False, indent=1,
                          separators=(',', ': '))
    if opts.get('csv') and maycsv:
        csv_dump(data, os.path.join(out, basename + '.csv'))


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
        if (params[key]['unique'] > maxval or key.endswith('_note')) and key != 'key':
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


def update_cod_adjusted(grid):
    """
    Update the cod_adjusted.json file based on the Mn-Re groups.
    """
    path = 'ballistics/cod_adjusted.json'
    if os.path.exists(path):
        adjust = json.load(open(path))
    else:
        adjust = {'version': 0, 'table': {}}
    version = adjust.get('version', 0)
    table = adjust.get('table', {}).copy()
    total = count = weight = absweight = 0
    for mn in grid:
        table.setdefault(str(mn), {})
        table.setdefault(str(mn+1), {})
        for re in grid[mn]:
            w = grid[mn][re]
            factor = w / max(abs(w), 1)
            total += factor
            weight += w
            absweight += abs(w)
            count += 1
            factor *= 0.0001
            if factor:
                factor *= max(1, min(200 - version, abs(w)))
                if version % 3 == 2:
                    factor /= 2
            table[str(mn)][str(re)] = (
                table[str(mn)].get(str(re), 0) + factor)
            table[str(mn)][str(re+1)] = (
                table[str(mn)].get(str(re+1), 0) + factor)
            table[str(mn+1)][str(re)] = (
                table[str(mn+1)].get(str(re), 0) + factor)
            table[str(mn+1)][str(re+1)] = (
                table[str(mn+1)].get(str(re+1), 0) + factor)
    # if len(adjust.get('table', {})):
    #     adjust['table_%d' % version] = adjust['table']
    adjust['version'] = version + 1
    for mn in table:
        for re in table[mn]:
            table[mn][re] = round(table[mn][re], 6)
    adjust['table'] = table
    adjust['resolution'] = cod_adjusted.Resolution

    json.dump(adjust, open(path, 'w'), sort_keys=True, indent=1,
              separators=(',', ': '))
    print('Adjustment: delta %d  weight %d |%d|  grid points %d  version %d' % (
        total, weight, absweight, count, adjust['version']))


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
  'client/static'.
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
        show_grid(make_groups_grid(opts), opts, False)
    if opts.get('adjust'):
        update_cod_adjusted(make_groups_grid(opts))
