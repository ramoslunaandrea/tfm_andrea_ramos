options(repos = c(CRAN = "https://cloud.r-project.org"))

# Local project library setup and package installation script
proj_lib <- file.path(getwd(), ".r-lib")
if (!dir.exists(proj_lib)) dir.create(proj_lib, recursive = TRUE)
.libPaths(c(proj_lib, .libPaths()))
message("Local project library: ", proj_lib)

# CRAN y Bioconductor installation
for (pkg in c("BiocManager","dotenv","Matrix","cli","rlang","codetools","nlme","MASS",
              "cluster","lattice","survival","mgcv","KernSmooth","boot","class","nnet","spatial",
              "foreign","rpart","tree","mgcv","MatrixModels","bitops","RCurl","RSQLite"
)) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
}

bioc_pkgs <- c(
  "SummarizedExperiment",
  "TreeSummarizedExperiment",
  "AnnotationHub",
  "ExperimentHub",
  "curatedMetagenomicData"
)
for (pkg in bioc_pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    BiocManager::install(pkg, update = FALSE, ask = FALSE)
  }
}

message("Bioconductor + CRAN installed successfully")
