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
import functools
import json
import markdown
import multiprocessing
import os
import pprint
import psutil
import signal
import sys
import time
import yaml

import ballistics


Pool = None


# Used to memoize computations.  When running in multiple processes, less
# benefit is gained from this, but it still saves computation time.
PreviousResults = {'used': 0}


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
        try:
            return super(FloatEncoder, self)(o)
        except TypeError:
            print 'Can\'t encode: %r' % o
            raise


def calculate_case(hash, args, info, verbose):
    """
    Process an individual case.

    Enter: hash: hash value used to memoize results.
           args: arguments formulated for the ballistics routines.
           info: info that was used to construct the arguments.
           verbose: verbosity for the ballistics program
    Exit:  hash: the input hash value.
           state: final state from the ballistics routines.
           points: time series of trajectory.
    """
    if verbose >= 3:
        pprint.pprint(info)
    if verbose >= 3:
        print hash
    if hash in PreviousResults:
        PreviousResults['used'] += 1
        if verbose >= 3:
            print 'From hash', PreviousResults['used']
        return PreviousResults[hash]
    ballistics.Verbose = max(0, verbose - 2)
    params, state, help = ballistics.parse_arguments(
        args, allowUnknownParams=True)
    ballistics.Verbose = max(0, verbose - 2)
    if verbose >= 4:
        pprint.pprint(state)
    starttime = ballistics.get_cpu_time()
    (newstate, points) = ballistics.find_unknown(
        state, params['unknown'], params.get('unknown_scan'))
    newstate['computation_time'] = ballistics.get_cpu_time()-starttime
    if verbose >= 3:
        pprint.pprint(newstate)
    if len(points) > 0:
        subset = points[::10]
        if subset[-1] != points[-1]:
            subset.append(points[-1])
        points = subset
        points = {key: FloatList([
            point.get(key) for point in points], '%.6g')
            for key in points[0]}
    else:
        points = None
    PreviousResults[hash] = (hash, newstate, points)
    if verbose >= 2:
        print hash, '-->', newstate.get('power_factor')
    return PreviousResults[hash]


def calculate_cases(results, cases, verbose, pool=None):
    """
    Given a set of cases, generate results for each, possibly using
    multiprocessing.

    Enter: results: array to store results.
           cases: cases to process:
           verbose: verbosity for the ballistics program.
           pool: if not None, use this multiprocessing pool.
    Exit:  success: False for cancelled
    """
    hashes = [item[-1] for item in sorted([(cases[hash]['position'], hash)
              for hash in cases])]
    if pool is None:
        for hash in hashes:
            hash, state, points = calculate_case(
                hash, cases[hash]['args'], cases[hash]['info'], verbose)
            calculate_cases_results(hash, state, points, results)
    else:
        tasks = []
        for hash in hashes:
            tasks.append(pool.apply_async(calculate_case, (
                hash, cases[hash]['args'], cases[hash]['info'], verbose)))
        while len(tasks):
            for pos in xrange(len(tasks) - 1, -1, -1):
                task = tasks[pos]
                if task.ready():
                    hash, state, points = task.get()
                    calculate_cases_results(hash, state, points, results)
                    del tasks[pos]
                    if verbose >= 1:
                        print '%d/%d left' % (len(tasks), len(hashes))
            if len(tasks):
                tasks[0].wait(0.1)
    return True


def calculate_cases_results(hash, state, points, results):
    """
    Store results from a processed case.

    Enter: hash: hash of the case.
           state: final state of the case.
           points: trajectory points of the case.
           results: array to store results.
    """
    for res in results['results']:
        if res.get('hash') == hash:
            res['results'] = state
            res['points'] = points
            del res['hash']


def get_multiprocess_pool(multi):
    """
    Get a multiprocessing pool.

    Enter: multi: the number of processors to use ot True to use them all.
    Exit:  pool: a multiprocess pool.
    """
    pool = multiprocessing.Pool(processes=None if multi is True else multi,
                                initializer=worker_init)
    priorityLevel = (psutil.BELOW_NORMAL_PRIORITY_CLASS
                     if sys.platform == 'win32' else 10)
    parent = psutil.Process()
    parent.nice(priorityLevel)
    for child in parent.children():
        child.nice(priorityLevel)
    return pool


