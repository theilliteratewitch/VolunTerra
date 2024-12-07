import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

# Load the dataset
data = pd.read_csv("Dataset.csv")

# Page title
st.title("Welcome to VolunTerra!")
st.text("Explore wildlife sanctuaries and volunteer organizations around the world.")

# Sidebar for filters
st.sidebar.header("Filters")
show_sanctuaries = st.sidebar.checkbox("Wildlife Sanctuaries", value=True)
show_volunteering_centers = st.sidebar.checkbox("Volunteering Centers", value=True)

# Filter the dataset
filtered_data = pd.DataFrame()

if show_sanctuaries:
    filtered_data = pd.concat([filtered_data, data[data["Type"] == "Wildlife Sanctuary"]])
if show_volunteering_centers:
    filtered_data = pd.concat([filtered_data, data[data["Type"] == "Volunteering Center"]])

# Assign colors based on the "Type" column
def assign_color(row):
    if row["Type"] == "Wildlife Sanctuary":
        return [200, 30, 0, 160]  # Red
    elif row["Type"] == "Volunteering Center":
        return [0, 150, 150, 160]  # Blue
    else:
        return [150, 150, 0, 160]  # Yellow

filtered_data["Color"] = filtered_data.apply(assign_color, axis=1)

# Geolocator for region search
geolocator = Nominatim(user_agent="volunterra_app")

# Sidebar for search by region
st.sidebar.subheader("Search by Region")
region_query = st.sidebar.text_input("Enter a country or region:")
zoom_to_region = st.sidebar.button("Search")

# Default view state
view_state = pdk.ViewState(latitude=0, longitude=0, zoom=2, pitch=35)

if zoom_to_region and region_query:
    try:
        location = geolocator.geocode(region_query)
        if location:
            view_state = pdk.ViewState(
                latitude=location.latitude, longitude=location.longitude, zoom=5, pitch=35
            )
        else:
            st.sidebar.error("Region not found. Showing default view.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}. Showing default view.")

# Add a dropdown to select a specific location
st.sidebar.subheader("Select a Location")
if not filtered_data.empty:
    location_names = filtered_data["Name"].tolist()
    selected_location = st.sidebar.selectbox("Choose a location:", ["None"] + location_names)

    # Display details of the selected location
    if selected_location != "None":
        selected_data = filtered_data[filtered_data["Name"] == selected_location].iloc[0]
        st.sidebar.markdown(
            f"*Name:* {selected_data['Name']}  \n"
            f"*Type:* {selected_data['Type']}  \n"
            f"*Latitude:* {selected_data['Latitude']}  \n"
            f"*Longitude:* {selected_data['Longitude']}  \n"
            f"*Description:* {selected_data['Description']}  \n"
        )
    else:
        st.sidebar.write("Select a location to view details.")
else:
    st.sidebar.write("No locations match your filters.")

# Function to create the map
def create_map(data, view_state):
    layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["Longitude", "Latitude"],
        get_radius=200000,  # Adjust size as needed
        get_color="Color",  # Use the color column
        pickable=True,
        auto_highlight=True,
    )

    # Tooltip to display dynamic information when a marker is hovered over
    tooltip = {
        "html": (
            "<b>{Name}</b><br>"
            "Type: {Type}<br>"
            "Latitude: {Latitude}<br>"
            "Longitude: {Longitude}<br>"
            "Description: {Description}"
        ),
        "style": {
            "backgroundColor": "rgba(0, 0, 0, 0.7)",
            "color": "white",
            "padding": "5px",
        },
    }

    # Return the map object
    return pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

# Display the map
if not filtered_data.empty:
    map_obj = create_map(filtered_data, view_state)
    st.pydeck_chart(map_obj)
else:
    st.write("Please pick a category!")