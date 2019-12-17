#!/usr/bin/env python3

import time
import subprocess
import sys
from typing import List

RUNS_FROM = 1
RUNS_TO = 100
CASE_STUDIES = [("BerkeleyDBC", 1000),
                ("LLVM", 1000),
                ("lrzip", 1),
                ("x264", 1000),
                ("x264_0", 1000),
                ("x264_1", 1000),
                ("x264_2", 1000),
                ("x264_3", 1000),
                ("x264_4", 1000),
                ("x264_5", 1000),
                ("x264_6", 1000),
                ("x264_7", 1000),
                ("x264_8", 1000),
                ("x264_9", 1000),
                ("x264_10", 1000),
                ("x264_11", 1000),
                ("x264_12", 1000),
                ("x264_13", 1000),
                ("x264_14", 1000),
                ("x264_15", 1000),
                ("x264_16", 1000),
                ("Dune", 1),
                ("7z", 1),
                ("Hipacc", 1000),
                ("Polly", 1000),
                ("JavaGC", 1000),
                ("VP9", 1000)
                ]

SCRIPT_LOCATION = "./runRandomHundredTimes.sh"

# The following sampling strategies can be used
# TODO: Add t-wise
ALLOWED_TYPES = ["solvBased", "distBased", "rand", "divDistBased", "henard", "twise"]


def print_usage() -> None:
    print("Usage:")
    print("./SPLConquerorExecuter <caseStudy> <strategy> <saveLocation> [run_start] [run_end]")
    print("caseStudy\t The case study you want to apply sampling and machine learning on.")
    print("strategy\t The sampling strategy you want to apply." +
          "Possible values are solverBased, distanceBased, random, diversified, henard, t-wise")
    print("saveLocation\t The location where the results should be stored")
    print("run_start\t the random run seed to begin with")
    print("run_end\t\t the random run seed to finish with")


def execute_command(command: str) -> str:
    output = subprocess.getstatusoutput(command)
    status_code = output[0]
    message = output[1]

    # Throw an error if the command was not successfully executed
    if (status_code != 0):
        raise RuntimeError(message)

    return message


def main() -> None:
    global RUNS_FROM
    global RUNS_TO
    if (len(sys.argv) < 4 or len(sys.argv) > 6):
        print_usage()
        exit(-1)

    case_study = sys.argv[1]
    sampling_strategy = sys.argv[2]
    save_location = sys.argv[3]

    if (len(sys.argv) >= 5):
        RUNS_FROM = int(sys.argv[4])

    if (len(sys.argv) >= 6):
        RUNS_TO = int(sys.argv[5])

    if sampling_strategy not in ALLOWED_TYPES:
        raise KeyError("The type " + sampling_strategy + " is not allowed.")

    # Check if the case study is valid and derive its multiplication factor
    found = False
    multiplication_factor = 1
    for tuple in CASE_STUDIES:
        if case_study == tuple[0]:
            found = True
            multiplication_factor = tuple[1]
            if case_study == "t-wise":
                RUNS_FROM = 1
                RUNS_TO = 1
            break

    if not found:
        raise KeyError("The case study " + case_study + " is not known.")

    # Executes the SPL Conqueror run
    for run in range(RUNS_FROM, RUNS_TO + 1):
        print("Run " + str(run))
        run_task = SCRIPT_LOCATION + " " + case_study + " " + str(multiplication_factor) + " " + sampling_strategy \
                   + " " + save_location + "/" + case_study + " " + str(run) + " " + str(run)
        print(run_task)
        execute_command(run_task)


if __name__ == "__main__":
    main()
