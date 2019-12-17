# Sampling Effect on Performance Prediction of Configurable Systems: A Case Study (Artifact)

In this repository, we provides general instructions of how to reproduce the results of the paper "Sampling Effect on Performance Prediction of Configurable Systems: A Case Study" and reuse the datasets.

# Overview

![Overview](https://github.com/jualvespereira/ICPE2020/blob/master/overview.png)

In the Figure above, we give an overview of our study.
We replicate a recent study [recent study](https://github.com/se-passau/Distance-Based_Data) through an in-depth analysis of x264, a popular and configurable video encoder.
We systematically measure 1,152 configurations of x264 with 17 different input videos and two quantitative properties (encoding time and encoding size).
Our goal is to understand whether there is a dominant sampling strategy (e.g., random, coverage-based, distance-based) over the very same subject system (x264), i.e., whatever the workload and targeted performance properties. 

# Data

The data is published in this [repository](https://github.com/jualvespereira/ICPE2020).
Overall, in this repository, we provide two directories: "Distance-Based_Data_Time" and "Distance-Based_Data_Size".
Each directory contains the data related to time and size prediction, respectively.
They provide two main directories: "MeasuredPerformanceValues" and "PerformancePredictions"

### Measured Performance Values

This directory contains the feature model and measurements of all seventeen analysed input videos, namely x264_0, x264_1, x264_2, ..., x264_16, and a file containing the description of the input video we used to measure all valid configurations. To perform additional experiments, the user can add the corresponding files to a new case study (more information about the format of these files can be found at [SPLConqueror](github.com/se-passau/SPLConqueror).

### Performance Predictions

This directory contains a set of prediction log files with the experiment results (i.e., error rate) of the different sampling approaches and input videos. Each sampling error rate is computed 100 times using different random seeds for each input video.

# Step-by-Step Instructions

Overall, our experiments consists of 3 main steps:
1. clone dependent repositories
2. performance prediction
3. aggregation and visualization of results

### 1. Dependencies

The implementation depends on the [SPLConqueror](github.com/se-passau/SPLConqueror) for sampling and learning, and on the [z3 Constraint solver](https://github.com/Z3Prover/z3.git) library to navigate through the configuration space of the subject system. These libraries need to be downloaded with the command lines:

- git clone https://github.com/se-passau/SPLConqueror.git
- git clone https://github.com/Z3Prover/z3.git

### 2. Performance Prediction

To reproduce our results, we rely on the docker container from [Distance-Based_Data](https://github.com/se-passau/Distance-Based_Data).
For more information on this conteiner, we refer to the [documentation](https://github.com/se-passau/Distance-Based_Data).
To set up the docker container, users must follow the following steps:

- Install [Docker](https://docs.docker.com/install/). Then, make sure it is running (use <code>status docker</code>).

- Download the container: 
<code> docker pull christiankaltenecker/distance-based:latest</code>.
By invoking this script, all required ressources are installed, which might take several minutes.

- Run the container:
<code>sudo docker run -it -v "$(pwd)":/docker christiankaltenecker/distance-based bash</code>

To clone the main repository containing the data used in our experiments, use the following command:
<code> git clone https://github.com/jualvespereira/ICPE2020.git</code>

To perform the sampling and learning process, inside the Docker container, go either to the directory "Distance-Based_Data_Time" or "Distance-Based_Data_Size".
Then, for each sampling approach (twise, solvBased, henard, distBased, divDistBased, and rand) and case-study (x2640, x2641,..., x26416), run the following Python script:
<code>./SPLConquerorExecuter.py <case-study> <sampling-approach> <save-location></code>
The experiments will run for 100 random seeds.
  
#### Files




### 3. Aggregation and Visualization of Results

analyzeRuns.py and ErrorRateTableCreator.py are the main scripts to aggregate and visualize the results.
analyzeRuns.py collects all error rates from all 100 runs of all case studies in an unique file "all_error_distBased_t1.txt" (see diretory <code>SupplementaryWebsite/PerformancePredictions/AllSummary</code>).
Then, the script ErrorRateTableCreator.py reads the generated file and invokes the R script PerformKruskalWallis.R to perform the significance tests and automatically create tex files that are compiled using LaTeX to generate the Tables 2-8 shown in the paper (i.e., the output tex-files).

- <code>./analyzeRuns.py <run-directory> <output-directory></code>
- Install the dependencies for R: <code>InstallPackages.R</code>. Please be aware that this installation process might take a while.
- <code>./ErrorRateTableCreator.py <input-directory> <sampling-approaches> <labels> <output-tex></code>

run-directory is the directory where all runs of all case studies are stored. output-directory and input-directory are the directory where the aggregated results should be written to and read from, respectively. sampling-approaches and labels contains the list of sampling approaches to consider and the labels that should be used in the table. output-tex contains the directory where the tex-files should be written to.


#### Files





# Usage Example (prediction of time for the input video x264_0)

For a better demonstration of the usage, we show it exemplarily for the subject system x264_0 and the non-functional property time.

The location of the measured performance values is <code>Distance-Based_Data_Time/SupplementaryWebsite/MeasuredPerformanceValues</code>.

create a new directory for storing the new results.
<code mkdir -p /application/Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/NewRuns</code>

Afterwards, we can use the script to perform the diversified distance-based sampling approach for the input video x264_0

Comand?

In the replication process, the error rates of the replication must be the same as the provided ones.
Then, we compare the error rates of x264_0 using (2) diversified samplig, (3) random seed 0, and (4) sample sizes t1, t2, and t3. 




-----------------------------
I. Sampling: SPL Conqueror provides different sampling strategies to select a set of configurations from the set of all valid configurations, for which the measured performance values are stored in the raw measurement files. 

II. Machine Learning: Based on the set of selected configurations, which is done in step I, a performance model is derived. This model describes the influence of the configuration options of the system on the performance of the configurations of the system. Overall, using the performance model, the performance of all configurations is predicted. The difference between the performance predictions and the measured performance values is given by the error rate (located in the log files of SPL Conqueror).

These sampling approaches propose to measure a small and representative set of configurations that leads to a good accuracy of performance prediction models. only a few configurations to learn and predict the performance of any combination of options’ values. 
