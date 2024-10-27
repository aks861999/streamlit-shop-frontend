import streamlit as st
import aiohttp
import asyncio
import pandas as pd
import requests

# Function to fetch data from Flask backend
def fetch_sweater_data():
    url = "http://127.0.0.1:5000/sweaters"  # Flask endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Failed to fetch data")
        return pd.DataFrame()

# Convert Google Drive link to direct image link
def convert_drive_link(drive_link):
    if 'drive.google.com' in drive_link:
        file_id = drive_link.split('id=')[-1]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return drive_link

# Asynchronous function to fetch image content from URL
async def fetch_image(session, url):
    async with session.get(url) as response:
        return await response.read()  # Return image content as bytes

# Asynchronous function to fetch all images concurrently and cache the result
async def fetch_images_concurrently(image_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url) for url in image_urls]
        return await asyncio.gather(*tasks)

# Streamlit UI
st.title("Sweater List")

# Show a waiting screen while fetching data
with st.spinner('Welcome to Biswas Garments, Please wait sometime, we are fetching the data...'):
    # Fetch sweater data without caching
    df = fetch_sweater_data()

# Check if the DataFrame is empty
if df.empty:
    st.write("No data available.")
else:
    # Convert image URLs
    df['Sweater Photo'] = df['Sweater Photo'].apply(convert_drive_link)

    # Async function call to fetch images once
    @st.cache_resource(show_spinner=False)
    def fetch_images(image_urls):
        return asyncio.run(fetch_images_concurrently(image_urls))

    # Fetch images asynchronously once
    image_urls = df['Sweater Photo'].tolist()
    
    with st.spinner('Welcome to Biswas Garments, Please wait sometime, we are fetching the data...'):
        image_contents = fetch_images(image_urls)

    # Store images in a dictionary for easier access based on filtering
    image_dict = {url: image for url, image in zip(image_urls, image_contents)}

    # Filter options
    sizes = ['All'] + df['Sweater Size'].unique().tolist()
    selected_size = st.selectbox("Select Size", sizes)

    # Apply filtering without refetching images
    filtered_df = df if selected_size == 'All' else df[df['Sweater Size'] == selected_size]

    # Display filtered images without reloading cached images
    for index, row in filtered_df.iterrows():
        st.image(image_dict[row['Sweater Photo']])  # Use the cached image from the dictionary
        st.write(f"Size: {row['Sweater Size']}")
        st.write(f"Price: {row['Price']}")
