# Install required packages if needed
if (!requireNamespace("biomaRt", quietly = TRUE)) {
    if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager")
    }
    BiocManager::install("biomaRt")
}
if (!requireNamespace("rjson", quietly = TRUE)) {
    install.packages("rjson")
}

# Gene information for humans
ensembl <- biomaRt::useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
grch38 <- biomaRt::getBM(attributes = c("ensembl_gene_id", "external_gene_name", "external_synonym", "chromosome_name",
                                        "description"), mart = ensembl)
grch38 <- grch38[order(grch38$ensembl_gene_id), ]

# Save gene information
genes_info <- rjson::fromJSON(file = "paths.json")$data$genes$info
write.table(grch38, file = genes_info, quote = FALSE, sep = "\t", row.names = FALSE)
