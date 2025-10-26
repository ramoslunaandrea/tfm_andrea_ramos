# Reproducible script to generate metadata.csv from curatedMetagenomicData

suppressPackageStartupMessages({ library(here) })

# Load utility functions
util_path <- here::here("src", "r", "metadata_utils.R")
cat("Sourcing utils from: ", util_path, " | exists = ", file.exists(util_path), "\n", sep = "")
stopifnot(file.exists(util_path))
source(util_path, chdir = FALSE)

# Load environment variables and prepare directories
paths <- load_env_paths()

# Retrieve sampleMetadata
sample_md <- get_cmg_sample_metadata()

# Logs for verification
cat("Object type: ", typeof(sample_md), " | class: ", paste(class(sample_md), collapse = ", "), "\n", sep = "")
if (!is.null(dim(sample_md))) {
  cat("Dimensions: ", paste(dim(sample_md), collapse = " x "), "\n", sep = "")
}

cat("Studies labeled as 'schizophrenia':\n")
print(summarize_schizophrenia(sample_md)$studies)

# Extract ZhuF_2020 subset and save as metadata.csv
zhu_data <- extract_zhu_data(sample_md)
save_metadata_csv(zhu_data, "metadata.csv", paths$metadata_dir)

cat("File saved at: ", file.path(paths$metadata_dir, "metadata.csv"), "\n", sep = "")