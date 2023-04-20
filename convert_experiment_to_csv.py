#!/usr/bin/env python3

import re
import pandas as pd
import argparse
from os import walk, path

# Regex
people_exp = re.compile(r"Running Loimos on (\d+) PEs with (\d+) people, (\d+) locations")
chares_exp = re.compile(r"(\d+) people chares, (\d+) location chares")
degree_exp = re.compile(r"Average degree of (\d+)")
nodes_exp = re.compile(r"Charm\+\+> Running on (\d+) hosts")
shared_loading_time = re.compile(r"Finished loading shared/global data in (\d+\.\d+) seconds")
local_loading_time = re.compile(r"Finished loading people and location data in (\d+\.\d+) seconds")
simulation_time = re.compile(r"Finished simulating (\d+) days in (\d+\.\d+) seconds")
edge_visits = re.compile(r"Total Visits Processed (\d+)")
daily_statistics = re.compile(r"Iteration (\d+) Execution Time: (\d+\.\d+) seconds. Infectious Count: (\d+).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyzes experimental data.')
    parser.add_argument('experiment_folder',
        help='Folder of experiments')
    parser.add_argument('-p', '--prefix', default="",
        help='Prefix for experiments')
    parser.add_argument('-o', '--out-file', default="results.csv",
        help='Name of file to save parsed output to')
    parser.add_argument('-d', '--get-daily', action="store_true",
        help='Pass this flag to collect daily statistics')

    args = parser.parse_args()
    if args.prefix != "" and args.prefix[-1] != "_":
        args.prefix += "_"

    experiment_folder = args.experiment_folder
    if experiment_folder[-1] == "/":
        experiment_folder = experiment_folder[:-1]

    verbose_filename_exp = re.compile(f"{args.prefix}([a-zA-Z_\d]+)_(\d+)_nodes_(\d+)_procs_(\d+)_threads_(\d+)_chares\.out")
    filename_exp = re.compile(f"{args.prefix}([a-zA-Z_\d]+)_(\d+)_nodes.out")
    # Get all files in experiment.
    _, _, filenames = next(walk(args.experiment_folder))
    print(f"{len(filenames)} runs found.")

    rows = []
    for filename in filenames:
        filename_is_verbose = False
        filename_match = filename_exp.search(filename)
        if filename_match is None:
            filename_match = verbose_filename_exp.search(filename)
            filename_is_verbose = filename_match is not None
        if filename_match is None:
            print(f"Skipping {filename}...")
            continue

        #print(f"Reading {filename}")
        f = open(path.join(experiment_folder, filename), "r")
        output = f.read()

        if people_exp.search(output) is None:
            print(f"Skipping {filename}...")
            continue

        runtime_analysis = {'filename': filename}

        # Some settings may be encoded in the file/expirement name
        runtime_analysis['dataset'] = filename_match.group(1)
        runtime_analysis['nodes'] = filename_match.group(2)
        if filename_is_verbose:
            runtime_analysis['procs/node'] = filename_match.group(3)
            runtime_analysis['worker threads/proc'] = filename_match.group(4)
            runtime_analysis['chares/thread'] = filename_match.group(5)

        if simulation_time.search(output) is None:
            print(f"Error in {filename}")
            runtime_analysis['error'] = True
        else:
            runtime_analysis['error'] = False

            # Extract total statistics
            runtime_analysis['shared_loading_time'] = shared_loading_time\
                    .search(output).group(1)
            runtime_analysis['local_loading_time'] = local_loading_time\
                    .search(output).group(1)
            runtime_analysis['total_execution_time'] = simulation_time\
                    .search(output).group(2)
            runtime_analysis['days'] = simulation_time\
                    .search(output).group(1)
            #runtime_analysis['edges_processed'] = edge_visits.search(output).group(1)

        # Extract overall runtime parameters
        match_obj = people_exp.search(output)
        #runtime_analysis['num_processors'] = match_obj.group(1)
        #runtime_analysis['num_nodes'] = match_obj.group(1) // 16
        runtime_analysis['people'] = match_obj.group(2)
        runtime_analysis['locations'] = match_obj.group(3)

        #nodes_match = nodes_exp.search(output)
        #runtime_analysis['num_nodes'] = nodes_match.group(1)

        #degree_match = degree_exp.search(output)
        #if degree_match:
        #    runtime_analysis['degree'] = degree_match.group(1)

        chare_match = chares_exp.search(output)
        runtime_analysis['people_chares'] = chare_match.group(1)
        runtime_analysis['location_chares'] = chare_match.group(2)

        # Extract daily statistics
        if args.get_daily:
            daily_matches = daily_statistics.findall(output)
            daily_dicts = [{"day": day, "runtime": runtime,
                "infectious_count": infectious}
                for day, runtime, infectious in daily_matches]
            daily_df = pd.DataFrame(daily_dicts)
            daily_df.to_csv(path.join(
                    experiment_folder,
                    filename.replace(".out", "_daily_summary.csv")
                ), index=False)

        # Append to dataframe and respect ordering.
        rows.append(runtime_analysis)

    df = pd.DataFrame(rows)

    # Clean up the data a little bit
    dtypes = {
        "nodes": int,
        "shared_loading_time": float,
        "local_loading_time": float,
        "total_execution_time": float,
        #"days": int,
        "people": int,
        "locations": int,
        "people_chares": int,
        "location_chares": int,
    }
    sort_by = [
        "dataset",
        "nodes",
    ]
    if filename_is_verbose:
        dtypes.update({
            "procs/node": int,
            "worker threads/proc": int,
            "chares/thread": int,
        })
        sort_by += [
            "procs/node",
            "worker threads/proc",
            "chares/thread",
        ]
    sort_by.append("filename")

    df = df.astype(dtypes)
    df.sort_values(sort_by, inplace=True)
    df.to_csv(path.join(experiment_folder, args.out_file), index=False)
