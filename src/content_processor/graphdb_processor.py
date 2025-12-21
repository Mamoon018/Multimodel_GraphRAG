

from src.document_parsing.sample_data import sample_textual_vectorized_payload_insertion_list, sample_multi_modal_vectorized_payload_insertion_list, Milvus_extracted_multimodal_chunks
from utils import Milvus_client, perplexity_llm
from src.content_processor.prompt import ENTITIES_GENERATOR_PROMPT
import os 
import perplexity


perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

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
        milvus_chunks = self.multi_modal_info_extraction_for_KG()
        KG_entities = self.entities_generation_for_multimodal_chunks(milvus_extracted_data= milvus_chunks)

        return KG_entities
 

    def multi_modal_info_extraction_for_KG(self):
        """
        It takes the multi-modal atomic units, entity info and entity summary of those units.
        1- Atomic unit will be extracted from the VDB. (Done)
        BEFORE:  Entity info and Entity summary of multi-modal content from metadata of VDB. (Done)

        **Args:**
        Multi_modal_atomic_units (list[dict]): It is the list of content units, which contains decription and other metadata related fields.

        **Returns:** 
        entities (list[dict]): It is the list of entities along with their details.
        relationships (list[dict]): It is the list of relationships between entities along with details explaining those relationships.

        Entities Extraction --> 
        1- Entity type : Person, Event, Organization, role, device, disease, inst

        """

        # lets extract the multi-modal chunks from Milvus VDB
        # For Sampling Purpose, we will use saved extracted data.
        Milvus_extracted_multimodal = Milvus_extracted_multimodal_chunks
        """
        self.milv_client = Milvus_client()

        multi_model_milvus_extracted_chunks = self.milv_client.query(
            collection_name= "Multi_modal_VDB_collection",
            output_fields=["chunk_id", "doc_id", "raw_content", "metadata"],
            limit = 2
        )
        """
        

        return Milvus_extracted_multimodal
    
    def entities_generation_for_multimodal_chunks(self,milvus_extracted_data):

        """
        1- Fetch the entity info that needs to be passed to LLM.
        2- Feeds content_of_chunk, parent_entity_name, and parent_entity_type to the LLM the atomic unit to extract entities and relationships between them. 
        3- In particular for multi-model units, an entity info of figure (Table,Image etc) is going to be considered
           as the Parent-node. Whereas, entities extracted from the entity description will be considered child-nodes.
        4- We will create the relationship of child-nodes with parent nodes.
        5- From the atomic unit content, some 'content keywords'(high level) will also be extracted.
        6- Push the data to the Graph Database for the creation of knowledge Graph.
        
        """

        # Compose the Parent entity info 
        content_of_chunk = milvus_extracted_data.get("raw_content",[])
        meta_data_of_chunk = milvus_extracted_data.get("metadata",[])
        entity_summary_of_chunk = meta_data_of_chunk.get("entity_summary",[])
        for i in entity_summary_of_chunk:
            Parent_entity_name = i.get("entity_name",[])
            Parent_entity_type = i.get("entity_type",[])

        entity_info:dict = {
            "parent_entity_name":Parent_entity_name, 
            "parent_entity_type": Parent_entity_type, 
            "content": content_of_chunk
            }
        
        # Extract entities using LLM
        perplexity_client = perplexity_llm(api_key=perplexity_api_key,
                                           retries=1)
        
        prompt = ENTITIES_GENERATOR_PROMPT

        try:
            # Generate perplexity response
            llm_content_description = perplexity_client.chat.completions.create(
                messages= 
                        [
                            {
                                "role": "user", 
                                "content" :  
                                    [ 
                                        {
                                            "type" : "text",
                                            "text": prompt
                                        },
                                        {
                                            "type": "text",
                                            "text": f"here is the input text: {content_of_chunk}"
                                        }
                                    ]
                            }
                        ],
                model= "sonar"

            )

            KG_material = llm_content_description.choices[0].message.content

            # For testing purpose.
            with open("LLM_extraction_output.txt", "w", encoding= "utf-8") as f:
                f.write(KG_material)
            
            return KG_material


        except perplexity.BadRequestError as e:
            print(f"Invalid request parameters: {e}")
        except perplexity.RateLimitError as e:
            print("Rate limit exceeded, please retry later")
        except perplexity.APIStatusError as e:
            print(f"API error: {e.status_code}")









## Final Run of Graphdb Processor

graphdb = graphdb_processor(textual_VBD_extracted_chunk=sample_textual_vectorized_payload_insertion_list,
                            multi_modal_VDB_extracted_chunks=sample_multi_modal_vectorized_payload_insertion_list)

output = graphdb.__run_graphdb_processor__()

print(output)










