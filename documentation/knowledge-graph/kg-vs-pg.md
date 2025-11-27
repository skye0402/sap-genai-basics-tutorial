Comparing SAP HANA Cloud Property Graph Engine and SAP HANA Cloud Knowledge Graph Engine
========================================================================================

The SAP HANA Cloud knowledge graph engine and the SAP HANA Cloud property graph engine work on different kinds of graphs. Both engines store and analyze connected data, but they use distinct structures to achieve this.

Use this information to help select the appropriate graph database technology for specific use cases, optimizing performance and functionality.

Property Graph
--------------

Property graphs show the relationships between entities. In a property graph, data is represented as vertices (entities) and edges (relationships), where each edge can hold different properties that describe the connection between vertices. Property graphs are stored in SQL tables.

In a supply chain context, a property graph models entities as vertices (products, suppliers, stores) and relationships as edges (supply links, delivery routes). Each vertex and edge can have multiple properties. The vertices are Product A, Supplier X, Store Y. The edges are "Supplier X supplies Product A" and "Product A is delivered to Store Y." Each edge can hold various properties like the distance of a shipment (for example, 100 km), the delivery time (for example, 2 days), and the cost of a transaction (for example, $500).

In this example, a property graph allows you to:

*   Identify the shortest delivery routes between suppliers and stores.
*   Calculate the total cost of supply chain for a given product.
*   Find high-reliability suppliers based on delivery time properties.

Use the property graph engine in scenarios where:

*   You need graph algorithms such as shortest path, centrality, or clustering.
*   Your focus is on analyzing structural relationships, not meaning or semantics.
*   You want to perform fast traversals over large networks of connected data.
*   Your graph data is relational in nature, such as data stored in SQL tables or JSON.

For more information, see [SAP HANA Cloud, SAP HANA Database Property Graph Engine Reference](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/30d1d8cfd5d0470dbaac2ebe20cefb8f.html?locale=en-US&state=PRODUCTION&version=2025_3_QRC "This reference provides information about SAP HANA Property Graph engine. It is organized as follows:").

Knowledge Graph
---------------

Knowledge graphs focus on establishing facts and the logical relationships between those facts. They use a subject-predicate-object structure (triples), where each fact is stored as a relationship. Knowledge graphs are stored in the triple store in RDF format.

In a supply chain context, a knowledge graph captures facts such as "Product A is made from recycled materials," "Supplier X follows sustainable sourcing practices," and "Store Y is located in an eco-friendly area."

A knowledge graph goes beyond simply showing who supplies a product. It allows you to:

*   Discover which suppliers with eco-friendly practices provide products to stores in green-certified regions.
*   Assess sustainability across the supply chain based on combined facts about materials and sourcing.

Use the knowledge graph engine in scenarios where:

*   You need semantic reasoning or integration across diverse datasets.
*   Your queries are contextual and based on meaning, not just structure.
*   You want to enforce or leverage ontologies and linked vocabularies.
*   You are working with federated data, possibly involving external sources.
*   You are building applications with GenAI and domain-specific context.