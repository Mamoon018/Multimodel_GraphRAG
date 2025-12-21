
TABLE_CONTENT_WITH_CONTEXT_PROMPT = """

You are an expert of interpreting the content of the Tables. Table is considered as multi-model content
which is non-textual content, mainly because it stores the data in columns and rows. You need to understand the 
way data is distributed in the context of columns and rows. 

You will be provided with the image of the table, that contains the datapoints. Along with that, you will be 
provided with the text that is present around the table in the document from which that image has been taken. 
Text is considered to be the context for the table because in documents usually either Tables are described
before or after showing as image. 

You will get some information about the Table from the context text, it will include the details about table. 
However, in order to generate the detailed description of the Table you also need to interpret the
Table data on your own in context of the context text provided to you.

Here are two things that you need to generate in the output:
1) content_description: It is the description of the datapoints of the Table. It includes the interpretation
of the Table content in the light of the context text. Make sure you follow the following guidelines for compiling the data for the 
content_description. 
Guidelines for content_description:
1- Start with brief introduction about the content of the table. Only overview of what information going to tell us and what entities it includes.
2- You only need to explain the stats that are given in the table, you need to interpret those stats. 
3- You do not need to analyze or give your opinion on those stats.
4- Do not give the analysis - only give the interpretation. 
5- Donot give the conclusion or summary at the end. 
6- Extract this information and format it as specified in the schema.

2) entity_summary: It is the summary of the entity for which you are currently generating the description. Make
sure you following the following guidelines for compiling the information for the entity summary. 
Guidelines for entity_summary:
1- It should include the entity name. Choose the name based on the your understanding of what table is constructed for.
2- It should include the entity type. Entity type is obviously "table"
3- It should include the names of the entities that are disucssed in the table. 
3- You should generate the brief description of the entity that will be required to store as a node description in the knowledge graph. 
4- In the entity description, you must include the brief intro about the entity and relationship between the entities.
5- Extract this information and format it as specified in the schema. 


 {contextual_text}
 {address_of_content}

"""

## Prompt for testing purpose for different use-case scenarios
ENTITIES_GENERATOR_PROMPT = """
You are an expert of identifying the entities and relationships between those entities from the text, which can be used
for the creation of knowledge graphs in Graph databases. 
Here entities refers to the technical solution, technical concept, devices, organization, person, technical event, category.
Here relationships refers to the "CLEAR RELATION" that the identified entities share with each other.

--- GOAL ---
Your goal is to look out for the entities and relationships among those identified entities from the provided text, and compile the information in the structured output. 

Step-1: Identiy entities from the text
--- Guidance for extraction of entities ---
1. Identify all entities from the text. For each entity, format the following details:
   entity_name: Name of the entity, capitalize the name.
   entity_type: Make sure it is one of these types: "Mechanism", "Concept", "Technique", "Technical Implementation", "Framework", "Model"
   entity_description: It is the brief description of the entity that you will take from text. It introduces entity.

You need to strictly follow the following format for structuring the entities info,
("entity"<|>"LightRAG"<|>"Framework"<|>"A RAG system using graph and vector retrieval")
("entity"<|>"Dual-level retrieval"<|>"Concept"<|>"Retrieval strategy using two layers")
("entity"<|>"Vector similarity"<|>"Mechanism"<|>"Technique to find semantically similar chunks using DB")##
("entity"<|>"LLM-based profiling"<|>"Technique"<|>"LLM for Profling the query")

Step-2: Identify relationships from the text
--- Guidance for extraction of relationships ---
1. Identify all relationships from the text. For each relationship between entities, format the following details
    source_entity: It is the name of the source entity, as identified in Step-1
    target_entity: It is the name of the target entity, as identified in Step-1
    relationship_description: It is the description of "How" source entity and target entity are related to each other.
    relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details

You need to strictly follow the following format for structuring the relationships info:
("relationship"<|>"LightRAG"<|>"Dual-level retrieval"<|>"Integrates this mechanism to unify retrieval strategies"<|>"architecture, integration"<|>"Main-theme")
("relationship"<|>"Dual-level retrieval"<|>"Vector search"<|>"Combines this technique with graph traversal"<|>"methodology, hybrid-search"<|>"Main-theme")
("relationship"<|>"LightRAG"<|>"Redis"<|>"Optionally supports this tool for session caching"<|>"caching, optimization"<|>"Supporting-theme")

Step-3: Identify the contextual keywords from the text
--- Guidence for extraction of contextual keywords ---
1. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should 
capture the overarching ideas present in the document. You only need to compile this once for a chunk.
Format the content-level key words as given below:
("context keywords"<|>"high level keywords")

Provide final output as List object that contains entities, relationships, context keywords. Use ## as list delimeter. 


"""