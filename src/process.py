#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013-2016 David Manthey
#
# Licensed under the Apache License, Version 2.0 ( the "License" ); you may
# not use this file except in compliance with the License.  You may obtain a
# copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Process yml and md files into results using the ballistics code.

See help for details.
"""

import copy
import json
import markdown
import os
import pprint
import sys
import yaml

import ballistics


class FloatList:
    """A special list for rendering floats in JSON with predictable precision
    and in a controlled way."""
    def __init__(self, newList=None, formatString='%0.10g'):
        """Create a FloatList.
        Enter: newList: array for the list.
               formatString: default format string for floats."""
        self.list = list(newList)
        self.formatString = formatString

    def __repr__(self):
        return '[' + ','.join([
            self.formatString % val if isinstance(val, float) else repr(val)
            for val in self.list]) + ']'


class FloatEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FloatList):
            return repr(o)
        return super(FloatEncoder, self)(o)


def process_cases(info, results):
    """
    Check if there are any data entries in the current level of the info.
    If so, process each entry in turn.  If not, calculate the ballistics and
    store the results.
    Enter: info: dictionary of information.  If a data key is present, that
                 is a list of sub-cases, each of which will be processed in
                 turn.
           results: a list to append results to.
    """
    if info.get('skip'):
        return
    info = copy.deepcopy(info)
    for key in ('date', 'details', 'key', 'link', 'summary', 'cms'):
        info.pop(key, None)
    if isinstance(info.get('data'), list):
        data = info.pop('data')
        for entry in data:
            subinfo = copy.deepcopy(info)
            subinfo.update(entry)
            process_cases(subinfo, results)
        return
    args = []
    if not max([info[key] == '?' for key in info]):
        args.append('--power=?')
    args.extend(['--%s=%s' % (key, info[key]) for key in info])
    if ballistics.Verbose >= 2:
        print ' '.join([('"%s"' if ' ' in arg else '%s') % arg
                        for arg in args])
    verbose = ballistics.Verbose
    params, state, help = ballistics.parse_arguments(
        args, allowUnknownParams=True)
    ballistics.Verbose = verbose
    if ballistics.Verbose >= 2:
        pprint.pprint(state)
    starttime = ballistics.get_cpu_time()
    (newstate, points) = ballistics.find_unknown(
        state, params['unknown'], params.get('unknown_scan'))
    newstate['computation_time'] = ballistics.get_cpu_time()-starttime
    if ballistics.Verbose >= 1:
        pprint.pprint(newstate)
    if len(points) > 0:
        subset = points[::10]
        if subset[-1] != points[-1]:
            subset.append(points[-1])
        points = subset
        points = {key: FloatList([point.get(key) for point in points], '%.6g')
                  for key in points[0]}
    else:
        points = None
    results.append({'conditions': info, 'results': newstate, 'points': points})


def read_and_process_file(srcfile, outputPath, all=False):
    """
    Load a yaml file and any companion files.  For each non-skipped data set,
    calculate the ballistics result.  Output the results as a json file with
    the same base name and .json extension.  Don't calculate the file if there
    is already a results file that is newer than the source file(s) unless the
    all flag is set.

    Enter: srcfile: path of the yml file to load.
           outputPath: directory where the results will be stored.
           all: True to process regardless of results time.
    """
    srcdate = os.path.getmtime(srcfile)
    info = yaml.safe_load(open(srcfile))
    if info.get('skip'):
        return
    basename = os.path.splitext(os.path.basename(srcfile))[0]
    basepath = os.path.dirname(srcfile)
    companionFiles = [os.path.join(basepath, file)
                      for file in os.listdir(basepath)
                      if os.path.splitext(file)[0] == basename]
    srcdate = max(srcdate, max([os.path.getmtime(file)
                                for file in companionFiles]))
    destpath = os.path.join(outputPath, basename + '.json')
    if (os.path.exists(destpath) and not all and
            os.path.getmtime(destpath) > srcdate):
        return
    for file in companionFiles:
        ext = os.path.splitext(file)[1]
        if ext == '.md':
            info['details'] = markdown.markdown(open(file).read())
        elif ext == '.yml':
            pass  # our source file.
        else:
            raise 'Unknown companion file %s\n' % file
    if ballistics.Verbose >= 1:
        print srcfile
    results = copy.deepcopy(info)
    results['results'] = []
    process_cases(info, results['results'])
    json.dump(results, open(destpath, 'wb'), sort_keys=True, indent=1,
              separators=(',', ': '), cls=FloatEncoder)


if __name__ == '__main__':  # noqa - mccabe
    files = []
    allFiles = False
    outputPath = None
    help = False
    for arg in sys.argv[1:]:
        if arg == '--all':
            allFiles = True
        elif arg.startswith('--out='):
            outputPath = os.path.abspath(os.path.expanduser(
                arg.split('=', 1)[1]))
        elif arg == '-v':
            ballistics.Verbose += 1
        elif arg.startswith('-'):
            help = True
        else:
            path = os.path.abspath(os.path.expanduser(arg))
            if not os.path.exists(path):
                raise 'Input path %s does not exist' % path
            if os.path.isdir(path):
                files.extend(sorted([os.path.abspath(os.path.join(path, file))
                                     for file in os.listdir(path)
                                     if os.path.splitext(file)[1] == '.yml']))
            else:
                files.append(path)
    if (help or not len(files) or not outputPath or
            not os.path.isdir(outputPath)):
        print """Process yml and md files using the ballistics code.

Syntax: process.py --out=(path) --all -v (input files ...)

If the input files are a directory, all yml files in that path are processed.
Only files newer than the matching results are processed unless the
--all flag is used.
--out specifies an output directory, which must exist.
-v increase verbosity.
"""
        sys.exit(0)
    for file in files:
        read_and_process_file(file, outputPath, allFiles)
