import pymongo
import requests
import rest_db 
import pandas as pd
import sys
sys.path.append('ml_retrievers/')
import fastembed_wrap

client = pymongo.MongoClient("mongodb+srv://mayank:mayank123@virtualsynccluster.xxs5t9r.mongodb.net/?retryWrites=true&w=majority")


def fetch_rest_db():
    db_client = rest_db.RestDB()
    all_items_dump = db_client.fetch_all_items()
    return all_items_dump

def generate_fast_emb_df(doc):
    prep_text = f"""{doc['post_text']}\n{f'This article is written by {doc["write_name"]}.'if doc['write_name'].strip()!='' else ''}
                                \n{f'The author professional headline is {doc["writer_details"]}.' if doc['writer_details'].strip()!='' else ''}"""
    return fastembed_wrap.generate_embedding([prep_text])[0]

def transfer_to_atlas(collection):
    all_items_dump = fetch_rest_db()
    df = pd.DataFrame(all_items_dump)
    df['fast_embed'] = df.apply(lambda x: generate_fast_emb_df(x), axis=1)
    del df['_id']
    prep_docs = df.to_dict(orient='records')
    collection.insert_many(prep_docs)

if __name__ == "__main__":
    db = client["vysncup"]
    collection = db["fast_embeded"]
    transfer_to_atlas(collection)
    print("Successfully migrated!")
    ## create index using python currently manually ui to create index

       