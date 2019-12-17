#!/usr/bin/env python3

import sys
import os
import math
from scipy import stats
from typing import List, Dict, Tuple
import copy
from statistics import stdev
import numpy as np

# Needed for temporary directory
import tempfile

# Needed to execute the R-scripts
import subprocess

# The constants
SEPARATION_SIGN = ","
ERROR_FILE_PREFIX = "all_error_"
ERROR_FILE_SUFIX = ".txt"
LOG_FILE_PREFIX = "out_"
LOG_FILE_SUFIX = ".log"
FILE_NAME_SEPARATOR = "_"
T_PARAMETER = [1,2,3]
CSV_SEPARATOR = ";"
PERCENT = "\\percent "
NEW_LINE = "\\\\"

BEST_FORMAT_PREFIX = "\\textbf{\\color{Green}"
BEST_FORMAT_SUFIX = "} "

SECOND_FORMAT_PREFIX = "{\\color{Blue}\\underline{"
SECOND_FORMAT_SUFIX = "}} "

CASE_STUDY_MAPPING = {"7z" : "7z", "BerkeleyDBC" : "BDB-C", "Dune" : "Dune",
                      "Hipacc" : "Hipacc", "JavaGC" : "JavaGC", "Polly" : "Polly",
                      "VP9" : "VP9"}

EXCLUDED_DIRECTORIES = ["SinglePlots"]#, "VP9_disc", "JavaGC_disc", "Hipacc_disc", "Polly_disc"]
FIRST_COLUMN_FORMAT = "e"
OTHER_COLUMN_FORMAT = "abd"

TO_IGNORE_RQ1 = ["rand"]
TO_IGNORE_RQ2 = ["twise"]


def printUsage():
    print("Usage: <inputDirectory> <typesToAdd> <labelsOfTypes> <outputDir>")
    print("inputDirectory\t The directory containing all information for the subject systems.")
    print("typesToAdd\t A comma-separated list containing the types (e.g., uni, rand, semi)" +
          " that should be displayed in the table.")
    print("labelsOfTypes\t A comma-separated list containing the labels " +
          "(e.g., distribution-aware, random sampling, semi-random sampling) that should be shown on the header.")
    print("outputDir\t The .tex-file where the table should be written to.")


def roundError(numberAsFloat):
    return int(numberAsFloat * 10) / 10


def retrieveAllRelevantDirectories(inputDir):
    subfolders = [f.path for f in os.scandir(inputDir)
                  if f.is_dir() and f.name not in EXCLUDED_DIRECTORIES and "_norm" not in f.name]
    return subfolders


def computeMeanError(filePath):
    avgError = 0
    allValues = []
    count = 0
    if (not os.path.exists(filePath)):
        return math.nan, allValues
    with open(filePath, 'r') as file:
        file.readline()
        for line in file:
            count += 1
            value = float(line.split(CSV_SEPARATOR)[1])
            avgError += value
            allValues.append(value)
        avgError /= count
    return avgError, allValues


def readTWiseLogFile(filePaths):
    result = {}
    for filePath in filePaths:
        accuracy = -1
        currentTParameter = -1
        with open(filePath, 'r') as file:
            analyzeLearning = False
            for line in file:
                if ("command:" in line):
                    if "clean-sampling" in line:
                        result[currentTParameter] = accuracy
                        analyzeLearning = False
                        currentTParameter = -1
                    elif "analyze-learning" in line:
                        analyzeLearning = True
                    elif " twise " in line:
                        tmp = line.split(" ")
                        tmp = tmp[len(tmp) - 1].replace("\n", "")
                        currentTParameter = int(tmp.split(":")[1])
                elif analyzeLearning and CSV_SEPARATOR in line:
                    tmp = line.split(CSV_SEPARATOR)
                    currentAccuracy = float(tmp[len(tmp) - 1])
                    if accuracy == -1 or currentAccuracy < accuracy:
                        accuracy = currentAccuracy
    return result


def addNewLine(listOfStrings):
    newList = []
    for element in listOfStrings:
        newList.append(element + "\n")
    return newList


