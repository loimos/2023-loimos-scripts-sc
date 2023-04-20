#!/usr/bin/env python3
# Copyright 2021 The Loimos Project Developers.
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: MIT

"""
Generates batch scripts for evaluation.
"""

import argparse
import pandas as pd
import math
import os
import stat
import subprocess

# Taken from:
# https://docs.python.org/3/library/stdtypes.html?highlight=format_map#str.format_map
# Dictionary that lets us leave out arguments without format_map freaking out
class DefaultValueDict(dict):
    def __missing__(self, key):
        return key

def write_script(batch_file, script_text, set_x=False):
    with open(batch_file, "w") as f:
        f.write(script_text)

    # Set executable mode on file
    if args.set_x:
        info = os.stat(batch_file)
        os.chmod(
            batch_file,
            info.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        )

def handle_command(command, batch_file, run=False):
    # Either submit the job...
    if run:
        run_argv = command.split(' ')
        run_argv.append(batch_file)
        subprocess.run(run_argv, check=True)

    # ...or print the run command
    else:
        print(command, batch_file)

def get_default_remapping(args):
    # Set up default remapping values which will be consistent across runs
    # note that these will be overwritten by values in experiments file,
    # if any are provided there
    remapping = DefaultValueDict()
    remapping['TEST_NAME'] = args.test_name
    remapping['TIME'] = args.time
    remapping['DAYS'] = args.days
    remapping['QUEUE'] = args.queue
    remapping['QOS'] = args.qos
    remapping['ENABLE_SCRATCH'] = args.enable_scratch
    remapping['ENABLE_DATA_GENERATION'] = args.synthetic
    remapping['ENABLE_TRACING'] = args.enable_tracing
    remapping['ENABLE_SMP'] = args.enable_smp
    remapping['ENABLE_LB'] = args.enable_lb
    remapping['ENABLE_CACHE'] = True
    remapping['CPUS_PER_TASK'] = args.cpus_per_task

    return remapping

def update_representation(remapping):
    # Bash boolean literals are all lower case
    for k, v in remapping.items():
        if isinstance(v, bool):
            remapping[k] = str(v).lower()
        if isinstance(v, float) and not pd.isna(v) and int(v) == v:
            remapping[k] = int(v)

def build_single_scripts(args, tests_to_run, baseline_script):
    remapping = get_default_remapping(args)
    for _, row in tests_to_run.iterrows():
        remapping.update(row.to_dict())
        update_representation(remapping)

        output_file_name = args.output_name.format_map(remapping)
        remapping['OUTPUT'] = output_file_name

        batch_file = os.path.join(args.output_folder, output_file_name) + ".sh"
        write_script(
            batch_file,
            baseline_script.format_map(remapping),
            set_x=args.set_x
        )
        command = args.run_command.format_map(remapping)
        handle_command(command, batch_file, run=args.run)

def build_ensemble_scripts(args, tests_to_run, baseline_script):
    # Split off run lines template from rest of script
    lines = baseline_script.split('\n')
    run_lines = lines[args.run_lines[0]:args.run_lines[1]]
    run_command = '\n'.join(run_lines)

    run_lines = []
    remapping = get_default_remapping(args)
    for _, row in tests_to_run.iterrows():
        remapping.update(row.to_dict())
        update_representation(remapping)

        output_file_name = args.output_name.format_map(remapping)
        remapping['OUTPUT'] = output_file_name

        run_lines.extend(run_command.format_map(remapping).split('\n'))

    # Merge the run lines back into a line string and make any final
    # variable expansions
    lines = lines[:args.run_lines[0]:] + run_lines + lines[args.run_lines[1]:]
    script = '\n'.join(lines).format_map(remapping)

    batch_file = os.path.join(args.output_folder, args.test_name) + ".sh"
    write_script(
        batch_file,
        script.format_map(remapping),
        set_x=args.set_x
    )
    command = args.run_command.format_map(remapping)
    handle_command(command, batch_file, run=args.run)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates batch scripts given testing file.')

    # Positional/required arguments:
    parser.add_argument('template',
        help='Template file.')
    parser.add_argument('tests_to_run',
        help='The path to a csv defined the tests to run.')
    parser.add_argument('output_folder',
        help='Where to output batch files.')
    parser.add_argument('test_name',
        help='Name of the test.')

    # Named/optional arguments
    parser.add_argument('-pn', '--processors-per-node', type=int, default=16,
        help='Number of processors per node to request.')
    parser.add_argument('-pt', '--cpus-per-task', type=int, default=10,
        help='Number of CPUs per task to request.')
    parser.add_argument('-t', '--time', type=int, default=60, #1 hour
        help='Time to request for allocation (in minutes).')
    parser.add_argument('-d', '--days', type=int, default=16,
        help='Number of simulation days to run for.')
    parser.add_argument('-c', '--run-command', default='sbatch',
        help='The command to run to submit the batch script.')
    parser.add_argument('-q', '--queue', default='default',
        help='The queue to submit the job to')
    parser.add_argument('-qos', '--qos', default='normal',
        help='The QoS to use for the job')
    parser.add_argument('-l', '--run-lines', type=int, nargs=2,
        default=[23,32],
        help='The range of lines containing the actual run command ' +\
        '(only used when building ensemble runs scripts)')
    parser.add_argument('-o', '--output-name',
        default="loimos_{TEST_NAME}_{NUM_NODES}_people_{PEOPLE_GRID_WIDTH}_by_{PEOPLE_GRID_HEIGHT}_location_{LOCATION_GRID_WIDTH}_by_{LOCATION_GRID_HEIGHT}_{DISTRIBUTION}{DEGREE}",
        help='The format of the name of the output files for each generated '+\
        'test')
    # Flags (pass them if you want the script to do the thing they enable)
    parser.add_argument('-r', '--run', action='store_true',
        help='Pass this flag to run job script in addition to generating it')
    parser.add_argument('-x', '--set-x', action='store_true',
        help='Pass this flag to set executable file mode on batch scripts')
    parser.add_argument('-e', '--ensemble', action='store_true',
        help='Pass this flag to combine jobs into an ensemble run')
    parser.add_argument('-et', '--enable-tracing', action='store_true',
        help='Pass this flag to obtain projections traces from the runs')
    parser.add_argument('-es', '--enable-smp', action='store_true',
        help='Pass this flag to run using smp')
    parser.add_argument('-el', '--enable-lb', action='store_true',
        help='Pass this flag to run using dynamic load balancing')
    parser.add_argument('-s', '--synthetic', action='store_true',
        help='Pass this flag to run using network data generated on the fly')
    parser.add_argument('-sr', '--enable-scratch', action='store_true',
        help='Pass this flag to load population data from system scratch')

    args = parser.parse_args()

    # Load the dataset.
    tests_to_run = pd.read_csv(args.tests_to_run, comment='#')
    print(tests_to_run.head())

    baseline_script = ''
    with open(args.template, "r") as f:
        baseline_script = f.read()

    if args.ensemble:
        build_ensemble_scripts(args, tests_to_run, baseline_script)
    else:
        build_single_scripts(args, tests_to_run, baseline_script)
