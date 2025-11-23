

from dataclasses import dataclass

from src.document_parsing.sample_data import sample_multi_model_chunks_with_llm_description, textual_knowledge_units
from utils import doc_id, document_title, Milvus_client

from pymilvus import DataType, Function, FunctionType
import os
from dotenv import load_dotenv
load_dotenv()

perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

# Here is the document ID
doc_id_generated = doc_id()
doc_title = document_title()



class processor_storage():
    """
    This class handles the tasks related to the storage of the data in vector & Graph databases.
    
    Below is the blueprint of the class:

    Config class: (Check if required or not.)   ---> Can only confirm after initial implementation. If we come across storing configurable parameters then we can create a configdata class for them.
    Main Class: (Finalize the class instances and object instances) ---> 
    Input handler-1: (Finalize the format that we want to pass onto the formatter-1)
    Input handler-2: (Finalize the format that we want to pass onto the formatter-2)
    Formatter for IH-1: (Finalize the final format required to pass onto the textual Vector database)
    Format for IH-2: (Finalize the final format required to pass onto the multi-mode Vector database)
    Processor for storing data: (Finalize the process the we need to implement for storing data in Vector DB)
    Output confirmation: (Finalize the confirmation required for the successful storage of the data)

    """


    def __init__(self, multi_model_chunks_with_llm_description, textual_knowledge_units):

        self.document_id = doc_id_generated
        self.docum_title = doc_title
        self.textual_units = textual_knowledge_units
        self.multi_model_units = multi_model_chunks_with_llm_description

    def __run_processor_storage__(self):
         
        """
        It orchestrate the implementation of the processor storage class, starts from generating the payload chunks,
        ends with push data to vector database.           
        """

        
        lists_of_units = [self.textual_units, self.multi_model_units]
        text_payload_insertion_list = []
        multi_model_payload_insertion_list = []

        current_item_no_textual = 0
        current_item_no_multimodal = 0
        list_no = 0

        for list_of_units in lists_of_units:
            list_no += 1
            for unit in list_of_units:
                  
                if list_no == 1: 
                    current_item_no_textual += 1
                    text_chunk_insertion_data = self.textual_chunk_payload_prep(
                        current_item=unit, 
                        current_item_number=current_item_no_textual
                    )
                    text_payload_insertion_list.append(text_chunk_insertion_data)
                elif list_no == 2:
                    current_item_no_multimodal += 1
                    multimodal_chunk_insertion_data = self.textual_chunk_payload_prep(
                        current_item= unit,
                        current_item_number=current_item_no_multimodal
                    )
                    multi_model_payload_insertion_list.append(multimodal_chunk_insertion_data)
        
        return      text_payload_insertion_list, multi_model_payload_insertion_list


                       

                  
        


    def textual_chunk_payload_prep(self,current_item,current_item_number):

        """
        ##  Textual Units Handler   ##
        It takes the current_unit, and generates the document-id and chunk-id for it, and insert both in that along
        with the document title in order to prepare final payload of the textual units that can be stored in the
        Vector database. (Embeddings for the chunk will be generated separately)

        **Args:**
        Textual_knowledge_units (list[dict]): It is the list of dictionaries that contains textual chunk & placement information.
        
        **Returns:**
        3)      Prepare the payload of the Textual Unit item that will be pushed to the VDB after embeddings generation of its text.

        """


        # Get a document id
        doc_id = self.document_id
        # Get a doc title
        doc_title = self.docum_title

        # Get a chunk id
        current_item_number = str(current_item_number)
        chunk_id = doc_id[0:8] + "-" + "chunk-" + current_item_number

        # Add doc_id, chunk_id in the item to prepare it for the chunk-payload
        current_item["doc_id"] = doc_id
        current_item["chunk_id"] = chunk_id
        current_item["document_title"] = doc_title

        # Get the JSON of Metadata
        metadata = {
            "page_no.": current_item["page_no."],
            "index_on_page": current_item["index_on_page"],
            "content_type": current_item["content_type"],
            "document_title": current_item["document_title"]
        }

        # Using metadata and current item fields, we need to create insertion payload that aligns with schema
        self.chunk_insertion_data = {
            "doc_id": current_item["doc_id"],
            "chunk_id": current_item["chunk_id"],
            "raw_content": current_item["raw_content"],
            "meta_data": metadata
        }

        return self.chunk_insertion_data
    
    def generate_embeddings_function(self,chunks_text_content:list):

        """
        It takes the list of text chunks of the textual_items, and passes it to the openai embedding models that generates the
        vector embeddings of the chunks in a single api call, and then attach the generated vectors back to respective items of
        textual_knowledge_units.

        **Args:**
                chunks_text_content (list): It is the list of the chunks text content that needs to be vectorized using embedding models.

        **Returns:**
                
        """

        text_embedding_function = Function(

            name= "openai_embedding",
            function_type= FunctionType.TEXTEMBEDDING,
            input_field_names= ["raw_content"],
            output_field_names= ["Vectors"],

            params= {
                "provider": "openai",
                "model_name": "text-embedding-3-small"
            }

        )

        return text_embedding_function


    def textual_VDB_collection(self):
        """
        It initializes the milvus client and defines the schema of the collection and load the collection using that 
        schema, also defines the indexing strategy for chunks vectors.

        **Returns:** (str): It returns the confirmation abuot the collection loading 

        """

        # Initialize milvus client
        Client = Milvus_client()
        # Initialize the schema creation 
        text_vectors_schema = Client.create_schema(
                                                    auto_id = False,
                                                    )                            

        # Add embedding function to the schema
        #text_vectors_schema.add_function(self.text_embedding_function)

        # Fields of schema
        text_vectors_schema.add_field(
            field_name= "doc_id",
            datatype=DataType.VARCHAR,
            max_length = 50
        )
        text_vectors_schema.add_field(
            field_name= "chunk_id",
            datatype= DataType.VARCHAR,
            is_primary = True,
            max_length = 50
        )
        text_vectors_schema.add_field(
            field_name= "raw_content",
            datatype= DataType.VARCHAR,
            max_length = 50000
        )
        text_vectors_schema.add_field(
            field_name= "metadata",
            datatype= DataType.JSON
        )
        text_vectors_schema.add_field(
            field_name= "Vectors",
            datatype= DataType.FLOAT_VECTOR, dim = 1536
        )
        
        """
        For prioritising the high recall & high QPS, we will stick with HNSW approach which uses graph to map the 
        data, params (M, ef) can be tuned based on the outcome quality.
        """


        # Indexing for vectors field is must - in order to perform vector search. Currently, we will stick with the
        vector_index_params = Client.prepare_index_params()
        vector_index_params.add_index(
            field_name="Vectors",
            index_name= "dense_vectors_index",
            # As TopK in our case gonna be low, we will choose Graph based approach (HNSW)
            index_type="HNSW",
            metric_type = "COSINE",
            params = {
                "M": 20,
                "efConstruction": 35
            }
        )

        collection_signal = None
        list_of_collections = Client.list_collections()
        if "Textual_collection_1" not in list_of_collections:

                # Let's create the collection which we will use to store the data
                Client.create_collection(
                                            collection_name="Textual_collection_1",
                                            schema= text_vectors_schema,
                                            index_params= vector_index_params)
                collection_signal = "Collection created"

        else:
                    # confirmation of collection creation
                collection_signal = Client.load_collection(
                        collection_name="Textual_collection_1"
                    )
                collection_signal = "Collection loaded!"
                
        list_of_collections = Client.list_collections()

        return collection_signal, list_of_collections





if __name__ == "__main__":

    db_storage = processor_storage()

    results = db_storage.__run__()

    print(results)
    

    



        
