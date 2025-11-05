

"""
Minima: (When current chunk has index 0)

    Case-1: Index = 0
    Solution: (Assuming title type exception)
        (a) Extract two chunks from previous page. (Done)
        (b) Extract next two chunks from current page (Done)


Maxima: (When current chunk has index among top two highest indexes of page such as if higest index is 17. Maxima zone 17.)
    
    Case-1: Index = 17
    Solution: (Assuming title type exception
        (a) Extract two chunks from next page. (Done)
        (b) Extract previous two chunks from current page (Done) 

        

        
Current page Issue:

    Case-1: Index = 1   (NOT HANDLED)
    Solution: (Assuming title type exception)
        (a) Extract next two chunks from the current page (Done)
        (b) Extract previous two chunks from the current page (Done)      (There is only 1 chunk left)


Current page Issue:
    Case-2: Index = 16   (NOT HANDLED)
    Solution: (Assuming title type exception)
        (a) Extract next two chunks from the current page (Done)          (There is only 1 chunk left)
        (b) Extract previous two chunks from the current page (Done)  

        
Solution questions:
1- How to find out that previous unit is the last unit of the current page?
2- If we are able to find then we can associate the "break" with it in order to ensure it does not run loop anymore.
        

"""


                                        ### APPROACH NO. 2 ###
"""

1- Find out the page of current chunk. Using that, find out previous page and next page.
2- Access all chunks of current page, extract their index numbers and store in a list in their hierarchical order.
3- Access all chunks of the next page, and of the previous page. Extract their index numbers and store separately.
4- Put them together in a single list 
5- Fetch the next two & previous two chunks of the current chunk from this list.
    (a) loop over the list to find out the current chunk
    (b) Findout the index of the current chunk in the list
    (c) Fetch the previous two chunks - if text or title then add, under title break the loop else add another chunk. 
    (e) Fetch the next two chunks - if text then add else break the loop.

"""
