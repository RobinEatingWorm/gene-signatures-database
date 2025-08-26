-- Query for a gene synonym with a specified name
SELECT gene_ensembl_id AS ensembl_id, name
FROM GeneSynonym
WHERE name = :synonym;