def gatherInformation(inputDirectories, typesToAdd):
    result = {}
    allResults = {}
    for inputDirectory in inputDirectories:
        caseStudy = os.path.basename(inputDirectory)
        result[caseStudy] = {}
        allResults[caseStudy] = {}
        for type in typesToAdd:
            if (type == "twise"):
                filePaths = [os.path.join(inputDirectory, LOG_FILE_PREFIX + type + "_t1" + LOG_FILE_SUFIX),
                             os.path.join(inputDirectory, LOG_FILE_PREFIX + type + "_t2" + LOG_FILE_SUFIX),
                             os.path.join(inputDirectory, LOG_FILE_PREFIX + type + "_t3" + LOG_FILE_SUFIX)]
                result[caseStudy][type] = readTWiseLogFile(filePaths)
                allResults[caseStudy][type] = dict(result[caseStudy][type])
                for t in T_PARAMETER:
                    allResults[caseStudy][type][t] = [allResults[caseStudy][type][t]] * 100
            else:
                result[caseStudy][type] = {}
                allResults[caseStudy][type] = {}
                for t in T_PARAMETER:
                    # The t-wise error rate has to be read from the .log-file
                    filePath = os.path.join(inputDirectory, ERROR_FILE_PREFIX + type + FILE_NAME_SEPARATOR + "t" + str(t) +
                                            ERROR_FILE_SUFIX)
                    avgValue, allValues = computeMeanError(filePath)
                    result[caseStudy][type][t] = avgValue
                    allResults[caseStudy][type][t] = allValues
    return result, allResults


def createRanking(typeInformation, allInformation, typesToAdd, toExclude = None):
    result = {}
    for caseStudy in sorted(typeInformation.keys()):
        result[caseStudy] = {}
        for t in T_PARAMETER:
            errorList = []
            allRunsList = []
            for type in typesToAdd:
                if (toExclude is not None and type in toExclude):
                    errorList.append(math.nan)
                else:
                    errorList.append(typeInformation[caseStudy][type][t])
                allRunsList.append(allInformation[caseStudy][type][t])

            result[caseStudy][t] = rankList(errorList, allRunsList)
    return result


def rankList(listToRank, allRuns):
    # NaN receives the highest value in the comparison
    order = sorted(listToRank, key=lambda x : float('inf') if math.isnan(x) else x)

    ranking = list(listToRank)
    for i in range(0, len(listToRank)):
        ranking[i] = order.index(listToRank[i]) + 1

    # Perform the t-test pair-wise on the non-nan entries
    entriesToConsider = list(filter(lambda a: not math.isnan(order[a]), map(lambda a: order.index(a), order)))

    # Correct the p-value
    #new_pvalue = 0.05 / (math.factorial(len(entriesToConsider)) / (math.factorial(2) * math.factorial(len(entriesToConsider) - 2)))

    #for firstEntry in entriesToConsider:
    #    otherEntries = entriesToConsider[entriesToConsider.index(firstEntry):]
    #    for secondEntry in otherEntries:
            # After creating the ranking, a t-test is performed on the best two runs.
    firstToCompare = allRuns[ranking.index(1)]

    # find the second rank (which can be 2 or a larger number)
    tmpRank = list(ranking)
    tmpRank.remove(1)
    reducedRanking = sorted(list(set(tmpRank)))
    secondToCompare = allRuns[ranking.index(reducedRanking[reducedRanking.index(min(reducedRanking))])]

    if len(firstToCompare) == 1:
        firstToCompare = firstToCompare * len(secondToCompare)
    elif len(secondToCompare) == 1:
        secondToCompare = secondToCompare * len(firstToCompare)

    _, pvalue = stats.mannwhitneyu(firstToCompare, secondToCompare)
        #stats.ttest_ind(firstToCompare, secondToCompare, equal_var=False)


    if pvalue > 0.05:
        ranking[ranking.index(1)] = 2


    return ranking


def sortByFirstLowerLetter(str: str) -> str:
    return str[0].lower()


