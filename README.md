# NBAR
## NBA Player Performance vs Odds Analysis

A comprehensive data analysis toolkit for evaluating NBA player performance against betting odds, combining historical statistics with machine learning to identify potential betting opportunities.

## Overview

This project provides a robust framework for analyzing NBA player performance data against betting odds. It features automated data collection from official NBA box scores, integration with betting odds APIs, and statistical modeling to identify patterns and potential value opportunities in the sports betting market.

## Features

### Data Collection & Processing
- Automated daily scraping of NBA box scores and player statistics
- Comprehensive player performance metrics including advanced statistics
- Automated data cleaning and preprocessing pipeline

### Technical Features
- Daily automated data updates via GitHub Actions
- R package integration for statistical analysis
- Modular design for easy extension and customization

## Installation

### R Package

```{r}

# Install the package
remotes::install_github("jsphellis/NBAR")

# Load the package
library(NBAR)

# Load the data
data("nba_data")

```

