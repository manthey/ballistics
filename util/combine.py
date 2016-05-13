"""
This compares all of the results files and collapses them into a simple array.
"""

import json
import os
import traceback

total = []

basedir = "results"
for file in os.listdir(basedir):  # noqa
    path = os.path.join(basedir, file)
    try:
        data = json.load(open(path))
    except Exception:
        print 'Failed to parse file %s' % path
        continue
    for entry in data['results']:
        try:
            item = {}
            for key in data:
                if key not in ('data', 'results'):
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
            item['date'] = str(item['date'])
            item['year'] = int(item['date'].split('-')[0])
            for basekey in ('res', 'desc'):
                for i in range(1, 10):
                    key = '%s%d' % (basekey, i)
                    if key in item:
                        item[basekey] = (item[basekey] + ', ' if
                                         item.get(basekey) else '') + item[key]
                        del item[key]
            if entry.get('points'):
                item['trajectory'] = {
                    'x': entry['points']['x'],
                    'y': entry['points']['y'],
                }
            total.append(item)
        except Exception:
            print 'Failed on %s: %d\n%r' % (file, entry.get('idx', 0),
                                            entry.get('conditions'))
            print traceback.format_exc().strip()
destpath = 'built/totallist.json'
json.dump(total, open(destpath, 'wb'), sort_keys=True, indent=1,
          separators=(',', ': '))
