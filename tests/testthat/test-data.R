test_that("nba_data loads correctly", {
  data(nba_data, package = "NBAR")
  expect_s3_class(nba_data, "data.frame")
  expect_gt(nrow(nba_data), 0)
  expect_gt(ncol(nba_data), 0)
})