import streamlit as st
from pymongo import MongoClient
import pandas as pd
import os
import math
from datetime import datetime
import openai
import json

# MongoDB connection details
MONGO_URI = os.getenv("MONGODB_ATLAS_URI")
DATABASE_NAME = "sample_airbnb"
COLLECTION_NAME = "rentals"

openai.api_key = os.getenv("OPENAI_API_KEY")


def create_ai_review_summary(listing_id,reviews):
    response = openai.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": """Generate a summary of the reviews below. JSON output only include fields like 'summary', 'negative_tags', 'neutral_tags', 'positive_tags'."""},
            {"role": "user", "content": f"Use those: {reviews}"}
        ],
        temperature=0,
        response_format={"type" : "json_object"}
    )

    json_response = json.loads(response.choices[0].message.content)

    collection.update_one({"_id" : int(listing_id)}, {"$set": {"ai_summary": json_response}})
    return json_response

    

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


def save_reviews(listing_id, new_review):
    collection.update_one({"_id": int(listing_id)}, {"$push": {"reviews": new_review}})
    return True



# Streamlit UI
st.title("🏡 Airbnb Listings Viewer")


# Load data from MongoDB
@st.cache_data
def load_data():

    data = list(collection.find({}, {"text_embedding" : 0, "image_embedding" : 0}))
    return pd.DataFrame(data)

global data
data = load_data()

# Display data in Streamlit
expander_data = st.expander("View Data")
expander_data.dataframe(data)

# Sidebar filters
st.sidebar.title("Filters")
min_price = st.sidebar.slider("Minimum Price", min_value=int(data["price"].min()), max_value=int(data["price"].max()), value=int(data["price"].min()))
max_price = st.sidebar.slider("Maximum Price", min_value=int(data["price"].min()), max_value=int(data["price"].max()), value=int(data["price"].max()))
room_type = st.sidebar.multiselect("Room Type", options=data["room_type"].unique(), default=data["room_type"].unique())
property_type = st.sidebar.multiselect("Property Type", options=data["property_type"].unique(), default=data["property_type"].unique())

# Filter data based on user input
filtered_data = data[(data["price"] >= min_price) & (data["price"] <= max_price)]
if room_type:
    filtered_data = filtered_data[filtered_data["room_type"].isin(room_type)]
if property_type:
    filtered_data = filtered_data[filtered_data["property_type"].isin(property_type)]

# Display filtered data
st.dataframe(filtered_data)
st.title("Listing Details")
selected_listing = st.selectbox("Select a Listing", options=filtered_data["name"])


# Show details of a selected listing

@st.experimental_dialog("Add Review",width="large")
def add_review(listing_id):
    new_review_text = st.text_input("Enter your review")
    if st.button("Submit"):
        new_review = {
            "_id" : str(math.ceil(len(reviews) + 1)),
            "comments": new_review_text,
            "date": datetime.now(),
            "reviewer_name" : "Anonymous"

        }
        save_reviews(listing_id, new_review)
        st.rerun()
        
        
        
        

if selected_listing:
    listing_details = collection.find_one({"name": selected_listing})
    
    st.subheader("Listing Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Name:** {listing_details['name']}")
        st.markdown(f"**Description:** {listing_details['description']}")
        st.markdown(f"**Price:** ${listing_details['price']} per night")
        st.markdown(f"**Property Type:** {listing_details['property_type']}")
        st.markdown(f"**Room Type:** {listing_details['room_type']}")
        st.markdown(f"**Accommodates:** {listing_details['accommodates']} guests")
        st.markdown(f"**Bedrooms:** {listing_details['bedrooms']}")
        st.markdown(f"**Beds:** {listing_details['beds']}")
        st.markdown(f"**Bathrooms:** {listing_details['bathrooms']}")
    
    with col2:
        st.markdown(f"**Number of Reviews:** {listing_details['number_of_reviews']}")
        st.markdown(f"**Review Scores:** {listing_details['review_scores']}")
        st.markdown(f"**Address:** {listing_details['address']}")
        st.markdown(f"**Amenities:** {', '.join(listing_details['amenities'])}")
        st.markdown(f"**Listing URL:** [Link]({listing_details['listing_url']})")
        
        if "images" in listing_details and listing_details["images"]:
            st.subheader("Images")
            st.image(listing_details["images"]['picture_url'])
    st.subheader("Reviews")
    
    if "reviews" in listing_details and listing_details["reviews"]:
        # reverse the reviews to show the latest review first
        reviews = listing_details["reviews"][::-1]
        if not "ai_summary" in listing_details:
            if st.button("Refresh AI Summary"):
                with st.spinner("Generating AI summary"):
                    ai_summary  = create_ai_review_summary(listing_details["_id"],reviews)
                    # adjust card for AI summary recieving {'summary' : ... , negative_tags  : [], neutral_tags : [], positive_tags : []}
                if ai_summary:
                    ai_expander = st.expander(f"**AI Summary** : {ai_summary['summary']}")
                    if ai_summary['negative_tags']:
                        ai_expander.markdown(f"**Negative Tags:** {', '.join(ai_summary['negative_tags'])}")
                    if ai_summary['neutral_tags']:
                        ai_expander.markdown(f"**Neutral Tags:** {', '.join(ai_summary['neutral_tags'])}")
                    if ai_summary['positive_tags']:
                        ai_expander.markdown(f"**Positive Tags:** {', '.join(ai_summary['positive_tags'])}")
        else:
            ai_summary = listing_details["ai_summary"]
            ai_expander = st.expander(f"**AI Summary** : {ai_summary['summary']}")
            if ai_summary['negative_tags']:
                ai_expander.markdown(f"**Negative Tags:** {', '.join(ai_summary['negative_tags'])}")
            if ai_summary['neutral_tags']:
                ai_expander.markdown(f"**Neutral Tags:** {', '.join(ai_summary['neutral_tags'])}")
            if ai_summary['positive_tags']:
                ai_expander.markdown(f"**Positive Tags:** {', '.join(ai_summary['positive_tags'])}")
        reviews_per_page = 10
        total_pages = math.ceil(len(reviews) / reviews_per_page)

        
        

        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        with st.expander(f"Reviews (Page {page}/{total_pages})", expanded=True):
            
            start_idx = (page - 1) * reviews_per_page
            end_idx = start_idx + reviews_per_page

            
            for review in reviews[start_idx:end_idx]:
                st.write(f"**Comments:** {review['comments']}")
                st.write("---")

            if st.button("Add Review"):
                new_review = add_review(listing_details["_id"])
                st.cache_data.clear()
                reviews.append(new_review)
               
    else:
        reviews = []
        st.write("No reviews found for this listing")
        if st.button("Add Review"):
            new_review = add_review(listing_details["_id"])
            # refresh chached data
            st.cache_data.clear()
            reviews.append(new_review)
            ai_summary  = create_ai_review_summary(reviews)
                

# Close MongoDB connection
#client.close()
