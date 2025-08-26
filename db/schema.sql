-- An article from PubMed Central
CREATE TABLE IF NOT EXISTS Article (
    -- DOI (Digital Object Identifier)
    doi TEXT,
    -- PMCID (PubMed Central ID)
    pmcid TEXT PRIMARY KEY,
    -- Title of article
    title TEXT,
    -- Journal in which article was published
    journal TEXT,
    -- Volume number
    volume TEXT,
    -- Issue number
    issue TEXT,
    -- Page numbers
    pages TEXT,
    -- Date published
    date TEXT
);

-- An author
CREATE TABLE IF NOT EXISTS Author (
    -- Arbitrary unique ID
    id INTEGER PRIMARY KEY,
    -- Name of author
    name TEXT NOT NULL
);

-- A human gene
CREATE TABLE IF NOT EXISTS Gene (
    -- Ensembl ID
    ensembl_id TEXT PRIMARY KEY,
    -- Gene name
    name TEXT,
    -- Chromosome where gene is located
    chromosome TEXT,
    -- Short description of gene
    description TEXT
);

-- An author of an article
CREATE TABLE IF NOT EXISTS ArticleAuthor (
    -- PMCID of the article which the author contributed to
    article_pmcid TEXT REFERENCES Article(pmcid) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Unique ID of the author
    author_id INTEGER REFERENCES Author(id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Relationship between each article and each author
    PRIMARY KEY (article_pmcid, author_id)
);

-- A synonym for a human gene
CREATE TABLE IF NOT EXISTS GeneSynonym (
    -- Synonym name
    name TEXT NOT NULL,
    -- Ensembl ID
    gene_ensembl_id TEXT REFERENCES Gene(ensembl_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Relationship between each synonym and its corresponding gene
    PRIMARY KEY (name, gene_ensembl_id)
);

-- A single gene within a gene signature
-- Note: this implicitly assumes that each article contains no more than one gene signature
CREATE TABLE IF NOT EXISTS GeneSignature (
    -- PMCID of the article in which the gene signature is found
    article_pmcid TEXT REFERENCES Article(pmcid) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Ensembl ID of the gene within the gene signature
    gene_ensembl_id TEXT REFERENCES Gene(ensembl_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Relationship between each article and each gene within the article's gene signature
    PRIMARY KEY (article_pmcid, gene_ensembl_id)
);
