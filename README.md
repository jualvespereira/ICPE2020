# Sampling Effect on Performance Prediction of Configurable Systems: A Case Study (Artifact)

In this repository, we provides general instructions of how to reproduce the results of the paper "Sampling Effect on Performance Prediction of Configurable Systems: A Case Study" and reuse our datasets of measurements.

## Overview

![Overview](https://github.com/jualvespereira/ICPE2020/blob/master/overview.png)

In the Figure above, we give an overview of our study.
We replicate a [recent study](https://github.com/se-passau/Distance-Based_Data) through an in-depth analysis of x264, a popular and configurable video encoder.
We systematically measure 1,152 configurations of x264 with 17 different input videos and two quantitative properties (encoding time and encoding size).
Our goal is to understand whether there is a dominant sampling strategy (*e.g.*, random, coverage-based, distance-based) over the very same subject system (x264), *i.e.*, whatever the workload and targeted performance properties. 

## Data

In this [repository](https://github.com/jualvespereira/ICPE2020), we provide two directories: [Distance-Based_Data_Time](Distance-Based_Data_Time/) and [Distance-Based_Data_Size](Distance-Based_Data_Size/).
Each directory contains the data related to *time* and *size* prediction, respectively.
They provide two main directories: [MeasuredPerformanceValues](Distance-Based_Data_Time/SupplementaryWebsite/MeasuredPerformanceValues/) and [PerformancePredictions](Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/).

### Measured Performance Values

This directory contains the feature model and measurements of all 17 analysed input videos, namely <img src="http://latex.codecogs.com/gif.latex?x264_0" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_1" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_2" border="0"/>, ..., <img src="http://latex.codecogs.com/gif.latex?x264_{16}" border="0"/>, and a file containing the description of the input video we used to measure all valid configurations. To perform additional experiments related to a new case study, the user can add the corresponding files at this directory (more information about the format of these files can be found at [SPLConqueror](github.com/se-passau/SPLConqueror)).

### Performance Predictions

This directory contains a set of prediction log files with the experiment results (*i.e.*, error rate) of the different sampling approaches and input videos. Each sampling error rate is computed 100 times using different random seeds for each input video.

## Step-by-Step Instructions

Our experiments consists of 3 main steps:
1. clone dependent repositories
2. performance prediction
3. aggregation and visualization of results

### 1. Dependencies

The implementation depends on the [SPLConqueror](github.com/se-passau/SPLConqueror) for sampling and learning, and on the [z3 Constraint solver](https://github.com/Z3Prover/z3.git) library to navigate through the configuration space of the subject system. These libraries need to be downloaded with the command lines:

- <code>git clone https://github.com/se-passau/SPLConqueror.git</code>
- <code>git clone https://github.com/Z3Prover/z3.git</code>

### 2. Performance Prediction

To reproduce our results, we rely on the docker container from the [Distance-Based Sampling repository](https://github.com/se-passau/Distance-Based_Data).
For more information on this conteiner, we refer to their documentation.
To set up the docker container, users must follow the following steps:

- Install [Docker](https://docs.docker.com/install/) (use the command <code>status docker</code> to make sure it is running).

- Download the container: 
<code> docker pull christiankaltenecker/distance-based:latest</code> (by invoking this script, all required ressources are installed, which might take several minutes).

- Run the container:
<code>sudo docker run -it -v "$(pwd)":/docker christiankaltenecker/distance-based bash</code>

To clone the main repository containing the data used in our experiments, use the following command:
- <code> git clone https://github.com/jualvespereira/ICPE2020.git</code>

To perform the sampling and learning process, inside the Docker container, go either to the directory [Distance-Based_Data_Time](Distance-Based_Data_Time/) or [Distance-Based_Data_Size](Distance-Based_Data_Size/).
Then, for each <code>sampling-approach</code> (twise, solvBased, henard, distBased, divDistBased, and rand) and <code>case-study</code> (<img src="http://latex.codecogs.com/gif.latex?x264_0" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_1" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_2" border="0"/>, ..., <img src="http://latex.codecogs.com/gif.latex?x264_{16}" border="0"/>), run the following Python script:
- <code>./SPLConquerorExecuter.py \<case-study\> \<sampling-approach\> \<save-location\></code>

The experiments will run for 100 random seeds.
  
#### Files




### 3. Aggregation and Visualization of Results

<code>analyzeRuns.py</code> and <code>ErrorRateTableCreator.py</code> are the main scripts to aggregate and visualize the results.
<code>analyzeRuns.py</code> collects all error rates from all 100 runs of all case studies in an unique file <code>all_error_\<sampling-approach\>_\<sampling-size\>.txt</code> (see [diretory](Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/AllSummary/)).
Then, the script <code>ErrorRateTableCreator.py</code> reads the generated file and invokes the <code>R</code> script <code>PerformKruskalWallis.R</code> to perform the significance tests and automatically create tex-files that are compiled using LaTeX to generate the Tables 2-8 shown in the paper.

- <code>./analyzeRuns.py \<run-directory\> \<output-directory\></code>
- Install the dependencies for R: <code>InstallPackages.R</code> 
- <code>./ErrorRateTableCreator.py \<input-directory\> \<sampling-approaches\> \<labels\> \<output-tex\> </code>
  
<code>run-directory</code> is the directory where all runs of all case studies are stored.
output-directory and input-directory are the directory where the aggregated results should be written to and read from, respectively.
sampling-approaches and labels contain the list of sampling approaches to consider and the labels that should be used in the table.
output-tex contains the directory where the tex-files should be written to.
