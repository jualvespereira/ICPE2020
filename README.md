# Sampling Effect on Performance Prediction of Configurable Systems: A Case Study (Artifact)

In this repository, we provide general instructions on how to reproduce the results of the paper "Sampling Effect on Performance Prediction of Configurable Systems: A Case Study" and reuse our datasets of measurements.

DOI: [10.5281/zenodo.3614085](https://doi.org/10.5281/zenodo.3614085)

## Overview

![Overview](https://github.com/jualvespereira/ICPE2020/blob/master/overview.png)

In the Figure above, we give an overview of our study.
We replicate a [recent study](https://github.com/se-passau/Distance-Based_Data) through an in-depth analysis of *x264*, a popular and configurable video encoder.
We systematically measure 1,152 configurations of *x264* with 17 different input videos and two quantitative properties (encoding time and encoding size).
Our goal is to understand whether there is a dominant sampling strategy (*e.g.*, random, coverage-based, distance-based) over the very same subject system (*x264*), *i.e.*, whatever the workload and targeted performance properties. 

## Publication

Juliana Alves Pereira, Mathieu Acher, Hugo Martin, Jean-Marc Jézéquel. [Sampling Effect on Performance Prediction of Configurable Systems: A Case Study](https://dl.acm.org/doi/abs/10.1145/3358960.3379137). International Conference on Performance Engineering (ICPE), ACM, April 2020. Pages 277–288. Best paper award.

## Data

In this [repository](https://github.com/jualvespereira/ICPE2020), we provide two directories: [Distance-Based_Data_Time](Distance-Based_Data_Time/) and [Distance-Based_Data_Size](Distance-Based_Data_Size/).
Each directory contains the data related to *time* and *size* prediction, respectively.
They provide two main directories: [MeasuredPerformanceValues](Distance-Based_Data_Time/SupplementaryWebsite/MeasuredPerformanceValues/) and [PerformancePredictions](Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/).

### Measured Performance Values

This directory contains the feature model and measurements of all 17 analysed input videos, namely <img src="http://latex.codecogs.com/gif.latex?x264_0" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_1" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_2" border="0"/>, ..., <img src="http://latex.codecogs.com/gif.latex?x264_{16}" border="0"/>, and a file containing the description of the input video we used to measure all valid configurations. To perform additional experiments related to a new case study *case_x*, the user should add the case-study name *case_x* into the files *SPLConquerorExecuter.py* and *analyzeRuns.py*, and add the files *"FeatureModel.xml"* and *"measurements.xml"* at a new folder *case_x* into the directory <code>Distance-Based_Data_Time/SupplementaryWebsite/MeasuredPerformanceValues/</code> (as an example see these files for x264 case study -- more information about the format of these files can be also found at [SPLConqueror](https://github.com/se-passau/SPLConqueror)).

### Performance Predictions

This directory contains a set of prediction log files with the experiment results (*i.e.*, error rate) of the different sampling approaches and input videos. Each sampling error rate is computed 100 times using different random seeds for each input video.

## Step-by-Step Instructions

Our experiments consists of 2 main steps:
1. performance prediction
2. aggregation and visualization of results

### 1. Performance Prediction

To reproduce our results, we rely on the docker container from the [Distance-Based Sampling repository](https://github.com/se-passau/Distance-Based_Data).
For more information on this conteiner, we refer to their documentation.
To set up the docker container, users must follow the following steps:

- Install [Docker](https://docs.docker.com/install/) (use the command <code>status docker</code> to make sure it is running).

- Download the image: 
<code> docker pull hmartinirisa/icpe2020:latest</code> (by invoking this script, all required ressources are installed, which might take several minutes).

- Run the container:
<code>sudo docker run -it -v "$(pwd)":/docker hmartinirisa/icpe2020 bash</code>

To perform the sampling and learning processes, inside the Docker container, go either to the directory [Distance-Based_Data_Time](Distance-Based_Data_Time/) or [Distance-Based_Data_Size](Distance-Based_Data_Size/).
- <code>cd /ICPE2020/Distance-Based_Data_Time</code> or <code>cd /ICPE2020/Distance-Based_Data_Size</code>

Then, for each <code>\<sampling-approach\></code> (twise, solvBased, henard, distBased, divDistBased, and rand) and <code>\<case-study\></code> (<img src="http://latex.codecogs.com/gif.latex?x264_0" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_1" border="0"/>, <img src="http://latex.codecogs.com/gif.latex?x264_2" border="0"/>, ..., <img src="http://latex.codecogs.com/gif.latex?x264_{16}" border="0"/>), run the following Python script:
- <code>./SPLConquerorExecuter.py \<case-study\> \<sampling-approach\> \<save-location\></code>

The experiments will run for 100 random seeds.
  
#### Files

- <code>learn_\<sampling-approach\>_\<sampling-size\>.a</code>: file containing a list of all input commands used to run SPL Conqueror
- <code>learnAll.a</code>: file containing a super-script to multiple <code>.a-files</code>.
- <code>out_\<sampling-approach\>_\<sampling-size\>.log</code>: file containing the error rate of applying a sampling strategy with a certain sample size on an input video (the error rate is the last number in the last line before *"Analyze finished"*).
- <code>sampledConfigurations_\<sampling-approach\>_\<sampling-size\>.csv</code>: file containing the set of configurations used as sample. This sample set is used as input for the machine-learning technique.
- <code>out_\<sampling-approach\>_\<sampling-size\>.log_error</code>: file containing the error(s) during the execution (if any).


### 3. Aggregation and Visualization of Results

<code>analyzeRuns.py</code> and <code>ErrorRateTableCreator.py</code> are the main scripts to aggregate and visualize the results.
<code>analyzeRuns.py</code> collects all error rates from all 100 runs of all case studies in an unique file <code>all_error_\<sampling-approach\>_\<sampling-size\>.txt</code> (see [diretory](Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/AllSummary/)).
Then, the script <code>ErrorRateTableCreator.py</code> reads the generated file and invokes the <code>R</code> script <code>PerformKruskalWallis.R</code> to perform the significance tests (*e.g.*, Kruskal Wallis, Mann Whitney U) on the collected error rates and automatically create tex-files that are compiled using LaTeX to generate the Tables 2-8 shown in the paper.

- <code>./analyzeRuns.py \<run-directory\> \<output-directory\></code>
- <code>./ErrorRateTableCreator.py \<input-directory\> \<sampling-approaches\> \<labels\> \<output-tex\> </code>
  
<code>\<run-directory\></code> is the directory where all runs of all case studies are stored.
<code>\<output-directory\></code> and <code>\<input-directory\></code> are the directory where the aggregated results should be written to and read from, respectively.
<code>\<sampling-approaches\></code> and <code>\<labels\></code> contain the list of sampling approaches to consider and the labels that should be used in the table.
<code>\<output-tex\></code> contains the directory where the tex-files should be written to.

#### Files

- <code>all_error_\<sampling-approach\>_\<sampling-size\>.txt</code>: file containing the agregated error rates from all 100 runs of all case studies
- <code>\<significance-tests\>Table.tex</code>: multiple different stand alone tex files that contains the summarized tables from the paper. These files can be compiled using LaTeX.

## Usage Example (prediction of time for the input video <img src="http://latex.codecogs.com/gif.latex?x264_0" border="0"/>)

For a better demonstration of the usage, we show it exemplarily for the diversified distance-based samplling approach, the input video <img src="http://latex.codecogs.com/gif.latex?x264_0" border="0"/> and the non-functional property *time* (for 10 random seeds - see final parameters of the command line in step 3).
The location of the measured performance values is [here](Distance-Based_Data_Time/SupplementaryWebsite/MeasuredPerformanceValues/).

1. <code>sudo docker run -it -v "$(pwd)":/docker hmartinirisa/icpe2020 bash</code>
2. <code>cd ICPE2020/Distance-Based_Data_Time</code>
3. <code>./SPLConquerorExecuter.py x264_0 divDistBased /docker/ICPE2020/DistanceBased\_Data\_Time/SupplementaryWebsite/PerformancePredictions/AllExperiments 1 10</code>
4. <code>./analyzeRuns.py /docker/ICPE2020/Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/AllExperiments/ /docker/ICPE2020/Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/AllSummary/</code>
5. Create a folder to store the generated latex files <code>mkdir latex_files</code>
6. <code>./ErrorRateTableCreator.py /docker/ICPE2020/Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/AllSummary/ "twise,solverBased,henard,distBased,divDistBased,random" "Coverage-based,Solver-based,Randomized solver-based,Distance-based,Diversified distance-based,Random" /docker/ICPE2020/Distance-Based_Data_Time/latex_files</code>

In the replication process, the generated error rates (in the local directory <code>/ICPE2020/DistanceBased_Data_Time/SupplementaryWebsite/PerformancePredictions/AllExperiments/x264_0</code>) must be the same as the provided in this [directory](Distance-Based_Data_Time/SupplementaryWebsite/PerformancePredictions/AllExperiments/x264_0) for the diversified distance-based sampling approach, same sample sizes and random seeds (1-10). 
