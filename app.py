import os
from dotenv import load_dotenv
from pymongo import MongoClient
import streamlit as st
import googlemaps
import openai

# Load environment variables from .env file
load_dotenv()

# Get MongoDB Atlas URI and other configurations from environment variables
MONGO_URI = os.getenv('MONGODB_ATLAS_URI')
DATABASE_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Connect to MongoDB
client = MongoClient(MONGO_URI, appname='devrel.content.python')
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

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

def generate_summary(location, deal, price, distance, duration):
    # Check if the summary already exists in the database
    existing_deal = collection.find_one({"Location": location, "Deal": deal, "Price": price})
    
    if existing_deal and "Summary" in existing_deal:
        return existing_deal["Summary"]
    
    # Generate a new summary using OpenAI API
    prompt = f"Location: {location}\nDeal: {deal}\nPrice: {price}\nDistance: {distance}\nDriving Time: {duration}\n\nGenerate a summary for this deal."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    summary = response.choices[0].message['content'].strip()
    
    # Update the document with the new summary
    collection.update_one(
        {"Location": location, "Deal": deal, "Price": price},
        {"$set": {"Summary": summary}}
    )
    
    return summary

# Streamlit UI
st.title("🏡 View products")

# Form for saving a deal
with st.form("Save Deal"):
    st.subheader("Enter Deal Details")
    location = st.text_input("Location")
    deal = st.text_input("Deal")
    price = st.text_input("Price")
    category = st.text_input("Category")
    submit_button = st.form_submit_button(label="Submit")
    if submit_button:
        if location and deal and price and category:
            save_deal(location, deal, price, category)
            st.success("Deal saved successfully!")
        else:
            st.error("Please fill in all fields.")

# User input for filtering products
st.header("Filter Products")
location_input = st.text_input("Enter Your Location")
category_input = st.text_input("Enter Category", value="Drinks")

# Display filtered products with distance and time
st.header("Filtered Products")
filtered_deals = get_filtered_deals(location_input, category_input)
for deal in filtered_deals:
    st.write(f"Calculating distance and time for: {deal['Location']}")
    distance, duration = calculate_distance_time(location_input, deal['Location'])
    summary = generate_summary(deal['Location'], deal['Deal'], deal['Price'], distance, duration)
    st.write(f"Location: {deal['Location']}")
    st.write(f"Deal: {deal['Deal']}")
    st.write(f"Price: {deal['Price']}")
    st.write(f"Category: {deal['Category']}")
    st.write(f"Summary: {summary}")
    st.write("---")

# Display all products
st.header("All Products")
deals = get_all_deals()
for deal in deals:
    if category_input and deal['Category'] != category_input:
        continue
    st.write(f"Calculating distance and time for: {deal['Location']}")
    distance, duration = calculate_distance_time(location_input, deal['Location'])
    summary = generate_summary(deal['Location'], deal['Deal'], deal['Price'], distance, duration)
    st.write(f"Location: {deal['Location']}")
    st.write(f"Deal: {deal['Deal']}")
    st.write(f"Price: {deal['Price']}")
    st.write(f"Category: {deal['Category']}")
    st.write(f"Summary: {summary}")
    st.write("---")