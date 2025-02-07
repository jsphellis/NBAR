#' Package Configuration Settings
#'
#' @description
#' Internal configuration settings for data locations
#'
#' @keywords internal
.get_config <- function() {
  list(
    base_url = "https://raw.githubusercontent.com/jsphellis/NBAR/main/inst/data",
    files = list(
      nba_data = "nba_data.rda"
    )
  )
}