def computeMeanValue(typesToAdd, allInformation, toExclude):
    means = {}
    count = {}
    typeResults = {}
    meanRanking = {}
    for t in T_PARAMETER:
        typeResults[t] = []
        means[t] = []
        count[t] = []
        for i in range(0, len(typesToAdd)):
            type = typesToAdd[i]
            typeResults[t].append([])
            means[t].append(0)
            count[t].append(0)
            for caseStudy in sorted(allInformation):
                for result in allInformation[caseStudy][type][t]:
                #result = allInformation[caseStudy][type][t]
                    typeResults[t][i].append(result)
                    means[t][i] += result
                    count[t][i] += 1
            means[t][i] /= count[t][i]

    # Remove the comparison to the random sampling strategy
    meansCopy = copy.deepcopy(means)
    for t in T_PARAMETER:
        for i in range(0, len(typesToAdd)):
            type = typesToAdd[i]
            if (toExclude is not None and type in toExclude):
                meansCopy[t][i] = math.nan

        meanRanking[t] = rankList(meansCopy[t], typeResults[t])
    return means, meanRanking


def writeTableToFile(outputFile, labelsOfTypes, typesToAdd, typeInformation, ranking, means = None, meanRanking = None, toExclude = None):
    # Write to the specified file
    file = open(outputFile, 'w')

    columns = FIRST_COLUMN_FORMAT
    header = "\t\t"
    midrules = "\t\t"
    tLabelLine = "\t\t"
    spaceBetweenCaseStudies = "\t\t"
    meanSeparator = "\\midrule\\multicolumn{" + str(len(labelsOfTypes) * len(T_PARAMETER) + 1) + "}{c}{\\cellcolor{white}} \\\\[-0.1cm]\\midrule"

    for i in range(0, len(labelsOfTypes)):
        columns += OTHER_COLUMN_FORMAT[0:len(T_PARAMETER)]

        if (len(T_PARAMETER) == 1):
            header += "&" + labelsOfTypes[i]
            midrules = "\\midrule"
        else:
            header += "& \\multicolumn{" + str(len(T_PARAMETER)) + "}{c}{" + labelsOfTypes[i] + "}"
            if (i < len(labelsOfTypes) - 1 and "rand" in labelsOfTypes[i + 1]):
                midrules += "\\cmidrule(lr{1.3em}){" + str(i * 3 + 2) + "-" + str(i * 3 + 4) + "} "
            else:
                midrules += "\\cmidrule(lr){" + str(i * 3 + 2) + "-" + str(i * 3 + 4) + "} "
        for j in T_PARAMETER:
            tLabelLine += "& $t=" + str(j) + "$"
            spaceBetweenCaseStudies += "& "
    header += NEW_LINE
    tLabelLine += NEW_LINE + "[0.1cm] "#\\midrule"
    spaceBetweenCaseStudies += NEW_LINE

    # Write the header of the table
    file.writelines(addNewLine(["\\begin{adjustbox}{angle=0}",
                     "\t\\begin{tabular}{" + columns + "}",
                     "\t\\toprule",
                     header,
                     midrules]))
    if (len(T_PARAMETER) > 1):
        file.writelines(addNewLine([tLabelLine,
                     spaceBetweenCaseStudies + "[-0.2cm]"]))

    # Write the results of every case study
    caseStudyLines = []
    for caseStudyDirectory in sorted(typeInformation.keys(), key = sortByFirstLowerLetter):
        caseStudyLine = "\t\t"
        if caseStudyDirectory in CASE_STUDY_MAPPING:
            caseStudyLine += CASE_STUDY_MAPPING[caseStudyDirectory]
        else:
            caseStudyLine += caseStudyDirectory

        for type in typesToAdd:
            for t in T_PARAMETER:
                if math.isnan(typeInformation[caseStudyDirectory][type][t]):
                    resultToPrint = "--"
                else:
                    resultToPrint = str(roundError(typeInformation[caseStudyDirectory][type][t])) + PERCENT

                if (ranking is None or ranking[caseStudyDirectory][t][typesToAdd.index(type)] > 1):
                    caseStudyLine += "&" + resultToPrint
                # elif (ranking[caseStudyDirectory][t][typesToAdd.index(type)] == 2):
                #     caseStudyLine += "&" + SECOND_FORMAT_PREFIX + \
                #                      resultToPrint + \
                #                      SECOND_FORMAT_SUFIX
                else:
                    caseStudyLine += "&" + BEST_FORMAT_PREFIX + \
                                     resultToPrint + \
                                     BEST_FORMAT_SUFIX
        caseStudyLine += NEW_LINE
        caseStudyLines.append(caseStudyLine)
        caseStudyLines.append(spaceBetweenCaseStudies + "[-0.3cm]")

    # Remove the last space, as it is not needed
    caseStudyLines = caseStudyLines[0:len(caseStudyLines) - 1]

    if (means is not None and meanRanking is not None):
        # Add a line for the mean values and their ranking
        #caseStudyLines.append(meanSeparator)
        meanLine = "Mean "

        for type in typesToAdd:
            for t in T_PARAMETER:
                resultToPrint = str(roundError(means[t][typesToAdd.index(type)])) + PERCENT
                if (meanRanking[t][typesToAdd.index(type)] > 1):
                    meanLine += " & " + resultToPrint
                else:
                    meanLine += " & " + BEST_FORMAT_PREFIX + resultToPrint + BEST_FORMAT_SUFIX
        meanLine += NEW_LINE
        caseStudyLines.append(meanLine)

    file.writelines(addNewLine(caseStudyLines))

    # Close all environments
    file.writelines(addNewLine(["\t\t\\bottomrule",
                     "\t\\end{tabular}",
                     "\\end{adjustbox}"]))


    file.close()

