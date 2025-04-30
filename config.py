# config.py

import streamlit as st
import pandas as pd

# --- Configuration ---
PAGE_TITLE = "🚚Boyz on Wheelz - Tracker™"


# Initial structure for session state
INITIAL_STATE = {
    'trips': [],
    'current_tab': "Add New Trip",
    'df_vehicles': pd.DataFrame(columns=['Vehicle', 'License Plate']),
    'logged_in': False,
    # 'confirm_delete': False # Handled dynamically per trip now
}

# Tab titles for navigation
TAB_TITLES = ["Add New Trip", "Edit Existing Trip", "View Records"]

# List of available vehicles
VEHICLE_OPTIONS = ["", "A", "B", "C"]  # Added empty string for default

# List of available drivers
DRIVER_OPTIONS = ["", "Georgekutty", "Cliffy", "Adwaith", "Aliyas",
                  "Tijo", "Deepak", "Akhil"]  # Added empty string for default

# Store region mapping
STORE_REGION_MAPPING = {
    "East": ["Woodside", "Kennedy Commons", "Scarborough", "Ajax", "Oshawa"],
    "West": ["Jane", "Stockyard", "Bloor", "Stoney Creek", "Burlington", "Oakville", "Niagara", "Dundas", "Waterloo", "Woodstock", "London"],
    "North": ["Vaughan", "Bradford", "NewMarket"],
    "Downtown": ["King", "Momo-King", "Queen", "Harbour", "Harlow", "Maverick", "Momo-Downtown", "Bayview", "Uptown", "Leslie"],
    "Chai Stop": ["Lakeshore - CS", "Harbourfront - CS"],
    "Others": ["Veggie Paradise", "Rexdale"]
}
