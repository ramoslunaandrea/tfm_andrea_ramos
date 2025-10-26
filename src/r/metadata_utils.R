suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(here)
})

# Set project-local library
.set_project_lib <- function() {
  proj_lib <- here::here(".r-lib")
  if (!dir.exists(proj_lib)) dir.create(proj_lib, recursive = TRUE)
  .libPaths(c(proj_lib, .libPaths()))
  invisible(proj_lib)
}

# Ensure packages are installed
.ensure_packages <- function() {
  .set_project_lib()

  if (!requireNamespace("dotenv", quietly = TRUE)) {
    install.packages("dotenv", repos = "https://cloud.r-project.org")
  }
  if (!requireNamespace("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager", repos = "https://cloud.r-project.org")
  }

  for (pkg in c("curatedMetagenomicData", "AnnotationHub", "ExperimentHub",
                "SummarizedExperiment", "TreeSummarizedExperiment")) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      BiocManager::install(pkg, update = FALSE, ask = FALSE)
    }
  }

  suppressPackageStartupMessages({
    library(dotenv)
    library(curatedMetagenomicData)
  })
}

# Load .env variables and prepare paths
load_env_paths <- function() {
  .ensure_packages()
  dotenv::load_dot_env(file = here::here(".env"))
  metadata_dir <- Sys.getenv("METADATA_DIR", unset = "data/metadata")
  if (!dir.exists(metadata_dir)) dir.create(metadata_dir, recursive = TRUE)
  list(metadata_dir = metadata_dir)
}

# Get the sampleMetadata object from curatedMetagenomicData
get_cmg_sample_metadata <- function() {
  obj <- get("sampleMetadata", envir = asNamespace("curatedMetagenomicData"))
  return(obj)
}

# Summarize schizophrenia-related studies
summarize_schizophrenia <- function(sample_md) {
  sch_samples <- sample_md |> dplyr::filter(study_condition == "schizophrenia")
  studies <- sch_samples |> dplyr::distinct(study_name, PMID)
  list(samples = sch_samples, studies = studies)
}

# Extract ZhuF_2020 study data
extract_zhu_data <- function(sample_md) {
  sample_md |> dplyr::filter(study_name == "ZhuF_2020")
}

# Save a dataframe as CSV
save_metadata_csv <- function(df, filename, metadata_dir) {
  out <- file.path(metadata_dir, filename)
  readr::write_csv(df, out)
  message("Saved file: ", out)
  invisible(out)
}