def exportForR(outputFile: str, data: List[List[List[List[float]]]], toExclude:List[str] = None) -> None:
    with open(outputFile, 'w') as file:
        file.write("CaseStudy;Strategy;t;Result\n")
        for caseStudy in data:
            for type in data[caseStudy]:
                if (toExclude is not None and type in toExclude):
                    continue
                for t in T_PARAMETER:
                    for result in data[caseStudy][type][t]:
                        file.write(caseStudy + ";" + type + ";" + str(t) + ";" +
                               str(result) + "\n")


def readInFromR(inputFile: str) -> Dict[str,Tuple[str, List[Tuple[str, float]]]]:
    result = {}
    kruskalPValue = None
    dunnTestValues = []

    with open(inputFile, 'r') as file:
        for line in file:
            if "t=" in line:
                if kruskalPValue is not None:
                    result[t] = (kruskalPValue, dunnTestValues)
                    dunnTestValues = []
                t = int(line.split("=")[1])
            elif CSV_SEPARATOR in line:
                dunnResult = line.split(";")
                if (len(dunnResult) == 3):
                    dunnTestValues.append((dunnResult[0], float(dunnResult[1]), float(dunnResult[2])))
                else:
                    dunnTestValues.append((dunnResult[0], float(dunnResult[1])))
            elif "Kruskal_p" in line:
                kruskalPValue = float(line.split("=")[1])

        if kruskalPValue is not None:
            result[t] = (kruskalPValue, dunnTestValues)

    return result

def computeStandardDeviation(typesToAdd, allInformation):
    result = {}
    for caseStudy in allInformation:
        result[caseStudy] = {}
        for type in typesToAdd:
            result[caseStudy][type] = {}
            for t in T_PARAMETER:
                if (len(allInformation[caseStudy][type][t]) > 1):
                    result[caseStudy][type][t] = stdev(allInformation[caseStudy][type][t])
                else:
                    result[caseStudy][type][t] = 0

    return result

def performRTest(allInformation, kruskal = True, toExclude=None) -> List[Tuple[str, List[Tuple[str, float]]]]:
    if kruskal:
        approach = "kruskal"
    else:
        approach = "levene"
    dirPath = tempfile.mkdtemp()

    print("Path: " + dirPath)

    # Print data in file
    file = dirPath + os.sep + "in.csv"
    exportForR(file, allInformation, toExclude)

    rOutputFile = dirPath + os.sep + "out.csv"

    # Execute R script
    command = "Rscript"
    scriptPath = os.getcwd() + "/PerformKruskalWallis.R"

    arguments = [file, rOutputFile, approach]

    cmd = [command, scriptPath] + arguments

    subprocess.check_call(cmd)

    # Read in results
    kruskalResults = readInFromR(rOutputFile)

    return kruskalResults


def searchForTuple(itemToSearchFor : str, tuples : List[Tuple[str,float]]) -> Tuple[str, float]:
    for tuple in tuples:
        if tuple[0] == itemToSearchFor:
            return tuple
    return None


