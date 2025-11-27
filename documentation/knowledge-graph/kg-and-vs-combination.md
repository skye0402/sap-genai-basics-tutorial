Using the SAP HANA Cloud Vector Engine with the SAP HANA Cloud Knowledge Graph Engine
=====================================================================================

The combination of the SAP HANA Cloud vector engine and the SAP HANA Cloud knowledge graph engine enables developers to create intelligent, context-aware queries that surpass traditional keyword matching. This integration is useful for enhancing search capabilities by providing both similarity insights and explicit relationship understanding.

The vector engine is great for finding matches based on similarities, but the knowledge graph engine adds the ability to understand relationships and connections within your data.

To gain more control over the prompting results of a Large Language Model (LLM) in your application, you can leverage your own specific documents or data using Retrieval Augmented Generation (RAG).

The benefits of RAG using vector searches (pure RAG) include the following:

*   It works with unstructured data and extracts information from documents, emails, reports, and logs.
*   It converts text into embeddings through chunking and vectorization.
*   It is effective when the required context is within a few related documents, and semantic similarity can infer relevant answers.
*   The large language model (LLM) extracts facts to generate responses.
*   It references original documents but lacks structured reasoning.

For more information, see [SAP HANA Database Vector Engine Guide](https://help.sap.com/docs/HANA_CLOUD_DATABASE/c40cab369db246f1a17feea1c031ddc1/8d2675524f454b248de942da9bc04777.html "https://help.sap.com/docs/HANA_CLOUD_DATABASE/c40cab369db246f1a17feea1c031ddc1/8d2675524f454b248de942da9bc04777.html").

The benefits of RAG using the vector engine with the knowledge graph engine (hybrid RAG) include the following:

*   It stores structured and linked data, including entities, relationships, and hierarchies.
*   Knowledge graphs are created from tables, documents, and other sources.
*   Graph queries enable deep context retrieval. The required context is spread across multiple sources, making exact facts, relationships, and historical data accessible.
*   The large language model (LLM) aggregates facts to generate responses.
*   It provides more context, explainability, and complex reasoning by leveraging structured knowledge along with unstructured data.

For information about how to perform a multi model query, see [Multi Model Query Example](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/hybrid-retrieval-augmented-generation-rag-example?locale=en-US&state=PRODUCTION&version=2025_3_QRC "You can perform a multi model query to find the information that fits your criteria.").

Related Information

[Seamless Data Interchange of Vector Data Types](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/seamless-data-interchange-of-vector-data-types?locale=en-US&state=PRODUCTION&version=2025_3_QRC "When the SQL_TABLE function runs inside a SPARQL query, vector data types like REAL_VECTOR and HALF_VECTOR are automatically converted into a user-defined type (UDT) form within SPARQL.")

Multi Model Query Example
You can perform a multi model query to find the information that fits your criteria.

In this hybrid Retrieval Augmented Generation (RAG) scenario, we will show you how to use multiple engines within SAP HANA Cloud to find the nearest warehouses in Germany within a 50 km radius of Frankfurt. These warehouses should be for suppliers that are ISO 9001 certified, have low carbon tax rates, and aren't flagged for customs delays.



To achieve this, do the following:
Conduct a multi model query to identify the warehouses that meet these criteria. For example, use a SPARQL table within the SAP HANA Cloud knowledge graph engine to filter suppliers that comply with the following conditions: ISO 9001 certified, low carbon tax rates, and not flagged for customs delays.
SELECT * FROM SPARQL_TABLE ('
	SELECT ?supplier ?certification ?carbontax ?flag
	FROM <kg_supplychain>
	WHERE {
		?supplier a ‹Supplier› .
		?supplier ‹hasCertification> ?certification .
		?supplier <hasCarbonTaxRate> ?carbontax .
		?supplier <isFlaggedForDelays> ?flag .
		FILTER(?certification = "ISO 9001" && ?carbontax = "low" && STR (?flag) = "false")
}
');

Combine the SPARQL_EXECUTE function in the SAP HANA Cloud knowledge graph engine with vector-based semantic filtering and spatial constraints. This helps identify suppliers located within 50 km of Frankfurt whose past customs report narratives indicate no delays.
This hybrid query leverages the SAP HANA Cloud vector engine, the SAP HANA Cloud knowledge graph engine, and the SAP HANA Cloud spatial engine. It ranks nearby suppliers not only by distance but also by their trustworthiness and performance signals.
CALL SPARQL_EXECUTE(

PREFIX ex: <http://example.org/supplier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?uri ?class ?label ?report ?sco
FROM <kg_supplychain>
WHERE {

	SQL_TABLE ("SELECT \"uri_str\", \ "REPORT_TEXT)", \"SCO\"
	FROM (SELECT *, SCO - FIRST VALUE (sco) OVER (ORDER BY sco DESC) AS diff 
	FROM (SELECT \"SUPPLIER URI\" AS \"uri str\" \"REPORT_TEXT\", COSINE SIMILARITY (\"REPORT_EMBEDDING\", VECTOR_EMBEDDING (''no custom delays'', ''QUERY', ''SAP NEB.20240715'')) 
	AS sco FROM KG SUPPLYCHAIN.SUPPLIER_REPORTS_LOOKUP WHERE \"GEO_LOCATION\".ST_ Distance(ST_GeomEcomText(''POINT(8.6821 50.1109) '', 4326)) < 50000 ORDER BY SCO DESC) ) 
	WHERE diff › -0.2")
	BIND(URI (?uri_str) AS ?uri).
	BIND(?REPORT_TEXT AS ?report).
	BIND(?SCO AS ?sco).

	?uri a ?class.
	?uri <hasCertification> "ISO 9001".
	?uri <hasCarbonTaxRate> "low".
	?uri < isFlaggedForDelays> false.
	OPTIONAL { ?uri rdfs:label ?label . }
}
ORDER BY DESC (?SCO)  
LIMIT 10
',
		'Accept: application/sparql-resultstesv Content-Type: application/sparql-query',
		?,
		?
	);

After running your queries, view the best matches for supplier warehouses:
un,class, label, report,sco
http://example.org/supplier/AlphaGmbH.Supplier,,Consistently on time. No customs issue.,0.615654
http://example.org/supplier/GammaLog/stics.Supplier,, Smooth operations, cleared customs quickly.".0.527002

Multi Model Query Example
=========================

You can perform a multi model query to find the information that fits your criteria.

In this hybrid Retrieval Augmented Generation (RAG) scenario, we will show you how to use multiple engines within SAP HANA Cloud to find the nearest warehouses in Germany within a 50 km radius of Frankfurt. These warehouses should be for suppliers that are ISO 9001 certified, have low carbon tax rates, and aren't flagged for customs delays.

![](https://help.sap.com/doc/5c3488c559d64d2c8b4f331a1d9b281a/2025_3_QRC/en-US/loio3bc6ec969e514536ac51349b12f8ca2c_LowRes.png)

To achieve this, do the following:

1.  Conduct a multi model query to identify the warehouses that meet these criteria. For example, use a SPARQL table within the SAP HANA Cloud knowledge graph engine to filter suppliers that comply with the following conditions: ISO 9001 certified, low carbon tax rates, and not flagged for customs delays.
    
        SELECT * FROM SPARQL_TABLE ('
        	SELECT ?supplier ?certification ?carbontax ?flag
        	FROM <kg_supplychain>
        	WHERE {
        		?supplier a ‹Supplier› .
        		?supplier ‹hasCertification> ?certification .
        		?supplier <hasCarbonTaxRate> ?carbontax .
        		?supplier <isFlaggedForDelays> ?flag .
        		FILTER(?certification = "ISO 9001" && ?carbontax = "low" && STR (?flag) = "false")
        }
        ');
    
2.  Combine the SPARQL\_EXECUTE function in the SAP HANA Cloud knowledge graph engine with vector-based semantic filtering and spatial constraints. This helps identify suppliers located within 50 km of Frankfurt whose past customs report narratives indicate no delays.
    
    This hybrid query leverages the SAP HANA Cloud vector engine, the SAP HANA Cloud knowledge graph engine, and the SAP HANA Cloud spatial engine. It ranks nearby suppliers not only by distance but also by their trustworthiness and performance signals.
    
        CALL SPARQL_EXECUTE(
        
        PREFIX ex: <http://example.org/supplier/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?uri ?class ?label ?report ?sco
        FROM <kg_supplychain>
        WHERE {
        
        	SQL_TABLE ("SELECT \"uri_str\", \ "REPORT_TEXT)", \"SCO\"
        	FROM (SELECT *, SCO - FIRST VALUE (sco) OVER (ORDER BY sco DESC) AS diff 
        	FROM (SELECT \"SUPPLIER URI\" AS \"uri str\" \"REPORT_TEXT\", COSINE SIMILARITY (\"REPORT_EMBEDDING\", VECTOR_EMBEDDING (''no custom delays'', ''QUERY', ''SAP NEB.20240715'')) 
        	AS sco FROM KG SUPPLYCHAIN.SUPPLIER_REPORTS_LOOKUP WHERE \"GEO_LOCATION\".ST_ Distance(ST_GeomEcomText(''POINT(8.6821 50.1109) '', 4326)) < 50000 ORDER BY SCO DESC) ) 
        	WHERE diff › -0.2")
        	BIND(URI (?uri_str) AS ?uri).
        	BIND(?REPORT_TEXT AS ?report).
        	BIND(?SCO AS ?sco).
        
        	?uri a ?class.
        	?uri <hasCertification> "ISO 9001".
        	?uri <hasCarbonTaxRate> "low".
        	?uri < isFlaggedForDelays> false.
        	OPTIONAL { ?uri rdfs:label ?label . }
        }
        ORDER BY DESC (?SCO)  
        LIMIT 10
        ',
        		'Accept: application/sparql-resultstesv Content-Type: application/sparql-query',
        		?,
        		?
        	);
    
3.  After running your queries, view the best matches for supplier warehouses:
    
        un,class, label, report,sco
        http://example.org/supplier/AlphaGmbH.Supplier,,Consistently on time. No customs issue.,0.615654
        http://example.org/supplier/GammaLog/stics.Supplier,, Smooth operations, cleared customs quickly.".0.527002