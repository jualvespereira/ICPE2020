# Imports needed for different functions
library(FSA) # needed for dunnTest-function
library(car) # needed for Levene's test

library(effsize)

# Constants
P_VALUE = 0.05

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) == 0) {
  # Input file paths
  inputFile <- "/tmp/tmp9uyuw4ru/in.csv"
  outputFile <- "'/tmp/tmp9uyuw4ru/out.csv'"
  aproach <- "levene"
} else {
  # Read it in by using the arguments
  inputFile <- arguments[1]
  outputFile <- arguments[2]  
  aproach <- arguments[3]
}


# Read in the file
data <- read.csv2(file=inputFile)

data$Result <- as.double(gsub('"','', data$Result))


# Standardize the result for every case study by subtracting the expectation 
# and dividing it by the standard deviation
for (caseStudy in unique(data$CaseStudy)) {
  for (t in unique(data$t)) {
    dataOfInterest <- data$Result[data$CaseStudy == caseStudy & data$t == t]
    standardDeviatoin <- sd(dataOfInterest)
    meanValue <- mean(dataOfInterest)
    data$Result[data$CaseStudy == caseStudy & data$t == t] = (dataOfInterest - meanValue) / standardDeviatoin
  }
}


data <- as.data.frame(data)

strategies <- sort(unique(data$Strategy))

resultString <- c()

# Do the tests for every sampling size (t=1, t=2, t=3)
for (t in unique(data$t)) {
  # Perform the Kruskal-Wallis test to find out whether one sample dominates the others
  dataOfInterest <- data[data$t == t,]
  if (aproach == "kruskal") {
    result <- kruskal.test(Result~Strategy, data=dataOfInterest);
    pValue <- result$p.value
  } else {
    result <- leveneTest(Result~Strategy,data=dataOfInterest);
    pValue <- result$`Pr(>F)`[[1]]
  }
  
  # Add results
  resultString <- c(resultString, 
                    paste("t=", t, sep=""),
                    paste("Kruskal_p=", pValue, sep=""))
  
  MWU <- NULL
  R1 <- NULL
  # If one sample significantly dominates the others, perform the Dunn test as post-hoc test
  if (pValue < P_VALUE) {
    for (i in 1:(length(strategies))) {
      strategy = toString(strategies[i])
      for (j in 1:length(strategies)) {
        if (i == j) {
          next
        }
        otherStrategy = toString(strategies[j])
        comparisonString = paste(strategy, " - ", otherStrategy, sep="")
        tmpData <- dataOfInterest[dataOfInterest$Strategy == strategy,]
        tmpData2 <- dataOfInterest[dataOfInterest$Strategy == otherStrategy,]
        
        if (aproach == "kruskal") {
            MWU <- wilcox.test(tmpData$Result, tmpData2$Result,
                        alternative="l",
                        paired=FALSE)
            
            # Also calculate the effect size A_{12}
            R1 <- effsize::VD.A(tmpData2$Result, tmpData$Result)
            resultString <- c(resultString,
                              paste(comparisonString, MWU$p.value, R1$estimate, sep=";"))
        } else {
          MWU <- var.test(tmpData$Result, tmpData2$Result,
                          alternative="l")
          resultString <- c(resultString,
                            paste(comparisonString, MWU$p.value, sep=";"))
        }
        
      }
    }
  }
}

# Write the results in a file for use in a python script
outputFileConn <- file(outputFile)
writeLines(resultString, outputFileConn)
close(outputFileConn)