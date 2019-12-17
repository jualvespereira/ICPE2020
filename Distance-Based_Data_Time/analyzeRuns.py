#!/usr/bin/env python3

import sys
import os
import math

# The sampling strategies that should be analyzed
TYPES = ["distBased_", "divDistBased_", "solverBased_", "random", "henard", "twise"]
CASE_STUDIES = ["x264_0", "x264_1", "x264_2", "x264_3", "x264_4", "x264_5", "x264_6", "x264_7", "x264_8", "x264_9", "x264_10", "x264_11", "x264_12", "x264_13", "x264_14", "x264_15", "x264_16"]

SEPARATOR = "/"
SPL_CONQUEROR_PREFIX = "out_"
ALL_RESULTS_PREFIX = "all_"
ERROR_PREFIX = "error_"
STANDARD_DEVIATION_PREFIX = "sd_"
T_TEST_PREFIX = "ttest_"
KOLMOGOROV_SMIRNOV_PREFIX = "kstest_"
WHOLE_POPULATION = "wp"
VARIANCE_RESULT_PREFIX = "var_"
OTHER_FILE_PREFIXES = ["dist_", "measurement_", "point_"]
OTHER_FILE_SUFFIX = ".txt"
SAMPLED_CONFIGURATIONS_FILE = ["sampledConfigurations"]
SAMPLED_CONFIGURATIONS_FILE_SUFFIX = ".csv"
CSV_SEPARATOR = ";"
TOTAL = "total"
SAMPLED_CONFIGURATIONS_STATS_SUFFIX = "_stat"
PERCENT = "%"


def print_usage():
    '''
    Prints the usage of this script.
    '''
    print("Usage: <RunDirectory> <SummaryDirectory>")
    print("RunDirectory\t\t The directory containing the data of all runs.")
    print("SummaryDirectory\t The directory where the average run should be copied to.")


def list_directories(path):
    '''
    Returns the subdirectories of the given path.
    :param path: the path to find the subdirectories from.
    :return: the subdirectories as list.
    '''
    for root, dirs, files in os.walk(path):
        return dirs


def get_specific_files_from_directory(path, prefixes, suffix, contains=None, excludes=None):
    '''
    Returns all files that begin with one of the given prefixes.
    :param path: the path to check the files from
    :param prefixes: the prefixes of the wanted files
    :return: a list containing the files
    '''
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            found = False
            for prefix in prefixes:
                if prefix in file and file.endswith(suffix):
                    found = True
                    break
            if not found:
                continue

            if contains is not None:
                found = False
                for containedString in contains:
                    if containedString in file:
                        found = True
                        break
                if not found:
                    continue

            if excludes is not None:
                skip = False
                for excludedString in excludes:
                    if excludedString in file:
                        skip = True
                        break
                if skip:
                    continue
            result.append(file)
    return result


def add_to_dictionary(dictionary, file_name, number_run, value):
    '''
    Adds the given data to the dictionary.
    :param dictionary: the dictionary to add to
    :param file_name: the file name
    :param number_run: the number of the random seed run
    :param value: the value to add to the dictionary
    '''
    if file_name not in dictionary:
        dictionary[file_name] = {}
    dictionary[file_name][number_run] = value


def add_bucket_to_dictionary(dict, bucket, numberRun, value):
    '''
    Adds the given bucket to the dictionary
    :param dict: the dictionary to add to
    :param bucket: the bucket (key)
    :param numberRun: the number of run
    :param value: the value to add
    '''
    if bucket not in dict:
        dict[bucket] = {}
    dict[bucket][numberRun] = int(value)


def analyze_log_file(path):
    '''
    Analyzes the log files of SPL Conqueror.
    :param path: the path to the log file
    :return: the error rate
    '''
    error_rate = sys.float_info.max
    python_learner = False

    file = open(path, 'r')
    parse_lines = False
    for line in file:
        # if "Models:" in line:
        #    continue;
        if "command: analyze-learning" in line:
            parse_lines = True
        elif "command: learn-python" in line:
            python_learner = True
        elif "command: clean-sampling" in line:
            parse_lines = False
        elif python_learner and "Error rate" in line:
            error_rate = float(line.strip().split(" ")[-1]) * 100
            return error_rate
        elif not python_learner and parse_lines and ";" in line and not "command" in line:
            split_line = line.strip().split(";")
            current_error_rate = float(split_line[len(split_line) - 1])
            if current_error_rate < error_rate:
                error_rate = current_error_rate
    file.close()

    return error_rate


def add_to_sum_dict(dict, file, value):
    '''
    Adds the given value to the dictionary.
    :param dict: the dictionary to add up to
    :param file: the file (key)
    :param value: the value to add
    '''
    if file not in dict:
        dict[file] = 0
    dict[file] += value


def copy_file_content(opened_file, target, run):
    '''
    Copies the file content
    :param opened_file: the file stream
    :param target: the targeted file to read from
    :param run: the run to write
    '''
    target_file = open(target, 'r')
    # Skip the header
    next(target_file)
    for line in target_file:
        opened_file.write(str(run) + ";" + line)
    target_file.close()


