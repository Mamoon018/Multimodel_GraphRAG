
from src.document_parsing.sample_data import sample_textual_vectorized_payload_insertion_list, sample_multi_modal_vectorized_payload_insertion_list
from utils import Milvus_client



class graphdb_processor():
    """
    It contains the methods that processes atomic units (textual & non-textual) in order to generate neo4j knowledge
    graph.
    1- Get the chunk from the VDB.
    2- PROMPT the LLM to extract the entities, relationships along with their description and content keywords.
    3- Format the output of the LLM - into dicts containing entities info as well as metadata. 
    4- Create the relationships with the Parent entity info generated with atomic units (Only for Multi-nomial Info KG)
    5- Push the data to the Graph database 
    """

    def __init__(self, textual_VBD_extracted_chunk, multi_modal_VDB_extracted_chunks):
        self.textual_VBD_extracted_chunk = textual_VBD_extracted_chunk
        self.multi_modal_VDB_extracted_chunks = multi_modal_VDB_extracted_chunks
        self.milv_client = None

    def __run_graphdb_processor__(self):
        """
        It initializes the different behaviors of the graphdb_process class by calling its method to act 
        upon the data it has received. It is the function that orchestrates the implementation of the
        class.
        """

        # Get the multi-modal chunks
        extracted_multimodal_chunks = self.multi_modal_info_extraction_for_KG()
        return extracted_multimodal_chunks
 

    def multi_modal_info_extraction_for_KG(self):
        """
        It takes the multi-modal atomic units, entity info and entity summary of those units.
        1- Atomic unit will be extracted from the VDB.
        2- Entity info and Entity summary of multi-modal content from metadata of VDB. (Need to add this to metadata first)
        3- Feeds LLM the atomic unit to extract entities and relationships between them. 
        4- In particular for multi-model units, an entity info of figure (Table,Image etc) is going to be considered
           as the Parent-node. Whereas, entities extracted from the entity description will be considered child-nodes.
        5- We will create the relationship of child-nodes with parent nodes.
        6- From the atomic unit content, some 'content keywords'(high level) will also be extracted.
        7- Push the data to the Graph Database for the creation of knowledge Graph.
        
        **Args:**
        Multi_modal_atomic_units (list[dict]): It is the list of content units, which contains decription and other metadata related fields.

        **Returns:** 
        entities (list[dict]): It is the list of entities along with their details.
        relationships (list[dict]): It is the list of relationships between entities along with details explaining those relationships.

        Entities Extraction --> 
        1- Entity type : Person, Event, Organization, role, device, disease, inst

        """

        # lets extract the multi-modal chunks from Milvus VDB
        self.milv_client = Milvus_client()

        multi_model_milvus_extracted_chunks = self.milv_client.query(
            collection_name= "Multi_modal_VDB_collection",
            output_fields=["chunk_id", "doc_id", "raw_content", "metadata"],
            limit = 2
        )


        return multi_model_milvus_extracted_chunks[0:]






## Final Run of Graphdb Processor

graphdb = graphdb_processor(textual_VBD_extracted_chunk=sample_textual_vectorized_payload_insertion_list,
                            multi_modal_VDB_extracted_chunks=sample_multi_modal_vectorized_payload_insertion_list)

output = graphdb.__run_graphdb_processor__()

print(output)