def process_cases(info, results, cases, verbose=0):
    """
    Check if there are any data entries in the current level of the info.
    If so, process each entry in turn.  If not, calculate the ballistics and
    store the results.
    Enter: info: dictionary of information.  If a data key is present, that
                 is a list of sub-cases, each of which will be processed in
                 turn.
           results: a list to append results to.
           cases: a dictionary to collect cases in
           verbose: verbosity for the ballistics program
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
            process_cases(subinfo, results, cases, verbose)
        return
    args = []
    if not max([info[key] == '?' for key in info]):
        args.append('--power=?')
    args.extend(sorted([
        '--%s=%s' % (key, info[key]) for key in info if key not in (
            'ref', 'ref2', 'ref3', 'desc', 'desc2', 'desc3')]))
    hash = ' '.join([('"%s"' if ' ' in arg else '%s') % arg for arg in args])
    if hash not in cases:
        cases[hash] = {'info': info, 'args': args, 'position': len(cases),
                       'hash': hash}
    results.append({'conditions': info, 'hash': hash})


def read_and_process_file(srcfile, outputPath, all=False, verbose=0,
                          pool=None):
    """
    Load a yaml file and any companion files.  For each non-skipped data set,
    calculate the ballistics result.  Output the results as a json file with
    the same base name and .json extension.  Don't calculate the file if there
    is already a results file that is newer than the source file(s) unless the
    all flag is set.

    Enter: srcfile: path of the yml file to load.
           outputPath: directory where the results will be stored.
           all: True to process regardless of results time.
           verbose: verbosity for the ballistics program.
           pool: if not None, use this multiprocessing pool.
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
            raise Exception('Unknown companion file %s\n' % file)
    if verbose >= 1:
        print srcfile
    results = copy.deepcopy(info)
    results['results'] = []
    cases = {}
    process_cases(info, results['results'], cases, verbose)
    if calculate_cases(results, cases, verbose, pool):
        json.dump(results, open(destpath, 'wb'), sort_keys=True, indent=1,
                  separators=(',', ': '), cls=FloatEncoder)


def worker_init():
    """Supress the ctrl-c signal in the worker processes."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


if __name__ == '__main__':  # noqa - mccabe
    files = []
    allFiles = False
    multi = False
    multiFile = True
    outputPath = None
    verbose = 0
    help = False
    for arg in sys.argv[1:]:
        if arg == '--all':
            allFiles = True
        elif arg.startswith('--multi'):
            multi = True
            if '=' in arg:
                multi = int(arg.split('=', 1)[1])
                if multi <= 1:
                    multi = False
            if 'multicase' in arg:
                multiFile = False
            if 'multifile' in arg:
                multiFile = True
        elif arg.startswith('--out='):
            outputPath = os.path.abspath(os.path.expanduser(
                arg.split('=', 1)[1]))
        elif arg == '-v':
            verbose += 1
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

Syntax: process.py --out=(path) --all -v
        --multi|--multifile|--multicase[=(number of processes)]
        (input files ...)

If the input files are a directory, all yml files in that path are processed.
Only files newer than the matching results are processed unless the
--all flag is used.
--multi runs parallel processes.  This uses the number of processors available
  unless a number is specified.  --multifile runs a process per input file,
  --multicase runs a process per basllistics case.
--out specifies an output directory, which must exist.
-v increase verbosity.
"""
        sys.exit(0)
    starttime = time.time()
    if multi:
        pool = get_multiprocess_pool(multi)
    else:
        pool = None
    try:
        if not multi or not multiFile:
            for file in files:
                read_and_process_file(file, outputPath, allFiles, verbose,
                                      pool)
        else:
            mapfunc = functools.partial(read_and_process_file, *[], **{
                'outputPath': outputPath,
                'all': allFiles,
                'verbose': verbose
            })
            task = pool.map_async(mapfunc, files, 1)
            while not task.ready():
                task.wait(1)
            pool.close()
            pool.join()
    except KeyboardInterrupt:
        if pool:
            try:
                pool.terminate()
                pool.join()
            except Exception:
                pass
        print "Cancelled via keyboard interrupt"
    if verbose >= 1:
        print 'Total computation time: %4.2f s' % (time.time() - starttime)
