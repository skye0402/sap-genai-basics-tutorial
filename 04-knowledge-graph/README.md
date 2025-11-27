# 04 – HANA Knowledge Graph

This exercise demonstrates how to use SAP HANA Cloud's Knowledge Graph Engine to store and query structured knowledge extracted from unstructured text.

## Overview

The Knowledge Graph approach differs from the vector-based RAG in exercise 03:
- **Vector Store (03)**: Stores text chunks as embeddings for similarity search
- **Knowledge Graph (04)**: Stores structured entities and relationships as RDF triples for semantic querying

This exercise includes two CLI tools:
1. **`ingest_kg.py`** – Extracts entities and relationships from text using an LLM, then stores them as RDF triples in HANA
2. **`chat_kg.py`** – Answers natural language questions by generating SPARQL queries against the knowledge graph

## Prerequisites

1. SAP HANA Cloud instance with **Triple Store** feature enabled
   - See: [Enable Triple Store](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/enable-triple-store/)
2. SAP AI Core / Generative AI Hub credentials configured
3. Environment variables set in the root `.env` file (same as previous exercises)

### Additional Environment Variable (Optional)

```bash
# Knowledge Graph URI (default: WORKSHOP_KG)
KG_GRAPH_URI=WORKSHOP_KG
```

## Setup

```bash
cd 04-knowledge-graph
uv sync
```

## Usage

### Step 1: Ingest Text into Knowledge Graph

The ingestion tool reads a text file, uses the LLM to extract entities and relationships, and stores them as RDF triples:

```bash
uv run ingest_kg.py sample-company.txt
```

Example output:
```
Reading text from: sample-company.txt
Initializing LLM (gpt-4.1)...
Extracting entities and relationships...
Extracted 8 entities and 15 relationships.

Entities:
  - techvision (Organization): TechVision Inc.
  - maria_chen (Person): Maria Chen
  - david_park (Person): David Park
  ...

Relationships:
  - maria_chen --[founded]--> techvision
  - maria_chen --[role]--> CEO
  ...

Connecting to HANA and storing in graph <WORKSHOP_KG>...
Successfully ingested knowledge graph from sample-company.txt
```

### Step 2: Query the Knowledge Graph

Start the chat interface to ask questions about the ingested data:

```bash
uv run chat_kg.py
```

Example session:
```
Connecting to HANA Knowledge Graph <WORKSHOP_KG>...
Initializing LLM (gpt-4.1)...

Knowledge Graph Chat
========================================
Ask questions about the data in the knowledge graph.
Press Enter with empty input to exit.

You: Who founded TechVision?
Assistant: TechVision was founded by Maria Chen and David Park.

You: What products does the company offer?
Assistant: TechVision offers two products: CloudSync and DataGuard.

You: Where is the company headquartered?
Assistant: TechVision is headquartered in San Francisco, California.
```

## How It Works

### Ingestion Pipeline (`ingest_kg.py`)

1. **Read text** from the input file
2. **LLM extraction**: Send text to LLM with a prompt to extract entities (people, organizations, products, etc.) and relationships
3. **Build SPARQL**: Convert extracted knowledge to `INSERT DATA` SPARQL statement
4. **Execute**: Store triples in HANA via `SPARQL_EXECUTE` stored procedure

### Query Pipeline (`chat_kg.py`)

Uses a custom two-step LLM approach:

1. **Schema extraction**: Auto-extracts ontology from the graph using `HanaRdfGraph`
2. **SPARQL generation**: LLM converts natural language question to SPARQL query based on the schema
3. **Query execution**: Runs SPARQL against HANA via `SPARQL_TABLE`
4. **Result cleaning**: Removes URIs, keeps only human-readable labels
5. **Answer formulation**: LLM converts cleaned results to natural language answer

## Key Concepts

### RDF Triples
Data is stored as subject-predicate-object triples:
```
<maria_chen> <founded> <techvision> .
<maria_chen> <role> "CEO" .
<techvision> a <Organization> .
```

### SPARQL
Query language for RDF data:
```sparql
SELECT ?founder ?name
WHERE {
    ?founder <founded> <techvision> .
    ?founder <http://www.w3.org/2000/01/rdf-schema#label> ?name .
}
```

### Knowledge Graph vs Vector Store

| Aspect | Vector Store | Knowledge Graph |
|--------|--------------|-----------------|
| Data format | Text chunks + embeddings | Structured triples |
| Query type | Similarity search | Semantic/logical queries |
| Best for | Finding relevant passages | Answering factual questions |
| Relationships | Implicit in text | Explicit and queryable |

## Troubleshooting

- **"Graph might be empty"**: Run `ingest_kg.py` first to populate the graph
- **SPARQL errors**: Check that Triple Store is enabled in your HANA instance
- **No results or wrong results**: The LLM-generated SPARQL might not match the schema; try rephrasing your question
- **Inconsistent answers**: SPARQL generation can vary with phrasing. Use `--verbose` to see what query was generated

## Tips

- Use `--verbose` flag with `chat_kg.py` to see the generated SPARQL queries and intermediate results
- Re-ingesting a file clears the previous graph data first (no duplicates)
- The extraction quality depends on the LLM - clearer input text produces better knowledge graphs

## Exercise

### Exercise 1: Extend the Company Knowledge Graph

- **Goal**: Get familiar with the ingestion pipeline and how entities/relationships are modeled.
- **What to do**:
  1. Copy `sample-company.txt` to a new file (for example `sample-company-b.txt`).
  2. Change the text to describe a different company (founders, products, locations, partnerships, etc.).
  3. Run:
     ```bash
     uv run ingest_kg.py your-new-file.txt
     ```
  4. Start the chat:
     ```bash
     uv run chat_kg.py --verbose
     ```
  5. Ask questions such as:
     - `Who founded <your company>?`
     - `What products does <your company> offer?`
     - `Where does <your company> have offices?`

- **Observe**:
  - How the ontology (schema) changes in the verbose schema output.
  - Which relationship names the LLM chooses (for example `founded_by`, `has_office_in`, `has_partnership_with`).

### Exercise 2: Improve SPARQL Generation with Prompt Tuning

- **Goal**: See how changing the SPARQL generation prompt affects the queries and answers.
- **What to do**:
  1. Run the chat in verbose mode:
     ```bash
     uv run chat_kg.py --verbose
     ```
  2. Ask a question that is not directly covered in the example, for example:
     - `In which year was TechVision founded?`
     - `How many employees does the company have?`
  3. Look at the generated SPARQL and the cleaned data printed by the script.
  4. Open `chat_kg.py` and locate the `SPARQL_GENERATION_PROMPT`.
  5. Adjust the instructions (for example, explicitly mention properties like `founded_in` or `has_employee_count`).
  6. Run `chat_kg.py` again and ask the same question.

- **Observe**:
  - How the generated SPARQL changes after you tune the prompt.
  - Whether the answers become more reliable or precise.

### Exercise 3: Compare LLM-Generated SPARQL with Manual SPARQL

- **Goal**: Understand the structure of SPARQL by comparing it to what the LLM generates.
- **What to do**:
  1. Run the chat with `--verbose` and ask:
     - `What products does the company offer?`
  2. Copy the generated SPARQL from the console.
  3. In a scratch file (or in a HANA SQL/SPARQL tool if available), tweak the query, for example:
     - Add a filter so that it only returns products for TechVision.
     - Add sorting or additional columns.
  4. Compare your manual query with the one generated by the LLM.

- **Reflect**:
  - How close the LLM-generated SPARQL is to what you would write manually.
  - Which parts of the query are easy or hard for the LLM to get right.
