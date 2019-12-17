[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![DOI](https://zenodo.org/badge/123678830.svg)](https://zenodo.org/badge/latestdoi/123678830)

# Distance-Based Sampling

Distance-based sampling is a novel black-box sampling strategy presented in the paper "Distance-Based Sampling of Software Configuration Spaces" by Christian Kaltenecker, Alexander Grebhahn, Norbert Siegmund, Jianmei Guo, and Sven Apel published at the ICSE 2019.
In this repository, we describe how to reproduce our results of the paper. 

## Overview

![Sketch](https://github.com/ChristianKaltenecker/Distance-Based_Data/raw/master/Sketch.png)

In the Figure above, we give a sketch of the whole workflow.
As input for the workflow, we need a variability model (containing a description of the configuration space of the configurable software system being considered) and the performance measurements for the subject system being considered.
Overall, our approach consists of 3 stages:

**I. Sampling**: 
SPL Conqueror provides different sampling strategies to select a set of configurations from the set of all valid configurations, for which the measured performance values are stored in the raw measurement files.
This sample set is used afterwards as input for the machine-learning technique.
At this point, the distance-based sampling strategy can be used.

**II. Machine Learning**: 
Based on the set of selected configurations, which is done in step I, a performance model is derived.
This model describes the influence of the configuration options of the system on the performance of the configurations of the system.
Overall, using the performance model, the performance of all configurations is predicted.
The difference between the performance predictions and the measured performance values is given by the error rate (located in the log files of SPL Conqueror).

**III. Aggregation (Python scripts)**: To aggregate the prediction errors for the different subject systems when using the different sampling strategies, we provide a set of scripts.

## Data 

In our paper, we use a machine-learning technique to predict the performance of all valid configurations of a configurable software system (i.e., the whole population) from a small set of configurations (i.e., a sample set).
In this process, we distinguish between the following data:
* *Variability Model*: 
  One file containing the description of a configurable system.
  This includes the configuration options of the configurable system and constraints among these configuration options.
* *Measured Performance Values*: 
  One file containing the measured values for all valid configurations of a subject system.
  Here, we have one file per subject system.
* *Prediction Log File*: 
  A file containing the error rate of applying a sampling strategy with a certain sample size on a configurable system.

The data is published in the [Distance-Based Data](https://github.com/ChristianKaltenecker/Distance-Based_Data/tree/master/SupplementaryWebsite) repository.
Overall, in this repository, we provide two directories:

### Measured Performance Values (`MeasuredPerformanceValues`)

In this directory, we provide the (I) variability models of the subject systems, (II) measured performance values, and (III) a file constaining a description of the infrastructre we used to measure all configurations of the systems and the used workload.
The last mentioned file can help a user in replicating the measurements.
However, gathering the measured performance values of the configuration took several months of CPU time, in the first place. 
Additionally, some of the identified perfomance characteristrics might be affected by hardware-speficic characteristics, which overall requires to perform the measurements on the same hardware using the same operating system and so on.

### Prediction Log File (`PerformancePredictions`)

In this directory, we provide files containing the predicted performance values of all configurations of the different subject systems, when using a specific sampling strategy.
Since using a random seed in all sampling strategies (except for t-wise) leads to different sample sets and in this vein also to slightly different predicion errors, we have performed the experiments using these sampling strategies 100 times using different seeds.
To examine the influence of these random seeds on the prediction accuracy, we provide one file for each random seed.

## Programs & Scripts

Next, we describe the tools and scripts used in this study and how they interplay.

### SPL Conqueror
The distance-based sampling strategy was implemented in [SPL Conqueror](https://github.com/se-passau/SPLConqueror), which is a library that provides implementations of all sampling strategies considered in the paper, as well as the used implementation of the applied machine-learning technique (multiple linear regression in combination with forward feature selection).
In the sampling and the learning provess, we depend only on SPL Conqueror.

### Scripts

To process the predicted performance values when using a specific sampling strategy and to automatically generate the tables shown in the paper (see for example Table II, we provide Python scripts for data aggregation, which further invokes an R script to perform the significance tests from which the results are shown in Table 3.
Overall, these scripts create stand alone tex files that can be compiled using LaTeX.

## Installation

For reproduction of our results, we provide a docker container containing scripts for the installation, alternatively, we also provide a description for a [manual setup](#manual-setup) showing the steps to perform on a Linux-based operating system to repoduce the results of this work. 

### Setup via Dockerfile

To ease the installation of our tool, we provide a [Dockerfile](./Dockerfile) for setting up a docker container.
Please note that the container will use up to 5 GB of disc storage after the setup is performed.

To apply this file, we rely on docker and refer to the [documentation](https://docs.docker.com/install/linux/docker-ce/ubuntu/) on how to install docker on your Linux operating system.

After docker is installed, make sure that the docker daemon is running. On systemd, you can use ```systemctl status docker``` to check the status of the daemon and ```sudo systemctl start docker``` to start the daemon, if necessary.

Next, download the [Dockerfile](./Dockerfile).
The container is set up by invoking ```sudo docker build -t distance-based ./``` in the directory where the Dockerfile is located.
By invoking this script, all dependencies as described in Section [Manual Setup](#manual-setup) are installed, which might take several minutes.

After setting up the docker container, all required ressources (i.e., packages, programs, and scripts) are installed and can now be used inside the container.
To begin an interactive session, the command ```sudo docker run -i -t distance-based /bin/bash``` can be used.
After starting the interactive session, you can continue [here](#usage).


### Manual Setup

Requirements:
  * Operating system: Ubuntu/Debian
  * Mono (for running SPL Conqueror)
  * git (for cloning the required repositories)
  * wget
  * unzip, tar
  * texlive (for generating the summarized table from the paper)
  * Python (for the aggregation of the results):
    * numpy
    * scipy
  * R (for the significance tests -- the dependencies are installed via the provided `InstallPackages.R` script)
    * FSA
    * car
    * effsize

#### Data

To clone the repository containing the data (variability models, measured performance values, and predicted performance values), use the following command:

```
git clone https://github.com/ChristianKaltenecker/Distance-Based_Data.git
```

Since the measured performance values of JavaGC and VP9 are compressed because of size restrictions, they have to be uncompressed by using `tar` with the following commands:

```
tar -xzf Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/JavaGC/measurements.tar.gz -C Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/JavaGC/
tar -xzf Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/VP9/measurements.tar.gz -C Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/VP9/
```

#### SPL Conqueror

Since we used a specific version of SPL Conqueror in our paper, and we can not make sure to achieve the same results in all version of SPL Conqueror in the future, additional steps are required to reset the repository to the version used in the paper.
```
git clone https://github.com/se-passau/SPLConqueror.git
cd SPLConqueror
git reset --hard 8d5e442f0e085f8df6d7807ca69c65deeae7e0b3
```

SPL Conqueror is written in C# and, thus, depends on [Mono](https://www.mono-project.com/) and [NuGet](https://www.nuget.org/) to install further packages needed to perform the experiments.
The Mono packages are downloaded by the use of a package manager, such as `apt`:
```
sudo apt install -y mono-complete
```
The current version of NuGet is downloaded by using the command:
```
cd SPLConqueror
wget https://dist.nuget.org/win-x86-commandline/latest/nuget.exe 
``` 

After cloning the repository with the given version, SPL Conqueror has to be built. This is done by using the following commands:
```
mono nuget.exe restore ./
xbuild /p:Configuration=Release /p:TargetFrameworkVersion="v4.5" /p:TargetFrameworkProfile="" ./SPLConqueror.sln
cd ../../
```

#### z3 Constraint solver

In our experiments, we rely on a satisfiability solver to navigate through the highly constained configuration space of the subject systems in an efficient way. 
Here, we use the [z3](https://github.com/Z3Prover/z3) constraint solver, which has to be downloaded.
This is done as follows:
```
wget https://github.com/Z3Prover/z3/releases/download/z3-4.7.1/z3-4.7.1-x64-debian-8.10.zip
unzip z3-4.7.1-x64-debian-8.10.zip -d z3
rm z3-4.7.1-x64-debian-8.10.zip
mv z3-4.7.1-x64-debian-8.10/bin/libz3.so /usr/lib/libz3.so
```

#### Scripts

To execute the scripts, we rely on [python3](https://www.python.org/download/releases/3.0/) and [R](https://www.r-project.org/).
They can be installed on Debian using `apt` as follows:
```
sudo apt install -y python3 python3-numpy python3-scipy r-recommend
```
For the installation of the dependencies for R, we provide an installation file, which is be invoked as follows:
```
Rscript InstallPackages.R
```
Please be aware that this installation process might take a while.


## Usage

Please note that we consider subject systems from different size. 
As a consequence, the replication of the results for different systems will take different amount of time.
We advise you to take a look on the performance values on the [supplementary website](https://github.com/ChristianKaltenecker/Distance-Based_Data/tree/master/SupplementaryWebsite) to simplify the decision on which results to replicate.
For a better demonstration of the usage, we show it exemplarily for the subject system x264.

The location of the measured performance values is ```Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues```

### Replication of a random seed

The following commands have to be executed inside the repository "Distance-Based_Data" to reproduce the sampling and the subsequent learning process when using a specific random seed.
```
cd Distance-Based_Data/
```
To execute the sampling and machine-learning process, we provide the script SPLConquerorExecuter.py.
```
./SPLConquerorExecuter.py <subjectSystem> <strategy> <saveLocation> [run_start] [run_end]
```
Here, valid arguments for the *subject system* are ```7z```, ```BerkeleyDBC```, ```Dune```, ```Hipacc```, ```JavaGC```, ```lrzip```, ```LLVM```, ```Polly```, ```VP9```, ```x264```. 
For the samplingStrategy, we provide the following arguments twise (coverage-based), solvBased (solver-based), henard (randomized solver-based), distBased (distance-based), divDistBased (diversified distance-based), rand (random).
The third argument specified the directory, where the results of the SPL Conqueror execution are stored.
The last two arguments can be used to specific a specific set of random seeds, for which the experiments have to be performened.
Additionally, if not all 100 random seeds should be used in the experiments, the interval of the random seed can be specified.

In our example, we first create a new directory for storing the new results.
```
mkdir -p /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/NewRuns
```
Afterwards, we can use the script to perform the diversified distance-based sampling for the subject system x264 by using the random seeds 42-43.
```
./SPLConquerorExecuter.py x264 divDistBased /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/NewRuns 42 43
```
By executing this script, new directories inside of the *saveLocation* are created for the subject system and the specified random seed.
The structure of the directories looks as follows:
  * run directory (e.g., NewRuns)
    * subject system (e.g., x264)
      * subject system with random seed (e.g., x264_42)
        * SPL Conqueror log files for a sampling strategy and different sample sizes (e.g., out_diversified_t1.log)
        * A file constaining the set of selected configurations. (e.g., sampledConfigurations_diversified_t1.csv)

To compare the results, one have to compare the results of (1) the same subject system using (2) the same sampling strategy, (3) the same random seed, and (4) the same sample size.
The results are compared by comparing error rates. 

In our example, we compare the error rates of (1) x264 using (2) diversified samplig, (3) random seed 42, and (4) sample sizes t1, t2, and t3.
Therefore, we compare the following SPL Conqueror log files:

| Provided Execution File| Replicated Execution File | 
| ---------------------- | -------------------------- |
| /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/AllRuns/x264/x264_42/out_divDistBased_t1.log |  /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/NewRuns/x264/x264_42/out_divDistBased_t1.log |
| /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/AllRuns/x264/x264_42/out_divDistBased_t2.log |  /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/NewRuns/x264/x264_42/out_divDistBased_t2.log |
| /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/AllRuns/x264/x264_42/out_divDistBased_t3.log |  /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/NewRuns/x264/x264_42/out_divDistBased_t3.log |

In these log files, the error rate is the last number in the last line before `Analyze finished`.
In the following example, the error rate is 10.481%.
``` 
[...]
3;472.586666666666 * no_asm + -29.8533333333331 * no_mixed_refs + -212.187499999999 * ref_1 + 214.236666666666 * ref_9;5.75863710582891;5.75863710582891;5.75863710582891;5.75863710582891;0.05085;4;214.236666666666 * ref_9;1;7.31333436817488;10.4810287299971
Analyze finished
[...]
```
In the replication process, the error rates of the replication must be the same as the provided ones.

### Aggregation

For the aggregation of our results, we provide two scripts:

**I. analyzeRuns.py**: 
  A script that collects all relevant information about the runs of all case studies and stores it in a given directory.
  Usage: `./analyzeRuns.py <runDirectory> <summaryDirectory>`
  `runDirectory` is the directory where all runs of all case studies are stored. 
  `summaryDirectory` is the directory where the accumulated results should be written to.

  In our example, we aggregate the results of `AllRuns` and write them into `Summary`:
  ```
  ./analyzeRuns.py /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/AllRuns/ /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/Summary/
  ```
**II. ErrorRateTableCreator.py**:
  A script that reads the information gathered by `analyzeRuns.py` and uses `PerformKruskalWallis.R` to perform the significance tests (e.g., Kruskal Wallis, Mann Whitney U) on the collected error rates.
  The results are written in multiple different table files.
  Usage: `./ErrorRateTableCreator.py <inputDirectory> <typesToAdd> <labelsOfTypes> <outputDirectory>`

  `inputDirectory` the directory containing the summary files.

  `typesToAdd` the sampling file labels to add (e.g., distBased, divDistBased).

  `lablesOfTypes` the labels of the sampling strategies that should be used in the table (e.g., Distance-based, Diversified distance-based). Please be aware that the order of the arguments has to be the same as in `typesToAdd`.

  `outputDirectory` the directory where the tex files should be written to.

  In our example, we use the aggregated results of all sampling strategies.
  ```
  ./ErrorRateTableCreator.py /application/Distance-Based_Data/SupplementaryWebsite/PerformancePredictions/Summary/ "twise,solvBased,henard,distBased,divDistBased,rand" "Coverage-based,Solver-based,Randomized solver-based,Distance-based,Diversified distance-based,Random" /application/Distance-Based_Data
  ```

  Afterwards, `pdflatex` and the file `TableStandalone.tex` should be used to create the table.
  ```
  pdflatex TableStandalone.tex
  ```
