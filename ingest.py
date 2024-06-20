import os
from pymongo import MongoClient
import datasets
from datasets import load_dataset
from bson import json_util

# MongoDB Atlas URI and client setup
uri = os.environ.get('MONGODB_ATLAS_URI')
client = MongoClient(uri)

# Change to the appropriate database and collection names
db_name = 'sample_airbnb'  # Change this to your actual database name
collection_name = 'rentals'  # Change this to your actual collection name

collection = client[db_name][collection_name]

# Load the "airbnb_embeddings" dataset from Hugging Face
dataset = load_dataset("MongoDB/airbnb_embeddings")

insert_data = []

# Iterate through the dataset and prepare the documents for insertion
# The script below ingests 1000 records into the database at a time
for item in dataset['train']:
    # Convert the dataset item to MongoDB document format
    doc_item = json_util.loads(json_util.dumps(item))
    insert_data.append(doc_item)

    # Insert in batches of 1000 documents
    if len(insert_data) == 1000:
        collection.insert_many(insert_data)
        print("1000 records ingested")
        insert_data = []

# Insert any remaining documents
if len(insert_data) > 0:
    collection.insert_many(insert_data)
    print("{} records ingested".format(len(insert_data)))

print("All records ingested successfully!")
