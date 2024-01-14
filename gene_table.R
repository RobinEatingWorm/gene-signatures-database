# Install biomaRt if needed
if (!requireNamespace("biomaRt", quietly = TRUE)) {
    if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager")
    }
    BiocManager::install("biomaRt")
}

# Gene table for humans
ensembl <- biomaRt::useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
grch38 <- biomaRt::getBM(attributes = c("ensembl_gene_id", "external_gene_name", "chromosome_name", "description"),
                mart = ensembl)
write.table(grch38, file = "grch38.tsv", quote = FALSE, sep = "\t")
