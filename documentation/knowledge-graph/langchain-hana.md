LangChain
=========

Integrate LangChain with SAP HANA Cloud to make use of vector searches, knowledge graphs, and other in-database capabilities as part of LLM-driven applications.

To use SAP HANA Cloud knowledge graph engine with LangChain, you must install the LangChain SAP HANA Cloud integration package using pip:

    %pip install -qU langchain-hana

To learn more about how to make use of vector searches and knowledge graphs, see [LangChain integration for SAP HANA Cloud![Information published on non-SAP site](https://help.sap.com/doc/5c3488c559d64d2c8b4f331a1d9b281a/2025_3_QRC/en-US/themes/sap-light/img/3rd_link.png "Information published on non-SAP site")](https://help.sap.com/docs/link-disclaimer?site=https%3A%2F%2Fgithub.com%2FSAP%2Flangchain-integration-for-sap-hana-cloud%2F "https://github.com/SAP/langchain-integration-for-sap-hana-cloud/").

You can also use the SAP HANA Cloud knowledge graph engine and SAP HANA Cloud vector engine with LangChain to build a question-answering (QA) chain that queries RDF (Resource Description Framework) data stored in an SAP HANA Cloud instance using the SPARQL query language, which returns a human-readable response. Learn more about [building a QA chain![Information published on non-SAP site](https://help.sap.com/doc/5c3488c559d64d2c8b4f331a1d9b281a/2025_3_QRC/en-US/themes/sap-light/img/3rd_link.png "Information published on non-SAP site")](https://help.sap.com/docs/link-disclaimer?site=https%3A%2F%2Fgithub.com%2Fyberber-sap%2Flangchain%2Fblob%2Fhana-graph-notebook%2Fdocs%2Fdocs%2Fintegrations%2Fgraphs%2Fhana_graph_sparql.ipynb "https://github.com/yberber-sap/langchain/blob/hana-graph-notebook/docs/docs/integrations/graphs/hana_graph_sparql.ipynb").


* Example-Notebook:

{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "a21f45a7",
   "metadata": {},
   "source": [
    "# SAP HANA Cloud Knowledge Graph Engine\n",
    "[SAP HANA Cloud Knowledge Graph](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/sap-hana-cloud-sap-hana-database-knowledge-graph-engine-guide) is a fully integrated knowledge graph solution within the `SAP HANA Cloud` database.\"\n",
    "\n",
    "## Setup & Installation\n",
    "You must have an SAP HANA Cloud instance with the **triple store** feature enabled.,\n",
    "For detailed instructions, refer to: [Enable Triple Store](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/enable-triple-store/)\n",
    "\n",
    "To use SAP HANA Knowledge Graph Engine and/or Vector Store Engine with LangChain, install the `langchain-hana` package:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "890beddc",
   "metadata": {
    "vscode": {
     "languageId": "shellscript"
    }
   },
   "outputs": [],
   "source": [
    "pip install langchain_hana"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "951a2b31",
   "metadata": {},
   "source": [
    "First, create a connection to your SAP HANA Cloud instance."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "46a66d94",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "from hdbcli import dbapi\n",
    "\n",
    "# Load environment variables if needed\n",
    "load_dotenv()\n",
    "\n",
    "# Establish connection to SAP HANA Cloud\n",
    "connection = dbapi.connect(\n",
    "    address=os.environ.get(\"HANA_DB_ADDRESS\"),\n",
    "    port=os.environ.get(\"HANA_DB_PORT\"),\n",
    "    user=os.environ.get(\"HANA_DB_USER\"),\n",
    "    password=os.environ.get(\"HANA_DB_PASSWORD\"),\n",
    "    autocommit=True,\n",
    "    # sslValidateCertificate=False,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0871029d",
   "metadata": {},
   "source": [
    "Then, import the `HanaRdfGraph` Class"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "4f86ef42",
   "metadata": {},
   "outputs": [],
   "source": [
    "from langchain_hana import HanaRdfGraph"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "baa8e27e",
   "metadata": {},
   "source": [
    "## Creating a HanaRdfGraph Instance"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "16afb74d",
   "metadata": {},
   "source": [
    " The constructor requires:\n",
    "\n",
    "- **`connection`**: an active `hdbcli.dbapi.connect(...)` instance  \n",
    "- **`graph_uri`**: the named graph (or `\"DEFAULT\"`) where your RDF data lives  \n",
    "- **One of**:  \n",
    "  1. **`ontology_query`**: a SPARQL CONSTRUCT to extract schema triples  \n",
    "  2. **`ontology_uri`**: a hosted ontology graph URI  \n",
    "  3. **`ontology_local_file`** + **`ontology_local_file_format`**: a local Turtle/RDF file  \n",
    "  4. **`auto_extract_ontology=True`** (not recommended for production—see note)\n",
    "\n",
    "`graph_uri` vs. Ontology\n",
    "- **`graph_uri`**:  \n",
    "  The named graph in your SAP HANA Cloud instance that contains your instance data (sometimes 100k+ triples).\n",
    "  If `None` or `\"DEFAULT\"` is provided, the default graph is used.\n",
    "- **Ontology**: a lean schema (typically ~50-100 triples) describing classes, properties, domains, ranges, labels, comments, and subclass relationships. The ontology guides SPARQL generation and result interpretation."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "ac775582",
   "metadata": {},
   "source": [
    "### Creating a graph instance with **DEFAULT** Graph\n",
    "More info on the DEFAULT graph can be found at [DEFAULT Graph and Named Graphs](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/default-graph-and-named-graphs)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "de839ea1",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    auto_extract_ontology=True,\n",
    ")\n",
    "\n",
    "# graph = HanaRdfGraph(\n",
    "#     connection=connection,\n",
    "#     graph_uri=\"DEFAULT\",\n",
    "#     auto_extract_ontology=True,\n",
    "# )\n",
    "\n",
    "# graph = HanaRdfGraph(\n",
    "#     connection=connection,\n",
    "#     graph_uri=\"\",\n",
    "#     auto_extract_ontology=True,\n",
    "# )"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0ae5e22e",
   "metadata": {},
   "source": [
    "### Creating a graph instance with a `graph_uri`"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7872e84d",
   "metadata": {},
   "outputs": [],
   "source": [
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    graph_uri=\"http://example.org/movies\",\n",
    "    auto_extract_ontology=True,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "20a874c6",
   "metadata": {},
   "source": [
    "### Creating a graph instance with a remote `ontology_uri`\n",
    "Load the schema directly from a hosted graph URI."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d8a77473",
   "metadata": {},
   "outputs": [],
   "source": [
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    ontology_uri=\"<your_ontology_graph_uri>\",\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9f966caf",
   "metadata": {},
   "source": [
    "### Creating a graph instance with a custom `ontology_query`\n",
    "Use a custom `CONSTRUCT` query to selectively extract schema triples."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "0938ef6a",
   "metadata": {},
   "outputs": [],
   "source": [
    "ontology_query = \"\"\"\n",
    "\t\tPREFIX owl: <http://www.w3.org/2002/07/owl#>\n",
    "\t\tPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n",
    "\t\tPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n",
    "\t\tPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n",
    "\t\tCONSTRUCT {?cls rdf:type owl:Class . ?cls rdfs:label ?clsLabel . ?rel rdf:type ?propertyType . ?rel rdfs:label ?relLabel . ?rel rdfs:domain ?domain . ?rel rdfs:range ?range .}\n",
    "\t\tFROM <kgdocu_movies>\n",
    "\t\tWHERE { # get properties\n",
    "\t\t\t{SELECT DISTINCT ?domain ?rel ?relLabel ?propertyType ?range\n",
    "\t\t\tWHERE {\n",
    "\t\t\t\t?subj ?rel ?obj .\n",
    "\t\t\t\t?subj a ?domain .\n",
    "\t\t\t\tOPTIONAL{?obj a ?rangeClass .}\n",
    "\t\t\t\tFILTER(?rel != rdf:type)\n",
    "\t\t\t\tBIND(IF(isIRI(?obj) = true, owl:ObjectProperty, owl:DatatypeProperty) AS ?propertyType)\n",
    "\t\t\t\tBIND(COALESCE(?rangeClass, DATATYPE(?obj)) AS ?range)\n",
    "\t\t\t\tBIND(STR(?rel) AS ?uriStr)       # Convert URI to string\n",
    "  \t\t\t\tBIND(REPLACE(?uriStr, \"^.*[/#]\", \"\") AS ?relLabel)\n",
    "\t\t\t}}\n",
    "\t\t\tUNION { # get classes\n",
    "\t\t\t\tSELECT DISTINCT ?cls ?clsLabel\n",
    "\t\t\t\tWHERE {\n",
    "\t\t\t\t\t?instance a/rdfs:subClassOf* ?cls .\n",
    "\t\t\t\t\tFILTER (isIRI(?cls)) .\n",
    "\t\t\t\t\tBIND(STR(?cls) AS ?uriStr)       # Convert URI to string\n",
    "  \t\t\t\t\tBIND(REPLACE(?uriStr, \"^.*[/#]\", \"\") AS ?clsLabel)\n",
    "\t\t\t\t}\n",
    "\t\t\t}\n",
    "\t\t}\n",
    "\"\"\"\n",
    "\n",
    "# can provide the graph_uri param as well if needed\n",
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    ontology_query=ontology_query,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1f136924",
   "metadata": {},
   "source": [
    "### Creating a graph instance with a Local rdf file\n",
    "(`ontology_local_file` + `ontology_local_file_format`): Load the schema from a local RDF ontology file.\n",
    "\n",
    "Supported RDF formats are `Turtle`, `RDF/XML`, `JSON-LD`, `N-Triples`, `Notation-3`, `Trig`, `Trix`, `N-Quads`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "35e74c74",
   "metadata": {},
   "outputs": [],
   "source": [
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    ontology_local_file=\"<your_ontology_file_path>\", # e.g., \"ontology.ttl\"\n",
    "    ontology_local_file_format=\"<your_ontology_file_format>\",  # e.g., \"Turtle\", \"RDF/XML\", \"JSON-LD\", \"N-Triples\", \"Notation-3\", \"Trig\", \"Trix\", \"N-Quads\"\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6220e1df",
   "metadata": {},
   "source": [
    "### Auto extraction of ontology\n",
    "(`auto_extract_ontology=True`): Infer schema information directly from your instance data."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a9d9e037",
   "metadata": {},
   "outputs": [],
   "source": [
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    graph_uri=\"<your_graph_uri>\",\n",
    "    auto_extract_ontology=True,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "ac2a1ac1",
   "metadata": {},
   "source": [
    "> **Note**: Auto-extraction is **not** recommended for production—it omits important triples like `rdfs:label`, `rdfs:comment`, and `rdfs:subClassOf` in general."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "fb0998cf",
   "metadata": {},
   "source": [
    "## Executing SPARQL Queries\n",
    "\n",
    "You can use the `query()` method to execute arbitrary SPARQL queries (`SELECT`, `ASK`, `CONSTRUCT`, etc.) on the data graph.\n",
    "\n",
    "The function has the following parameters\n",
    "- **query**: the SPARQL query string.\n",
    "- **content_type**: the response format  for the output (Default is CSV)\n",
    "\n",
    "Please use the following strings for the respective formats.\n",
    "- CSV: `\"sparql-results+xml\"`\n",
    "- JSON: `\"sparql-results+json\"`\n",
    "- XML: `\"sparql-results+csv\"`\n",
    "- TSV: `\"sparql-results+tsv\"`\n",
    "\n",
    "> **Note**: CONSTRUCT and ASK Queries return `turtle` and `boolean` formats respectively.\n",
    "\n",
    "Refer to the [HANA SPARQL Reference](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sparql-reference-guide/) to know more about writing SPARQL queries.\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c5214c3a",
   "metadata": {},
   "source": [
    "Let us insert some data into the `Puppets` graph."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "4d5af5f5",
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor = connection.cursor()\n",
    "try:\n",
    "    result = cursor.callproc(\n",
    "        \"SYS.SPARQL_EXECUTE\", (\n",
    "        \"\"\"\n",
    "        INSERT DATA {\n",
    "        GRAPH <Puppets> {\n",
    "            <P1> a <Puppet>; <name> \"Ernie\"; <show> \"Sesame Street\".\n",
    "            <P2> a <Puppet>; <name> \"Bert\"; <show> \"Sesame Street\" .\n",
    "            }\n",
    "        }\n",
    "        \"\"\", \"\", \"?\", \"?\"\n",
    "        )\n",
    "    )\n",
    "    response = result[2]\n",
    "except dbapi.Error as db_error:\n",
    "    raise RuntimeError(\n",
    "        f'The database query failed: '\n",
    "        f'{db_error.errortext.split(\"; Server Connection\")[0]}'\n",
    "    )\n",
    "finally:\n",
    "    cursor.close()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f16d44cc",
   "metadata": {},
   "source": [
    "Then, we create a graph instance for the `Puppets` graph."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "726d765e",
   "metadata": {},
   "outputs": [],
   "source": [
    "puppets_graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    graph_uri=\"Puppets\",\n",
    "    auto_extract_ontology=True,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4cbdf304",
   "metadata": {},
   "source": [
    "\n",
    "The given query lists all tuples in the `Puppets` graph.  "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "078ce2c9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "s,p,o\n",
      "P1,name,Ernie\n",
      "P1,show,Sesame Street\n",
      "P1,http://www.w3.org/1999/02/22-rdf-syntax-ns#type,Puppet\n",
      "P2,name,Bert\n",
      "P2,show,Sesame Street\n",
      "P2,http://www.w3.org/1999/02/22-rdf-syntax-ns#type,Puppet\n",
      "\n"
     ]
    }
   ],
   "source": [
    "query = \"\"\"\n",
    "SELECT ?s ?p ?o\n",
    "WHERE {\n",
    "    GRAPH <Puppets> {\n",
    "        ?s ?p ?o .\n",
    "    }\n",
    "}\n",
    "ORDER BY ?s\n",
    "\"\"\"\n",
    "\n",
    "result = puppets_graph.query(query)\n",
    "print(result)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "langchain-hana-0Dgwpkzf-py3.13",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

* Example-Notebook 2

{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "e48024ef",
   "metadata": {},
   "source": [
    "# Question Answering with `HanaSparqlQAChain`"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0b340e95",
   "metadata": {},
   "source": [
    "## Setup and Installation\n",
    "To use this feature, install the `langchain-hana` package:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0f6d6d15",
   "metadata": {
    "vscode": {
     "languageId": "shellscript"
    }
   },
   "outputs": [],
   "source": [
    "pip install langchain_hana"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1be79aa5",
   "metadata": {},
   "source": [
    "And then, create a connection to your SAP HANA Cloud instance."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "873c22a2",
   "metadata": {
    "vscode": {
     "languageId": "shellscript"
    }
   },
   "outputs": [],
   "source": [
    "import os\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "from hdbcli import dbapi\n",
    "\n",
    "# Load environment variables if needed\n",
    "load_dotenv()\n",
    "\n",
    "# Establish connection to SAP HANA Cloud\n",
    "connection = dbapi.connect(\n",
    "    address=os.environ.get(\"HANA_DB_ADDRESS\"),\n",
    "    port=os.environ.get(\"HANA_DB_PORT\"),\n",
    "    user=os.environ.get(\"HANA_DB_USER\"),\n",
    "    password=os.environ.get(\"HANA_DB_PASSWORD\"),\n",
    "    autocommit=True,\n",
    "    sslValidateCertificate=False,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "dbbe5007",
   "metadata": {},
   "source": [
    "`HanaSparqlQAChain` ties together:\n",
    "\n",
    "1. **Schema-aware SPARQL generation**  \n",
    "2. **Query execution** against SAP HANA  \n",
    "3. **Natural-language answer formatting**\n",
    "\n",
    "\n",
    "## Initialization\n",
    "\n",
    "You need:\n",
    "\n",
    "- An **LLM** to generate and interpret queries  \n",
    "- A **`HanaRdfGraph`** (with connection, `graph_uri`, and ontology)\n",
    "\n",
    "Follow the steps here [HanaRdfGraph](/docs/integrations/graphs/sap_hana_rdf_graph) to know more about creating a `HanaRdfGraph` instance."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "699c9c99",
   "metadata": {},
   "source": [
    "Import the HanaSparqlQAChain"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8fa69303",
   "metadata": {},
   "outputs": [],
   "source": [
    "from langchain_hana import HanaSparqlQAChain"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4319c81c",
   "metadata": {},
   "outputs": [],
   "source": [
    "qa_chain = HanaSparqlQAChain.from_llm(\n",
    "    llm=llm, graph=graph, allow_dangerous_requests=True, verbose=True\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "522c5294",
   "metadata": {},
   "source": [
    "## Pipeline Overview\n",
    "\n",
    "1. **SPARQL Generation**  \n",
    "   - Uses `SPARQL_GENERATION_SELECT_PROMPT`  \n",
    "   - Inputs:  \n",
    "     - `schema` (Turtle from `graph.get_schema`)  \n",
    "     - `prompt` (user’s question)  \n",
    "2. **Query Post-processing**  \n",
    "   - Extracts the SPARQL code from the llm output.\n",
    "   - Inject `FROM <graph_uri>` if missing  \n",
    "   - Ensure required common prefixes are declared (`rdf:`, `rdfs:`, `owl:`, `xsd:`)  \n",
    "3. **Execution**  \n",
    "   - Calls `graph.query(generated_sparql)`  \n",
    "4. **Answer Formulation**  x\n",
    "   - Uses `SPARQL_QA_PROMPT`  \n",
    "   - Inputs:  \n",
    "     - `context` (raw query results)  \n",
    "     - `prompt` (original question)  "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6f33ffd6",
   "metadata": {},
   "source": [
    "## Prompt Templates\n",
    "\n",
    "\n",
    "#### \"SPARQL Generation\" prompt\n",
    "\n",
    "The `sparql_generation_prompt` is used to guide the LLM in generating a SPARQL query from the user question and the provided schema.\n",
    "\n",
    "#### Answering prompt\n",
    "\n",
    "The `qa_prompt` instructs the LLM to create a natural language answer based solely on the database results.\n",
    "\n",
    "The default prompts can be found here: [`prompts.py`](https://github.com/SAP/langchain-integration-for-sap-hana-cloud/blob/main/langchain_hana/chains/graph_qa/prompts.py)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4572ed2e",
   "metadata": {},
   "source": [
    "## Customizing Prompts\n",
    "\n",
    "You can override the defaults at initialization:\n",
    "\n",
    "```python\n",
    "qa_chain = HanaSparqlQAChain.from_llm(\n",
    "    llm=llm,\n",
    "    graph=graph,\n",
    "    allow_dangerous_requests=True,\n",
    "    verbose=True,\n",
    "    sparql_generation_prompt=YOUR_SPARQL_PROMPT,\n",
    "    qa_prompt=YOUR_QA_PROMPT\n",
    ")\n",
    "```\n",
    "\n",
    "Or swap them afterward:\n",
    "\n",
    "```python\n",
    "qa_chain.sparql_generation_chain.prompt = YOUR_SPARQL_PROMPT\n",
    "qa_chain.qa_chain.prompt              = YOUR_QA_PROMPT\n",
    "```\n",
    "\n",
    "> - `sparql_generation_prompt` must have the input variables: `[\"schema\", \"prompt\"]`\n",
    "> - `qa_prompt` must have the input variables: `[\"context\", \"prompt\"]`"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a443cdd7",
   "metadata": {},
   "source": [
    "## Example: Question Answering over a “Movies” Knowledge Graph\n",
    "\n",
    "**Prerequisite**:  \n",
    "You must have an SAP HANA Cloud instance with the **triple store** feature enabled.  \n",
    "For detailed instructions, refer to: [Enable Triple Store](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/enable-triple-store/)<br />\n",
    "Load the `kgdocu_movies` example data. See [Knowledge Graph Example](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/knowledge-graph-example).\n",
    "\n",
    "Below we’ll:\n",
    "\n",
    "1. Instantiate the `HanaRdfGraph` pointing at our “movies” data graph  \n",
    "2. Wrap it in a `HanaSparqlQAChain` powered by an LLM  \n",
    "3. Ask natural-language questions and print out the chain’s responses  \n",
    "\n",
    "This demonstrates how the LLM generates SPARQL under the hood, executes it against SAP HANA, and returns a human-readable answer.\n",
    "\n",
    "We'll use the `sap-ai-sdk-gen` package. Currently still installed via: \n",
    "\n",
    "`pip install \"sap-ai-sdk-gen[all]\"` \n",
    "\n",
    "Please check [sap-ai-sdk-gen](https://pypi.org/project/sap-ai-sdk-gen/) for future releases."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f638733f",
   "metadata": {},
   "source": [
    "First, create a connection to your SAP HANA Cloud instance."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "6de1a91a",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "from hdbcli import dbapi\n",
    "\n",
    "# Load environment variables if needed\n",
    "load_dotenv()\n",
    "\n",
    "# Establish connection to SAP HANA Cloud\n",
    "connection = dbapi.connect(\n",
    "    address=os.environ.get(\"HANA_DB_ADDRESS\"),\n",
    "    port=os.environ.get(\"HANA_DB_PORT\"),\n",
    "    user=os.environ.get(\"HANA_DB_USER\"),\n",
    "    password=os.environ.get(\"HANA_DB_PASSWORD\"),\n",
    "    autocommit=True,\n",
    "    sslValidateCertificate=False,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4b66b111",
   "metadata": {},
   "source": [
    "Then, set up the knowledge graph instance"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "c1be66d8",
   "metadata": {},
   "outputs": [],
   "source": [
    "from gen_ai_hub.proxy.langchain.openai import ChatOpenAI\n",
    "from langchain_hana import HanaRdfGraph, HanaSparqlQAChain\n",
    "\n",
    "# from langchain_openai import ChatOpenAI  # or your chosen LLM"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "bfad5f94",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Set up the Knowledge Graph\n",
    "graph_uri = \"kgdocu_movies\"\n",
    "\n",
    "graph = HanaRdfGraph(\n",
    "    connection=connection,\n",
    "    graph_uri=graph_uri,\n",
    "    auto_extract_ontology=True\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "ad4c00e2",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n",
      "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n",
      "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n",
      "\n",
      "<http://kg.demo.sap.com/acted_in> a owl:ObjectProperty ;\n",
      "    rdfs:label \"acted_in\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Actor> ;\n",
      "    rdfs:range <http://kg.demo.sap.com/Film> .\n",
      "\n",
      "<http://kg.demo.sap.com/dateOfBirth> a owl:DatatypeProperty ;\n",
      "    rdfs:label \"dateOfBirth\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Actor> ;\n",
      "    rdfs:range xsd:dateTime .\n",
      "\n",
      "<http://kg.demo.sap.com/directed> a owl:ObjectProperty ;\n",
      "    rdfs:label \"directed\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Director> ;\n",
      "    rdfs:range <http://kg.demo.sap.com/Film> .\n",
      "\n",
      "<http://kg.demo.sap.com/genre> a owl:ObjectProperty ;\n",
      "    rdfs:label \"genre\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Film> ;\n",
      "    rdfs:range <http://kg.demo.sap.com/Genre> .\n",
      "\n",
      "<http://kg.demo.sap.com/placeOfBirth> a owl:ObjectProperty ;\n",
      "    rdfs:label \"placeOfBirth\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Actor> ;\n",
      "    rdfs:range <http://kg.demo.sap.com/Place> .\n",
      "\n",
      "<http://kg.demo.sap.com/title> a owl:DatatypeProperty ;\n",
      "    rdfs:label \"title\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Film> ;\n",
      "    rdfs:range xsd:string .\n",
      "\n",
      "rdfs:label a owl:DatatypeProperty ;\n",
      "    rdfs:label \"label\" ;\n",
      "    rdfs:domain <http://kg.demo.sap.com/Actor>,\n",
      "        <http://kg.demo.sap.com/Director>,\n",
      "        <http://kg.demo.sap.com/Genre>,\n",
      "        <http://kg.demo.sap.com/Place> ;\n",
      "    rdfs:range xsd:string .\n",
      "\n",
      "<http://kg.demo.sap.com/Director> a owl:Class ;\n",
      "    rdfs:label \"Director\" .\n",
      "\n",
      "<http://kg.demo.sap.com/Genre> a owl:Class ;\n",
      "    rdfs:label \"Genre\" .\n",
      "\n",
      "<http://kg.demo.sap.com/Place> a owl:Class ;\n",
      "    rdfs:label \"Place\" .\n",
      "\n",
      "<http://kg.demo.sap.com/Actor> a owl:Class ;\n",
      "    rdfs:label \"Actor\" .\n",
      "\n",
      "<http://kg.demo.sap.com/Film> a owl:Class ;\n",
      "    rdfs:label \"Film\" .\n",
      "\n",
      "\n"
     ]
    }
   ],
   "source": [
    "# a basic graph schema is extracted from the data graph. This schema will guide the LLM to generate a proper SPARQL query.\n",
    "schema_graph = graph.get_schema\n",
    "print(schema_graph.serialize(format=\"turtle\"))"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1bd22a30",
   "metadata": {},
   "source": [
    "After that, initialise the LLM."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "2356fce5",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Initialize the LLM\n",
    "llm = ChatOpenAI(proxy_model_name=\"gpt-4o\", temperature=0)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7c18d596",
   "metadata": {},
   "source": [
    "Then, we create a SPARQL QA Chain"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "c728654b",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a SPARQL QA Chain\n",
    "chain = HanaSparqlQAChain.from_llm(\n",
    "    llm=llm,\n",
    "    verbose=True,\n",
    "    allow_dangerous_requests=True,\n",
    "    graph=graph,\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "b426da8d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "\n",
      "\u001b[1m> Entering new HanaSparqlQAChain chain...\u001b[0m\n",
      "Generated SPARQL:\n",
      "\u001b[32;1m\u001b[1;3m```\n",
      "PREFIX kg: <http://kg.demo.sap.com/>\n",
      "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n",
      "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n",
      "SELECT ?actorLabel\n",
      "WHERE {\n",
      "    ?movie rdf:type kg:Film .\n",
      "    ?movie kg:title ?movieTitle .\n",
      "    ?actor kg:acted_in ?movie .\n",
      "    ?actor rdfs:label ?actorLabel .\n",
      "    FILTER(?movieTitle = \"Blade Runner\")\n",
      "}\n",
      "```\u001b[0m\n",
      "Final SPARQL:\n",
      "\u001b[33;1m\u001b[1;3m\n",
      "PREFIX kg: <http://kg.demo.sap.com/>\n",
      "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n",
      "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n",
      "SELECT ?actorLabel\n",
      "\n",
      "FROM <kgdocu_movies>\n",
      "WHERE {\n",
      "    ?movie rdf:type kg:Film .\n",
      "    ?movie kg:title ?movieTitle .\n",
      "    ?actor kg:acted_in ?movie .\n",
      "    ?actor rdfs:label ?actorLabel .\n",
      "    FILTER(?movieTitle = \"Blade Runner\")\n",
      "}\n",
      "\u001b[0m\n",
      "Full Context:\n",
      "\u001b[32;1m\u001b[1;3mactorLabel\n",
      "Morgan Paull\n",
      "William Sanderson\n",
      "James Hong\n",
      "Brion James\n",
      "Q81328\n",
      "M. Emmet Walsh\n",
      "Joe Turkel\n",
      "Daryl Hannah\n",
      "Joanna Cassidy\n",
      "Rutger Hauer\n",
      "Hy Pyke\n",
      "Sean Young\n",
      "Edward James Olmos\n",
      "\u001b[0m\n",
      "\n",
      "\u001b[1m> Finished chain.\u001b[0m\n",
      "The actors who acted in Blade Runner are Morgan Paull, William Sanderson, James Hong, Brion James, M. Emmet Walsh, Joe Turkel, Daryl Hannah, Joanna Cassidy, Rutger Hauer, Hy Pyke, Sean Young, and Edward James Olmos.\n"
     ]
    }
   ],
   "source": [
    "# output = chain.invoke(\"Which movies are in the data?\")\n",
    "# output = chain.invoke(\"In which movies did Keanu Reeves and Carrie-Anne Moss play in together\")\n",
    "# output = chain.invoke(\"which movie genres are in the data?\")\n",
    "# output = chain.invoke(\"which are the two most assigned movie genres?\")\n",
    "# output = chain.invoke(\"where were the actors of \"Blade Runner\" born?\")\n",
    "# output = chain.invoke(\"which actors acted together in a movie and were born in the same city?\")\n",
    "output = chain.invoke(\"which actors acted in Blade Runner?\")\n",
    "\n",
    "print(output[\"result\"])"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e233a4c1",
   "metadata": {},
   "source": [
    "### What’s happening under the hood?\n",
    "\n",
    "1. **SPARQL Generation**  \n",
    "   The chain invokes the LLM with your Turtle-formatted ontology (`graph.get_schema`) and the user’s question using the `SPARQL_GENERATION_SELECT_PROMPT`. The LLM then emits a valid `SELECT` query tailored to your schema.\n",
    "\n",
    "2. **Pre-processing & Execution**  \n",
    "   - **Extract & clean**: Pull the raw SPARQL text out of the LLM’s response.  \n",
    "   - **Inject graph context**: Add `FROM <graph_uri>` if it’s missing and ensure common prefixes (`rdf:`, `rdfs:`, `owl:`, `xsd:`) are declared.  \n",
    "   - **Run on HANA**: Execute the finalized query via `HanaRdfGraph.query()` over your named graph.\n",
    "\n",
    "3. **Answer Formulation**  \n",
    "   The returned CSV (or Turtle) results feed into the LLM again—this time with the `SPARQL_QA_PROMPT`. The LLM produces a concise, human-readable answer strictly based on the retrieved data, without hallucination.\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "langchain-hana-0Dgwpkzf-py3.13",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}