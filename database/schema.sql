-- An article from PubMed Central
CREATE TABLE IF NOT EXISTS Article(
    -- Title of the article
    title TEXT,
    -- Journal in which article was published
    journal TEXT,
    -- PMID (PubMed ID)
    pmid INTEGER,
    -- PMCID (PubMed Central ID)
    pmcid INTEGER PRIMARY KEY
);

-- A human gene
CREATE TABLE IF NOT EXISTS Gene(
    -- Ensembl ID
    ensembl_id INTEGER PRIMARY KEY,
    -- Gene name
    name TEXT,
    -- Short description of gene
    description TEXT,
    -- Chromosome where gene is located
    chromosome TEXT
);

-- A single gene within a gene signature
-- Note: this implicitly assumes that each article contains no more than one gene signature
CREATE TABLE IF NOT EXISTS GeneSignature(
    -- PMCID of the article in which the gene signature is found
    pmcid INTEGER REFERENCES Article(pmcid) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Ensembl ID of the gene
    ensembl_id INTEGER REFERENCES Gene(ensembl_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (pmcid, ensembl_id)
);

-- A synonym for a human gene
CREATE TABLE IF NOT EXISTS GeneSynonym(
    -- Synonym name
    name TEXT,
    -- Ensembl ID
    ensembl_id INTEGER REFERENCES Gene(ensembl_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (name, ensembl_id)
);
