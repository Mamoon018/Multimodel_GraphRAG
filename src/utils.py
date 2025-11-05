

from dataclasses import dataclass

from src.document_parsing.data_extraction import MinerU_Parser
from src.document_parsing.sample_data import combined_knowledge_units, current_multimodel_unit



"""
Utils Functions:

1- Knowledge units splitter
2- Context extractor for multi-modal content

"""
                        ##  1-  Knowledge units splitter  ##

# Define the function to split the knowledge units into textual and non-textual units

def units_splitter(knowledge_units_list:list):
    """
    This function takes the list of the knowledge units created in the parsing process from minerU output, and 
    filter out the textual and non-textual knowledge units on the basis of their content type, into two different
    objects. 

    **Args:**
    knowledge_units_list (list): It is the list of the knowledge units - combined textual and non-textual units.

    **Returns:**
    textual_knowledge_units (list): It is the list of the textual knowledge units.
    multi-model_knowledge_units (list): It is the list of the non-textual knowledge units.

    **Raises:**

    Implementation workflow:
    
    1- Initiate the two lists to store respective type of units separately.
    2- Iterate over the units using for loop 
    3- If content type is in ["title","text"]: append the list for textual knowledge units
    4- If content type == "table": append the list for non-textual knowledge units
    5- Return the textual_knowledge_units, non_textual_knowledge_units
    
    """

    # Initialize the minerU parser
    #### FREEZED FOR TESTING PURPOSE ####
    #init_minerU = MinerU_Parser(data_file_path=knowledge_units_list)
    #knowledge_units_list = init_minerU.format_minerU_output()

    complete_knowledge_units = knowledge_units_list

    # Initialize the lists for textual and non-textual units separately
    multi_model_units = []
    textual_units = []

    for unit in complete_knowledge_units:
        unit = dict(unit)

        # Fetch the textual units
        content_type = unit.get("content_type")
        if content_type in ["text","title"]:
            textual_units.append(unit)
        
        # Fetch the non-textual units
        elif content_type == "table":
            multi_model_units.append(unit)

    return multi_model_units,textual_units





                        ####  2-  Context Extractor  ####


