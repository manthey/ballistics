"""
This compares all of the results files and collapses them into a simple array.
"""

import json
import os
import traceback
import yaml

total = []

references = yaml.safe_load(open('data/references.yml'))['references']
references = {item['key']: item for item in references}

basedir = "results"
sources = 0
for file in sorted(os.listdir(basedir)):  # noqa
    path = os.path.join(basedir, file)
    try:
        data = json.load(open(path))
    except Exception:
        print 'Failed to parse file %s' % path
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
                if key not in ('data', 'results', 'summary', 'details', 'cms'):
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
                item['trajectory_x'] = entry['points']['x']
                item['trajectory_y'] = entry['points']['y']
            if 'given_technique' in item:
                item['technique'] = item['given_technique']
            for key in ('date', 'power_factor', 'technique', 'ref'):
                if item.get(key) is None:
                    raise Exception('Missing parameter %s' % key)
            total.append(item)
        except Exception:
            print 'Failed on %s: %d\n%r' % (file, entry.get('idx', 0),
                                            entry.get('conditions'))
            print traceback.format_exc().strip()
destpath = 'built/totallist.json'
json.dump(total, open(destpath, 'wb'), sort_keys=True, indent=1,
          separators=(',', ': '))
print '%d samples from %d sources' % (len(total), sources)
refpath = 'built/references.json'
json.dump(references, open(refpath, 'wb'), sort_keys=True, indent=1,
          separators=(',', ': '))
print '%d references' % len(references)
