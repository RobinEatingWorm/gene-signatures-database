# Install biomaRt if needed
if (!requireNamespace("biomaRt", quietly = TRUE)) {
    if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager")
    }
    BiocManager::install("biomaRt")
}

# Gene table for humans
ensembl <- biomaRt::useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
grch38 <- biomaRt::getBM(attributes = c("ensembl_gene_id", "external_gene_name", "external_synonym", "chromosome_name",
                                        "description"), mart = ensembl)
grch38 <- grch38[order(grch38$ensembl_gene_id), ]
write.table(grch38, file = "data/grch38.tsv", quote = FALSE, sep = "\t", row.names = FALSE)