class context_extractor():
    """
    It contains the context extractor for the provided chunk. It can process the Textual-chunk as well as Multi-model chunk to get
    the context around the provided chunk. 

    SCALED FORM OF CLASS - FINAL AFTER REFACTERICATION:
    Main function run:
    It aligns all the function together to run the context extractor
    
    Input source format:
    Atomic units content list (list): It is the list of the combined knowledge atomic units

    Output producer strategy:
    Chunks context (str): It is the approach where we will extract the chunks text that is surrounding the underneath text

    Final output formatting: 
    Truncate the text: It is for ensuring that generated context is within the token limits

    """
    def __init__(self,all_knowledge_units):

        self.all_knowledge_units:list[dict[str]] = combined_knowledge_units

    
    # Create the context extractor for multi-model content
    def multi_model_context_extractor(self, multi_model_knowledge_units:list[dict[str]]):

        """
        It takes the multi-model atomic unit list, fetches the details of the multi-model content such as index on page 
        and page number. It will access the combined knowledge units & will extract the units around the given content.

        **Args:**
        multi_model_knowledge_units (list[dict[str]]): It is the list of multi-model atomic units
        combined_knowledge_units (list[dict[str]]): It is the list of the comined textual and multi-model atomic units. 

        **Returns:**
        chunk_context (list[str]): It is the list of the chunks surroudning the content.

        """

        # Call the input variables 
        multi_model_units = multi_model_knowledge_units
        combined_atomic_units = self.all_knowledge_units

        # fetches the information of the current unit 
        current_unit = current_multimodel_unit
        for chunk in current_unit:
            
            if "table_image_path" in chunk:
                page_of_chunk = chunk.get("page_no.","")
                index_of_current_chunk = chunk.get("index_on_page","")
                table_image_path = chunk.get("table_image_path","")
            elif "table_caption" in chunk:
                page_of_chunk = chunk.get("page_no.","")
                index_of_current_chunk = chunk.get("index_on_page","")
                table_caption = chunk.get("table_caption","")
        
        # get the surrounding chunks from the combined atomic units dict
        """
        Surrounding chunks: (For Multi-model content, it makes sense to fetch the two next & two previous chunks. As
        we usually give description of multi-model content after it's display and some context before its display.)
        0- Initialize the list to store the contextual (Done)
        1- Use the current unit info details to get the current page number (Done)
        2- Calculate the previouse page number and the next page number (Done)
        3- Get the list of the number of indexes on the current page (Done)
        4- check if index of the current unit is in minima zone = (minim or minim + 1) or maxima = (maximum - 1) zone index of the page (Done)
        5- If current chunk neither lies in minima nor maxima index of the current page then just take two next and two previouse chunks of current page (Done)
        6- If lies in minima zone, then filter out the units of previous page. (Done)
        7- fetch the last two units of previous page (Done)
        8- If lies in maxima zone, then filter out the units of next page (Done)
        9- fetch the first two units of next page (Done)
        In this way, we will be able to get the surrounding units required to extract the context (Done)
        """

        current_page = page_of_chunk
        previous_page = page_of_chunk - 1
        next_page = page_of_chunk + 1

        # Fetch all the units for the current page
        units_of_current_page = [unit for unit in combined_atomic_units if unit["page_no."] == current_page]
        

        # Calculate minima & maxima zone
        for indexes in units_of_current_page:
            count =+ 1
            index_of_current_page = indexes["index_on_page"]
            if count == 1:
                lowest_index_of_page = index_of_current_page

        maximum_index_of_page = index_of_current_page
        minima = lowest_index_of_page + 1
        maxima_zone = maximum_index_of_page - 1

        # Based on the placement of the current chunk, we will extract the surrounding chunks
        if index_of_current_chunk > maxima_zone:
            need_to_extract_from_next_page = True
        else:
            need_to_extract_from_next_page = False
            need_to_extract_from_current_page = True
        if index_of_current_chunk < minima:
            need_to_extract_from_previous_page = True
        else: 
            need_to_extract_from_previous_page = False 
            need_to_extract_from_current_page = True
        
        # Extract the list of chunks
        list_of_context_chunks = []
        
        if need_to_extract_from_next_page:

            # get two previous chunks from current page
            count = 1
            index_previous_chunk_of_CP = index_of_current_chunk - count
            index_previous_chunk_of_CP = max(0,index_previous_chunk_of_CP)
            for unit_of_CP in units_of_current_page:
                if unit_of_CP["index_on_page"] == index_previous_chunk_of_CP:
                    count =+ 1
                    if unit_of_CP["content_type"] == "text" and count <= 3:
                        previous_chunk_of_CP = unit_of_CP.get("raw_content","")
                        list_of_context_chunks.append(previous_chunk_of_CP)
                    elif unit_of_CP["content_type"] == "title" and count < 3: 
                        count =+ 1                                              # if found title in previous chunk, then we need to chunk behind that title as it would belong to previous heading.
                        previous_chunk_of_CP = unit_of_CP.get("raw_content","")
                        list_of_context_chunks.append(previous_chunk_of_CP)      
                    else:
                        break


            # Get two chunks of the next page
            units_of_next_page = [units for units in combined_atomic_units if units["page_no."] == next_page]
            """
            1- Extract first two chunks of the next page only if they are text - otherwise, break the loop.
            """
            count = 0
            for unit_of_NP in units_of_next_page:
                count =+ 1
                if unit_of_NP["content_type"] == "text" and count < 3:
                    chunk_of_NP = unit_of_NP.get("raw_content","")
                    list_of_context_chunks.append(chunk_of_NP)
                else:
                    break

            # Minima Zone: fetch maximum two chunks from previous page before heading, and next two chunks of current page before heading.
        if need_to_extract_from_previous_page:
            units_of_previous_page = [units for units in combined_atomic_units if units["page_no."] == previous_page]
            units_of_previous_page = sorted(units_of_previous_page, key=lambda x:x["index_on_page"], reverse=True)
            
                        # Two chunks from previous page
            count = 0
            for unit_of_PP in units_of_previous_page:
                count =+ 1
                if unit_of_PP["content_type"] == "text" and count < 3:
                    chunk_of_PP = unit_of_PP.get("raw_content","")
                    list_of_context_chunks.append(chunk_of_PP)
                elif unit_of_PP["content_type"] == "title" and count < 3:
                    count =+ 1
                    chunk_of_PP = unit_of_PP.get("raw_content","")
                    list_of_context_chunks.append(chunk_of_PP)
                else:
                    break
                        # Next two chunks from current page
            count = 1
            index_next_chunk_of_CP = index_of_current_chunk + count
            for unit_of_CP in units_of_current_page:
                if unit_of_CP["index_on_page"] == index_next_chunk_of_CP:
                    count =+ 1
                    if unit_of_CP["content_type"] == "text" and count <= 3:
                        next_chunk_of_CP = unit_of_CP.get("raw_content","")
                        list_of_context_chunks.append(next_chunk_of_CP)                
                    else:
                        break

        
        if need_to_extract_from_current_page:
            # We have already calculated units for current page

            # Previous chunks of current page
            """
            1- Case_no.1: If title type is coming first, and as previous chunk then pick title type considering it reference for figure and terminate the loop.
            2- Case_no.2: If text type is coming first, & then title type as previous chunks then pick both and terminate the loop.
            3- Case_no.3: If text type is coming as 2 times as previous chunks then pick both and terminate the loop.
            """
            count = 1
            index_previous_chunk_of_CP = index_of_current_chunk - count
            index_previous_chunk_of_CP = max(0,index_previous_chunk_of_CP)
            for unit_of_CP in units_of_current_page:
                if unit_of_CP["index_on_page"] == index_previous_chunk_of_CP:
                    
                    count =+ 1
                    if unit_of_CP["content_type"] == "text" and count <= 3:
                        previous_chunk_of_CP = unit_of_CP.get("raw_content","")
                        list_of_context_chunks.append(previous_chunk_of_CP)
                    elif unit_of_CP["content_type"] == "title" and count < 3: 
                        count =+ 1                                              # if found title in previous chunk, then we need to chunk behind that title as it would belong to previous heading.
                        previous_chunk_of_CP = unit_of_CP.get("raw_content","")
                        list_of_context_chunks.append(previous_chunk_of_CP)      
                    else:
                        break
            # Next chunks of current page
            """
            1- Case_no.1: If text type chunks are coming as next two chunks, then pick both and terminate the loop.
            2- Case_no.2: If there is any chunk other than text type, then terminate the loop.
            """
            count = 1
            index_next_chunk_of_CP = index_of_current_chunk + count
            for unit_of_CP in units_of_current_page:
                if unit_of_CP["index_on_page"] == index_next_chunk_of_CP:
                    count =+ 1
                    if unit_of_CP["content_type"] == "text" and count <= 3: 
                        next_chunk_of_CP = unit_of_CP.get("raw_content","")
                        list_of_context_chunks.append(next_chunk_of_CP)
                    # We do not need to catch next heading coming after current chunk - it will most likely to be starting another topic
                    # and irrelevant to previous figure. So, if next-chunk is not "text" then terminate loop. 
                    else:
                        break

            
        
        return print(list_of_context_chunks)
    
    def multi_model_extractor(self,current_multi_model_unit:list[dict[str]]):
        """
        It takes the current unit, and fetches its placement details to identify the surrouding chunks in the documents and then 
        place them in the chunks for context extraction list.

        Here is the workflow:
        1- Find out the page of current chunk. Using that, find out previous page and next page. (Done)
        2- Access all chunks of current page, extract their index numbers and store in a list in their hierarchical order. (Done)
        3- Access all chunks of the next page, and of the previous page. Extract their index numbers and store separately. (Done)
        4- Put them together in a single list (Done)
        5- Fetch the next two & previous two chunks of the current chunk from this list.
            (a) loop over the list to find out the current chunk (Done)
            (b) Findout the index of the current chunk in the list (Done)
            (c) Fetch the previous two chunks - if text or title then add, under title break the loop else add another chunk. (In-progress)
            (e) Fetch the next two chunks - if text then add else break the loop.
                
        """

        # Input variables
        all_knowledge_units = self.all_knowledge_units
        current_item = current_multimodel_unit

        # As it is list of chunk because of figure & caption unit so, we need to find out only figure unit as reference for placement of current chunk
        unit_of_figure = None
        # Placement details of the current chunk
        for unit in current_item:
            if "table_image_path" in unit:
                page_of_current_unit = unit.get("page_no.","")
                page_index_of_current_unit = unit.get("index_on_page","")
                content_of_current_unit = unit.get("table_image_path","")
                unit_of_figure = unit
        
        surrounding_pages_units = []

        # Previous page & Next page 
        previous_page = page_of_current_unit - 1
        next_page = page_of_current_unit + 1
        pages_relvant_for_context = [previous_page,page_of_current_unit,next_page]
        # Fetch all the chunks from previous page, current page, and next page (In this hierarchical order)
        for page in pages_relvant_for_context:
            for unit in combined_knowledge_units:
                if unit.get("page_no.") == page:
                    surrounding_pages_units.append(unit)

        # Fetch the index of the current chunk in the list of surrounding chunks
        index_of_current_unit = surrounding_pages_units.index(unit_of_figure)
        
        # Fetch previous two chunks
        range_of_surrounding_chunks = list(range(index_of_current_unit-2, index_of_current_unit+3))
        list_of_context_chunks = [surrounding_pages_units[i] for i in range_of_surrounding_chunks]

        return print(list_of_context_chunks)


if __name__ == "__main__":

    multi_model_knowledge_units, textual_knowledge_units = units_splitter(knowledge_units_list=combined_knowledge_units)

    extractor = context_extractor(all_knowledge_units=combined_knowledge_units)
    extractor.multi_model_extractor(current_multi_model_unit=current_multimodel_unit)

