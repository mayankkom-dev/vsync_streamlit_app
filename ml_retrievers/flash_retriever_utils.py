import flash_rank
import numpy as np

def prep_input_query(input_query):
    # query enrichment
    if len(input_query)<100:
        input_query = f"""I am looking for information about {input_query}"""
    return input_query

def prep_all_items(all_items):
    prep_items = []
    for idx, item in enumerate(all_items):
        item_dict = {
            "id": idx+1,
            "text": item.get('post_text', ''),
            "meta": {"writer_name": item.get('writer_name', ''),
                     "writer_details": item.get('writer_details', '')
                     }
        }
        prep_items.append(item_dict)
    return prep_items

def fetch_flash_topn(input_query, all_items):
    if not all_items:
        return []
    prep_query = prep_input_query(input_query)
    prep_items = prep_all_items(all_items)
    try:
        rank_result = flash_rank.rank_query_passages(prep_query, prep_items)
    except:
        rank_result = []
    
    if len(rank_result)> 20:
        rank_result = [_['id']-1 for _ in rank_result][:20]
    
    return np.array(all_items)[rank_result].tolist()
