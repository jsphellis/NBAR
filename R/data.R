#' NBA Player Performance Dataset
#'
#' A comprehensive dataset containing NBA player performance statistics, including traditional 
#' box score stats, advanced metrics, and betting-related information.
#'
#' @format A data frame with the following variables:
#' \describe{
#'   \item{Player}{Player's full name}
#'   \item{Seconds_Played}{Time played in seconds}
#'   \item{FG}{Field goals made}
#'   \item{FGA}{Field goals attempted}
#'   \item{FG%}{Field goal percentage}
#'   \item{3P}{Three-pointers made}
#'   \item{3PA}{Three-pointers attempted}
#'   \item{3P%}{Three-point percentage}
#'   \item{FT}{Free throws made}
#'   \item{FTA}{Free throws attempted}
#'   \item{FT%}{Free throw percentage}
#'   \item{ORB}{Offensive rebounds}
#'   \item{DRB}{Defensive rebounds}
#'   \item{TRB}{Total rebounds}
#'   \item{AST}{Assists}
#'   \item{STL}{Steals}
#'   \item{BLK}{Blocks}
#'   \item{TOV}{Turnovers}
#'   \item{PF}{Personal fouls}
#'   \item{PTS}{Points scored}
#'   \item{GmSc}{Game Score - a metric created by John Hollinger}
#'   \item{+/-}{Plus/minus score}
#'   \item{TS%}{True Shooting Percentage}
#'   \item{eFG%}{Effective Field Goal Percentage}
#'   \item{3PAr}{Three Point Attempt Rate}
#'   \item{FTr}{Free Throw Rate}
#'   \item{ORB%}{Offensive Rebound Percentage}
#'   \item{DRB%}{Defensive Rebound Percentage}
#'   \item{TRB%}{Total Rebound Percentage}
#'   \item{AST%}{Assist Percentage}
#'   \item{STL%}{Steal Percentage}
#'   \item{BLK%}{Block Percentage}
#'   \item{TOV%}{Turnover Percentage}
#'   \item{USG%}{Usage Percentage}
#'   \item{ORtg}{Offensive Rating}
#'   \item{DRtg}{Defensive Rating}
#'   \item{BPM}{Box Plus/Minus}
#'   \item{Team}{Team abbreviation}
#'   \item{GameID}{Unique game identifier}
#'   \item{Year}{Year of the game}
#'   \item{Month}{Month of the game}
#'   \item{Day}{Day of the game}
#'   \item{rebs+asts}{Combined rebounds and assists}
#'   \item{pts+asts}{Combined points and assists}
#'   \item{pts+rebs}{Combined points and rebounds}
#'   \item{pts+rebs+asts}{Combined points, rebounds, and assists}
#'   \item{assists}{Assists betting line}
#'   \item{rebounds}{Rebounds betting line}
#'   \item{points}{Points betting line}
#'   \item{date}{Date of the game}
#'   \item{Predicted_PTS}{Model's predicted points}
#'   \item{Exceeds_Prediction}{Whether actual points exceeded prediction}
#' }
#'
#' @source Data collected from official NBA box scores and various sportsbooks
#' @examples
#' \dontrun{
#' library(BeatTheOdds)
#' library(ggplot2)
#' 
#' # Plot points vs predicted points
#' nba_data |>
#'   ggplot(aes(Predicted_PTS, PTS)) +
#'   geom_point(alpha = 0.1) +
#'   geom_abline(color = "red", linetype = "dashed") +
#'   labs(title = "Actual vs Predicted Points")
#' 
#' # Calculate average prediction accuracy
#' mean(nba_data$Exceeds_Prediction, na.rm = TRUE)
#' }
"nba_data"

#' Load NBA Player Performance Dataset
#'
#' @return A data frame containing NBA player performance statistics
#' @export
#'
#' @examples
#' nba_data <- load_nba_data()
load_nba_data <- function() {
  # The data() function will look for nba_data.rda in the package
  data("nba_data", package = "BeatTheOdds", envir = environment())
  nba_data
}