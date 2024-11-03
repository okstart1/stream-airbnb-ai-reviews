import os
from dotenv import load_dotenv
from pymongo import MongoClient
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Get MongoDB Atlas URI and other configurations from environment variables
MONGO_URI = os.getenv('MONGODB_ATLAS_URI')
DATABASE_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Connect to MongoDB
client = MongoClient(MONGO_URI, appname='devrel.content.python')
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def save_reviews(listing_id, new_review):
    collection.update_one({"_id": int(listing_id)}, {"$push": {"reviews": new_review}})
    return True

def save_deal(location, deal, price, category):
    deal_data = {
        "Location": location,
        "Deal": deal,
        "Price": price,
        "Category": category
    }
    collection.insert_one(deal_data)
    return True

def get_all_deals():
    return list(collection.find())

def get_filtered_deals(location, category):
    query = {}
    if location:
        query["Location"] = location
    if category:
        query["Category"] = category
    return list(collection.find(query))

# Streamlit UI
st.title("🏡 View products")

# Example usage of save_deal function
if st.button("Save Deal"):
    location = st.text_input("Location")
    deal = st.text_input("Deal")
    price = st.text_input("Price")
    category = st.text_input("Category")
    if location and deal and price and category:
        save_deal(location, deal, price, category)
        st.success("Deal saved successfully!")

# User input for filtering products
st.header("Filter Products")
location_input = st.text_input("Enter Location")
category_input = st.text_input("Enter Category")

# Display filtered products
st.header("Filtered Products")
filtered_deals = get_filtered_deals(location_input, category_input)
for deal in filtered_deals:
    st.write(f"Location: {deal['Location']}")
    st.write(f"Deal: {deal['Deal']}")
    st.write(f"Price: {deal['Price']}")
    st.write(f"Category: {deal['Category']}")
    st.write("---")

# Display all products
st.header("All Products")
deals = get_all_deals()
for deal in deals:
    st.write(f"Location: {deal['Location']}")
    st.write(f"Deal: {deal['Deal']}")
    st.write(f"Price: {deal['Price']}")
    st.write(f"Category: {deal['Category']}")
    st.write("---")