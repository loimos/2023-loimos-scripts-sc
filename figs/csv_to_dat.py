#!/usr/bin/env python3

import pandas as pd
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Converts csv to dat file')
    parser.add_argument('in_file', metavar='I',
        help='Path to input csv file')

    args = parser.parse_args()

    in_file = args.in_file
    prefix, _ = os.path.splitext(in_file)
    out_file = f'{prefix}.dat'

    df = pd.read_csv(in_file)
    df['average_execution_time'] = df['total_execution_time'] / df['days']

    pivoted_df = df.pivot(columns='dataset', index=['nodes'],
            values=['average_execution_time'])
    print(pivoted_df)

    pivoted_df.to_csv(out_file, sep=" ", header=False)
    print(f'Saved results to {out_file}')
