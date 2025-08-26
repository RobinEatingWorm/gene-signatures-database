-- Query for a gene with a specified name
SELECT ensembl_id, name
FROM Gene
WHERE name = :gene;
