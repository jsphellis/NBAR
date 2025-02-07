# Read the processed CSV
nba_data <- read.csv("data/24-25_NBA_processed.csv")

# Convert date column to proper Date type
nba_data$date <- as.Date(nba_data$date)

# Create inst/data directory if it doesn't exist
dir.create("inst/data", recursive = TRUE, showWarnings = FALSE)

# Save as .rda file in the correct location
save(nba_data, file = "inst/data/nba_data.rda", compress = "xz")