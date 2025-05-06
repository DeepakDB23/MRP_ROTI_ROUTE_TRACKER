# config.py

import streamlit as st
import pandas as pd

# --- Configuration ---
PAGE_TITLE = "🚚Boyz on Wheelz - Tracker™"
PAGE_LAYOUT = "wide"  # Pagelayout is default set to wide

# Initial structure for session state
INITIAL_STATE = {
    'trips': [],
    'current_tab': "Add New Trip",
    # Removed 'Fleet Change' from df_vehicles structure as it moves to trips
    'df_vehicles': pd.DataFrame(columns=['Vehicle', 'License Plate', 'Comments']),
    'logged_in': False,
    # 'confirm_delete': False # Handled dynamically per trip now
    'data_loaded': False,  # Flag to ensure data is loaded only once per session
    # Removed 'add_trip_start_km_value' as auto-population is removed
    # Removed 'previous_add_trip_vehicle' as it's no longer needed for auto-population
}

# Tab titles for navigation
TAB_TITLES = ["Add New Trip", "Edit Existing Trip", "View Records"]

# List of available vehicles
VEHICLE_OPTIONS = ["", "A", "B", "C"]  # Added empty string for default

# List of available drivers
DRIVER_OPTIONS = ["", "Georgekutty", "Cliffy", "Adwaith", "Aliyas",
                  "Tijo", "Deepak"]  # Change: Removed Akhil from driver's list

# Store region mapping (Added 5 new locations)
STORE_REGION_MAPPING = {
    # Added Pickering, Whitby
    "East": ["Woodside", "Kennedy Commons", "Scarborough", "Ajax", "Oshawa"],
    # Added Brampton to the West route
    "West": ["Jane", "Stockyard", "Bloor", "Stoney Creek", "Burlington", "Oakville", "Niagara", "Dundas", "Waterloo", "Woodstock", "London", "Brampton"],
    "North": ["Vaughan", "Bradford", "NewMarket"],
    "Downtown": ["King", "Momo-King", "Queen", "Harbour", "Harlow", "Maverick", "Momo-Downtown", "Bayview", "Uptown", "Leslie"],
    "Chai Stop": ["Lakeshore - CS", "Harbourfront - CS"],
    # changed the name from other to Central
    "Central": ["Veggie Paradise", "Rexdale"],
    # Added Rexdale list
    "Missisauga": ["Dixie", "Mississauga", "Square One", "Hakka Mississauga"]
}

# Google Sheets Configuration
# You need to set these in Streamlit Secrets
# [gsheets]
# spreadsheet_name = "Your RotiRoute Tracker Sheet Name"
# trips_worksheet_name = "Full_route"
# vehicles_worksheet_name = "Vehicle plates"
# credentials = "{...}" # The JSON content of your service account key file
GSHEETS_SPREADSHEET_NAME = st.secrets.get(
    "gsheets", {}).get("spreadsheet_name")
GSHEETS_TRIPS_WORKSHEET_NAME = st.secrets.get("gsheets", {}).get(
    "trips_worksheet_name", "Full_route")  # Default
GSHEETS_VEHICLES_WORKSHEET_NAME = st.secrets.get("gsheets", {}).get(
    "vehicles_worksheet_name", "Vehicle plates")  # Default
GSHEETS_CREDENTIALS = st.secrets.get("gsheets", {}).get("credentials")

# Define the columns expected in the Google Sheet for Trips
# Ensure these match the keys used in the trip dictionaries
GSHEETS_TRIPS_COLUMNS = [
    "id", "Date", "Vehicle", "Start KM", "End KM", "Accumulated KM",
    "Driver", "Route", "Remarks", "Edited By", "Fleet Change", "License Plate at Trip Time"
]

# Define the columns expected in the Google Sheet for Vehicle Plates
# Removed 'Fleet Change' from here
GSHEETS_VEHICLES_COLUMNS = [
    "Vehicle", "License Plate", "Comments"
]
