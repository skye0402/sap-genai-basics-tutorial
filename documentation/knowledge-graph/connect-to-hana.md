Python Interface
================

Use the Python interface to connect to an SAP HANA database and execute SPARQL queries and update options.

SAP HANA database supports multiple connectivity interfaces, including Python, Node.js, Java, and so on, that allow you to develop your own stand-alone applications. All these interfaces use drivers like JDBC or ODBC to connect to SAP HANA Cloud and can provide a higher-level API to use with the programming language of your choice. While you can use these interfaces, we recommend using the SQL console in SAP HANA Cloud Central or the SAP HANA HDBSQL command-line interface.

The Python command-line interface takes your SPARQL query, wraps and packages it as SQL, and then runs the SQL statement.

For information about installing and connecting to the Python client interface, see [Python Application Programming](https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/f3b8fabf34324302b123297cdbe710f0.html "https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/f3b8fabf34324302b123297cdbe710f0.html") and the [SAP HANA Client Interface Programming Reference](https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/ce5509c492af4a9f84ee519d5659f186.html "https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/ce5509c492af4a9f84ee519d5659f186.html").

Example
-------

    from hdbcli import dbapi
     
    # connect to database using username/password
    conn = dbapi.connect(user='db-username', password='db-user-password', address='database host', port=port_number, ...)
     
    # call stored procedure to execute SPARQL Query
    resp = conn.cursor().callproc('SPARQL_EXECUTE', ('SPARQL Query or RDF Turtle Data', 'Metadata headers describing Input and/or Output', '?', None) )
    # resp[3] --> OUT: SAP HANA Cloud knowledge graph engine Response Metadata/Headers
    # resp[2] --> OUT: SAP HANA Cloud knowledge graph engine Response
    # resp[1] --> IN: Metadata headers describing Input and/or Output
    # resp[0] --> IN: SPARQL Query or RDF Turtle Data

Related Information

[SQL Interface](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/sql-interface?locale=en-US&state=PRODUCTION&version=2025_3_QRC "The SAP HANA Cloud knowledge graph engine uses the existing SAP HANA Connectivity Interface for connecting and authenticating users and clients to the SAP HANA system and then uses the SQL interface as a gateway to send SPARQL Query and SPARQL Update statements to the SAP HANA Cloud knowledge graph engine.")

[LangChain](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/langchain?locale=en-US&state=PRODUCTION&version=2025_3_QRC "Integrate LangChain with SAP HANA Cloud to make use of vector searches, knowledge graphs, and other in-database capabilities as part of LLM-driven applications.")