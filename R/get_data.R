#' Get NBA Player Statistics
#'
#' @description
#' Fetches processed NBA player statistics from GitHub repository
#'
#' @param quiet Logical; if FALSE, prints status messages
#' @return A tibble containing NBA player statistics
#' @export
#'
#' @examples
#' nba_stats <- get_nba_stats()
get_nba_stats <- function(quiet = FALSE) {
  config <- .get_config()
  stats_url <- paste0(config$base_url, "/", config$files$nba_stats)

  if (!quiet) message("Fetching NBA player statistics...")

  tryCatch({
    temp_file <- tempfile(fileext = ".csv")

    # Set higher timeout
    options(timeout = 120)  # Increase to 120 seconds

    # Download the file with a more robust method
    download.file(
      stats_url, 
      destfile = temp_file, 
      method = "libcurl",  # Use 'libcurl' instead of 'curl'
      quiet = quiet
    )

    # Read the CSV file
    data <- readr::read_csv(temp_file, show_col_types = FALSE) %>%
      tibble::as_tibble()
    
    unlink(temp_file)  # Clean up

    if (!quiet) message("Data successfully retrieved!")
    return(data)

  }, error = function(e) {
    stop("Failed to fetch NBA statistics: ", e$message)
  })
}
