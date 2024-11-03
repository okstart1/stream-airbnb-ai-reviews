import os
from dotenv import load_dotenv
from pymongo import MongoClient
import streamlit as st
import googlemaps

# Load environment variables from .env file
load_dotenv()

# Get MongoDB Atlas URI and other configurations from environment variables
MONGO_URI = os.getenv('MONGODB_ATLAS_URI')
DATABASE_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Connect to MongoDB
client = MongoClient(MONGO_URI, appname='devrel.content.python')
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

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

def calculate_distance_time(origin, destination):
    if not origin or not destination:
        return None, None
    try:
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['text']
            duration = result['rows'][0]['elements'][0]['duration']['text']
            return distance, duration
        else:
            return None, None
    except googlemaps.exceptions.ApiError as e:
        st.error(f"Google Maps API error: {e}")
        return None, None

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
location_input = st.text_input("Enter Your Location")
category_input = st.text_input("Enter Category")

# Display filtered products with distance and time
st.header("Filtered Products")
filtered_deals = get_filtered_deals(location_input, category_input)
for deal in filtered_deals:
    st.write(f"Calculating distance and time for: {deal['Location']}")
    distance, duration = calculate_distance_time(location_input, deal['Location'])
    st.write(f"Location: {deal['Location']}")
    st.write(f"Deal: {deal['Deal']}")
    st.write(f"Price: {deal['Price']}")
    st.write(f"Category: {deal['Category']}")
    if distance and duration:
        st.write(f"Distance: {distance}")
        st.write(f"Driving Time: {duration}")
    else:
        st.write("Could not calculate distance and time.")
    st.write("---")

# Display all products
st.header("All Products")
deals = get_all_deals()
for deal in deals:
    st.write(f"Calculating distance and time for: {deal['Location']}")
    distance, duration = calculate_distance_time(location_input, deal['Location'])
    st.write(f"Location: {deal['Location']}")
    st.write(f"Deal: {deal['Deal']}")
    st.write(f"Price: {deal['Price']}")
    st.write(f"Category: {deal['Category']}")
    if distance and duration:
        st.write(f"Distance: {distance}")
        st.write(f"Driving Time: {duration}")
    else:
        st.write("Could not calculate distance and time.")
    st.write("---")