def formatPResult(pvalue : float, effSize : float = None) -> List[str]:
    if pvalue == 0:
        exponent = float("-inf")
    else:
        exponent = np.floor(np.log10(np.abs(pvalue)))

    if (exponent <= 0 and exponent >= -2):
        number = pvalue * 10 ** abs(exponent)

    if (exponent == 0):
        if (number > 0.05):
            return [""]
        result = "$" + str(roundError(number)) + "$"
    elif (exponent == -1):
        if (number > 0.5):
            return [""]
        result = "$" + str(roundError(number/ 10 ** abs(exponent))) + "$"
    elif (exponent == -2):
        if (number > 5):
            return [""]
        result = "$" + str(round(number / 10 ** abs(exponent), 2)) + "$"
    elif (exponent > -10):
        result = "$10^{-0" + str(int(abs(exponent))) +  "}$"
    #elif (exponent < -99):
    #    result = "$<10^{-99}$"
    elif pvalue == 0:
        result = "$0$"
    else:
        result = "$10^{" + str(int(exponent)) + "}$"

    if (effSize != None):
        result2 = " ($" + '{0:.2f}'.format(effSize) + "$)"
        return [result, result2]

    return [result]

def writeTestResultsToFiles(outputFile : str, kruskalResult : List[Tuple[str, List[Tuple[str, float]]]],
                               typesToAdd : List[str], labelsOfTypes : List[str], toExclude : List[str],
                               kruskal : bool) -> None:
    if kruskal:
        testDescription = "Kruskal-Wallis test"
        pairwiseTestDescription = "Mann-Whitney U test"
        testTableFile = outputFile + "kruskalTable.tex"
        pairwiseTestTableFile = outputFile + "mwuTable.tex"
    else:
        testDescription = "Levene's test"
        pairwiseTestDescription = "F-test"
        testTableFile = outputFile + "leveneTable.tex"
        pairwiseTestTableFile = outputFile + "fTable.tex"

    # 1. Table: Table containing the p-value results from the Kruskal-Wallis test
    with open(testTableFile, 'w') as file:
        file.writelines(addNewLine(["\\begin{tabular}{l r}",
                        "\\toprule",
                        "\\multicolumn{2}{c}{\\texttt{" + testDescription + "}}\\\\",
                        "\\midrule",
                        "& \\textit{p}-value " + NEW_LINE,
                        "\\midrule"]))

        for t in kruskalResult.keys():
            file.writelines(addNewLine(["t=" + str(t) + " & " + formatPResult(kruskalResult[t][0])[0] + NEW_LINE]))

        file.writelines(addNewLine(["\\bottomrule",
                        "\\end{tabular}"]))

    # 2. Table: Table containing the dunn-test values for the pair-wise comparisons
    with open(pairwiseTestTableFile, 'w') as file:
        columns = FIRST_COLUMN_FORMAT
        header = ""
        midrules = ""
        tLabelLine = ""
        spaceBetweenCaseStudies = ""
        # Remove all irrelevant columns
        remainingLabels = list(labelsOfTypes)
        remainingTypes = list(typesToAdd)
        for exclude in toExclude:
            remainingLabels.remove(labelsOfTypes[typesToAdd.index(exclude)])
            remainingTypes.remove(exclude)

        columnCounter = 1


        for i in range(0, len(remainingLabels)):
            columnCounter += 3
            columns += OTHER_COLUMN_FORMAT

            header += "& \\multicolumn{3}{c}{" + remainingLabels[i] + "}"
            midrules += "\\cmidrule(lr){" + str(i * 3 + 2) + "-" + str(i * 3 + 4) + "} "
            for j in T_PARAMETER:
                tLabelLine += "& $t=" + str(j) + "$"
                spaceBetweenCaseStudies += "& "
        header += NEW_LINE
        tLabelLine += NEW_LINE + "[0.1cm] "  # \\midrule"
        spaceBetweenCaseStudies += NEW_LINE

        if (kruskal):
            pValueText = " [\\textit{p} value ($\hat{A}_{12}$)]}}\\\\"
        else:
            pValueText = " (\\textit{p} value)}}\\\\"

        # Write the header of the table
        file.writelines(addNewLine(["\\begin{tabular}{" + columns + "}",
                                    "\\toprule",
                                    "\\multicolumn{" + str(columnCounter) + "}{c}{\\normalfont{" + pairwiseTestDescription + pValueText,
                                    "\\midrule",
                                    header,
                                    midrules,
                                    tLabelLine,
                                    spaceBetweenCaseStudies + "[-0.3cm]"]))

        # Write the p-values for all comparisons
        linesToWrite = []
        for i in range(0, len(remainingTypes)):
            if (kruskal):
                lineToWrite = ""
                secondLineToWrite = "\\multirow{-2}{*}{" + remainingLabels[i] + "}"
            else:
                lineToWrite = remainingLabels[i]
                secondLineToWrite = ""
            for j in range(0, len(remainingTypes)):
                if (j == i):
                    lineToWrite += " & \\multicolumn{3}{c}{\\cellcolor{white} \\noindent}"
                    secondLineToWrite += "& \\multicolumn{3}{c}{\\cellcolor{white}}"
                else:
                    # Search for the right comparison
                    for t in T_PARAMETER:
                        if (len(kruskalResult[t][1]) == 0):
                            continue
                        compStrats = [remainingTypes[i], remainingTypes[j]]
                        compString = compStrats[0] + " - " + compStrats[1]
                        tResult = searchForTuple(compString, kruskalResult[t][1])


                        if (len(tResult) == 3):
                            formatedResult = formatPResult(tResult[1], tResult[2])
                            lineToWrite += " & " + formatedResult[0]
                            secondLineToWrite += "& "
                            if (len(formatedResult) == 2):
                                secondLineToWrite += formatedResult[1]
                        else:
                            lineToWrite += " & " + formatPResult(tResult[1])[0]

            lineToWrite += NEW_LINE
            secondLineToWrite += NEW_LINE
            if (kruskal):
                linesToWrite.append(lineToWrite + "[-0.1cm]")
                linesToWrite.append(secondLineToWrite)
            else:
                linesToWrite.append(lineToWrite)
            linesToWrite.append(spaceBetweenCaseStudies + "[-0.3cm]")
        linesToWrite = linesToWrite[:len(linesToWrite) - 1]

        file.writelines(addNewLine(linesToWrite))

        file.writelines(["\\bottomrule",
                        "\\end{tabular}"])


