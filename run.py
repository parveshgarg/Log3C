#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import cascading_clustering as cluster
from lib.util import *
import argparse


# ***********************************CODE USAGE GUIDE***************************************
#                             		Work for FSE 2018
#                              
# 1. How to run the code?
#    Open a terminal, run the cascading clustering with "python run.py".
#    Make sure that you have Python 3 and all required packages installed.
#
# 2. How to set the parameters?
#    Replace the parameters in the following "para" according to your data
# 
# Notes: multiprocessing is only used to read input files and save output files.
# ******************************************************************************************


@timeit
def main(args):
    raw_data, raw_index, event_occu_matrix = load_all_data(args)

    kpi_list = cluster.load_kpi(args.kpi_path)

    correlation_weight_list = cluster.get_correlation_weight(event_occu_matrix, kpi_list)

    weight_data, weight_list = cluster.weigh(raw_data, correlation_weight_list)

    cleanup_output_dir(args)

    final_clustering_result = cluster.cascade(args, raw_data, raw_index, weight_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--seq_folder", default="seq_folder/", required=False,
                        help="folder of log sequence matrix file")

    parser.add_argument("--kpi_path", default="kpi_path/", required=False,
                        help="the path of KPI file")

    parser.add_argument("--proc_num", type=int, default=16, required=False,
                        help="number of processes when loading files and saving files")

    parser.add_argument("--sample_rate", type=int, default=100, required=False,
                        help="same rate for sampling, 100 represents 1% sample rate")

    parser.add_argument("--threshold", type=float, default=0.3, required=False,
                        help="threshold for clustering, and also used when matching the nearest sequence")

    parser.add_argument("--save_file", type=bool, default=False, required=False,
                        help="FLAG to decide whether saving output clusters, it costs a lot if turned on")

    parser.add_argument("--output_path", default="output_path", required=False,
                        help="folder for saving output clusters of data")

    parser.add_argument("--rep_path", default="rep_path/", required=False,
                        help="path used for saving all representatives (patterns)")

    args = parser.parse_args()

    main(args)