def get_header_of(file):
    '''
    Returns the header of the file
    :param file: the file to read the header from
    :return: the header of the file
    '''
    f = open(file, 'r')
    result = next(f)
    return result


def add_values_from_file_to_dict(dictionary, run, file_path):
    ''''
    Reads in the current content of the file into the dictionary
    :param dictionary: the dictionary to save the content of the file into
    :param run: the random seed run
    :param file_path: the path to the file
    '''
    value_file = open(file_path, 'r')

    # Skip the header
    next(value_file)

    # The files have to be written in a csv-like manner, where ';' is taken as element separator and
    # '\n' as row separator
    for line in value_file:
        elements = line.split(';')
        add_bucket_to_dictionary(dictionary, elements[0], run, elements[1])


def convert_dict_to_list(dictionary):
    '''
    Converts the given dictionary to a list.
    :param dictionary: the dictionary to convert
    :return: the dictionary as list
    '''
    result = []
    for key in dictionary.keys():
        result.append(dictionary[key])
    return result


############
#   MAIN   #
############
def main():
    '''
    This is the main method, which (1) gathers and (2) processes the information of all the runs.
    The accumulated information is stored in another directory.
    '''
    if len(sys.argv) != 3:
        print_usage()
        exit(0)

    run_directory = sys.argv[1]
    original_directory = sys.argv[2]

    if not run_directory.endswith(SEPARATOR):
        run_directory = run_directory + SEPARATOR

    if not original_directory.endswith(SEPARATOR):
        original_directory = original_directory + SEPARATOR

    run_statistic = {}

    # Precompute the prefixes of the files to analyze
    prefixes = []
    for type in TYPES:
        prefixes.append(SPL_CONQUEROR_PREFIX + type[:len(type) - 1])
    suffix = ".log"
    name = ""

    sampled_config_contains = ["_rand", "_uni_"]
    sampled_exclude = ["_stat"]

    for case_study in CASE_STUDIES:
        print("Analyzing " + case_study + ".")

        directories = list_directories(run_directory + case_study + SEPARATOR)
        average_values = {}
        for directory in sorted(directories):
            split_name = directory.split("_")
            tmp_name = ""
            print("Scanning " + split_name[len(split_name) - 1] + ". directory.")

            for i in range(0, len(split_name) - 1):
                if i != 0:
                    tmp_name += "_"
                tmp_name += split_name[i]
            name = tmp_name
            number_run = int(split_name[len(split_name) - 1])
            files = get_specific_files_from_directory(run_directory + case_study + SEPARATOR + directory, prefixes,
                                                      suffix)
            for file in sorted(files):
                error = analyze_log_file(run_directory + case_study + SEPARATOR + directory + SEPARATOR + file)
                add_to_sum_dict(average_values, file, error)
                add_to_dictionary(run_statistic, file, number_run, error)

        for key in average_values.keys():
            average_values[key] = average_values[key] / len(run_statistic[key])

        # Retrieve the most average runs, print the error rates into a file
        avg_runs = {}
        best_runs = {}
        worst_runs = {}
        best_score = {}
        worst_score = {}
        standard_deviation = {}
        for file in run_statistic.keys():
            best_score[file] = 1000
            worst_score[file] = 0

            min_deviation = sys.float_info.max

            standard_deviation[file] = 0

            # Save the error rates in the following file (needed for box-plots)
            mid_file_name = file[len(SPL_CONQUEROR_PREFIX):len(file) - len(suffix)]
            error_rate_file = open(original_directory + case_study + os.path.sep + ALL_RESULTS_PREFIX + ERROR_PREFIX + mid_file_name +
                                   OTHER_FILE_SUFFIX, 'w+')
            error_rate_file.write("Run;Error\n")

            for run in run_statistic[file].keys():
                error = run_statistic[file][run]

                # Ignore runs where the error rate is Inf (in C#)
                if error >= 1.79769313486e+308:
                    continue

                if error < best_score[file]:
                    best_score[file] = error
                    best_runs[file] = run
                if error > worst_score[file]:
                    worst_score[file] = error
                    worst_runs[file] = run

                try:
                    standard_deviation[file] += (average_values[file] - error) ** 2
                except:
                    print("Error of run " + str(run) + " too high.")
                    continue

                error_rate_file.write(str(run) + ";" + str(error) + "\n")

                deviation = abs(average_values[file] - error)
                if deviation < min_deviation:
                    min_deviation = deviation
                    avg_runs[file] = run

            error_rate_file.close()

            # Compute the relative standard deviation
            standard_deviation[file] /= len(run_statistic[file].keys())
            standard_deviation[file] = math.sqrt(standard_deviation[file])
            standard_deviation[file] /= average_values[file]

            standard_deviation_file = open(original_directory + case_study + os.path.sep + ALL_RESULTS_PREFIX + STANDARD_DEVIATION_PREFIX +
                                           mid_file_name + OTHER_FILE_SUFFIX, 'w+')
            standard_deviation_file.write(str(standard_deviation[file]) + "\n")
            standard_deviation_file.close()


if "__main__" == __name__:
    main()