def main() -> None:
    if (len(sys.argv) != 5):
        printUsage()
        exit(-1)

    inputDir = sys.argv[1]
    output_directory = sys.argv[4]
    typesToAdd = sys.argv[2].split(SEPARATION_SIGN)
    labelsToAdd = sys.argv[3].split(SEPARATION_SIGN)

    # Some error handling for wrong input
    if (len(typesToAdd) != len(labelsToAdd)):
        print("<typesToAdd> and <labelsOfTypes> have to be of the same length.")
        exit(-1)

    if (not os.path.exists(output_directory)):
        print("The directory '" + output_directory + "' does not exist. Please create it.")
        exit(-1)

    if (not os.path.exists(inputDir)):
        print("The input directory '" + inputDir + "' does not exist.")
        exit(-1)

    relevantDirectories = retrieveAllRelevantDirectories(inputDir)

    avgInformation, allInformation = gatherInformation(relevantDirectories, typesToAdd)

    # Create the error rate table
    ranking = createRanking(avgInformation, allInformation, typesToAdd, TO_IGNORE_RQ1)

    means, meanRanking = computeMeanValue(typesToAdd, allInformation, TO_IGNORE_RQ1)

    writeTableToFile(output_directory + os.path.sep + "table.tex", labelsToAdd, typesToAdd, avgInformation, ranking, means, meanRanking, TO_IGNORE_RQ1)

    kruskalResult = performRTest(allInformation, kruskal=True, toExclude=[])
    writeTestResultsToFiles(output_directory + os.path.sep, kruskalResult, typesToAdd, labelsToAdd,
                               kruskal=True, toExclude=[])

    leveneResult = performRTest(allInformation, kruskal=False, toExclude=TO_IGNORE_RQ2)
    writeTestResultsToFiles(output_directory + os.path.sep, leveneResult, typesToAdd, labelsToAdd,
                               kruskal=False, toExclude=TO_IGNORE_RQ2)


if __name__ == "__main__":
    main()
