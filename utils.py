# utils.py

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json  # To parse the credentials string

from config import (
    STORE_REGION_MAPPING, DRIVER_OPTIONS,
    GSHEETS_SPREADSHEET_NAME, GSHEETS_TRIPS_WORKSHEET_NAME,
    GSHEETS_VEHICLES_WORKSHEET_NAME, GSHEETS_CREDENTIALS,
    GSHEETS_TRIPS_COLUMNS, GSHEETS_VEHICLES_COLUMNS, INITIAL_STATE
)

# --- Google Sheets Integration ---


@st.cache_resource(ttl=3600)  # Cache the client for an hour
def get_gsheets_client():
    """Authenticates and returns a gspread client."""
    if GSHEETS_CREDENTIALS is None:
        st.error("Google Sheets credentials not found in Streamlit Secrets.")
        st.stop()  # Stop the app if credentials is missing

    try:
        # Parse the JSON credentials string
        credentials_info = json.loads(GSHEETS_CREDENTIALS)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(
            credentials_info, scopes=scopes)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Error authenticating with Google Sheets: {e}")
        st.stop()  # Stop the app on authentication failure


@st.cache_resource(ttl=3600)  # Cache the spreadsheet object for an hour
def get_spreadsheet():
    """Returns the Google Spreadsheet object."""
    client = get_gsheets_client()
    try:
        spreadsheet = client.open(GSHEETS_SPREADSHEET_NAME)
        return spreadsheet
    except Exception as e:
        st.error(
            f"Error opening Google Spreadsheet '{GSHEETS_SPREADSHEET_NAME}': {e}")
        st.stop()


def get_worksheet(worksheet_name):
    """Returns a specific worksheet object within the spreadsheet."""
    spreadsheet = get_spreadsheet()
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet
    except Exception as e:
        st.error(f"Error opening Google Worksheet '{worksheet_name}': {e}")
        st.stop()


def load_trips_from_gsheets():
    """Loads trip data from the Google Sheet (Full_route) into session state."""
    worksheet = get_worksheet(GSHEETS_TRIPS_WORKSHEET_NAME)
    try:
        # Get all records as a list of dictionaries
        records = worksheet.get_all_records()
        # Convert to DataFrame for easier handling, then back to list of dicts
        df = pd.DataFrame(records)

        # Ensure all expected columns are present, add if missing
        for col in GSHEETS_TRIPS_COLUMNS:
            if col not in df.columns:
                df[col] = None  # Add missing column with None values

        # Convert DataFrame back to list of dictionaries
        # Use .where(pd.notna, None) to replace NaN with None for cleaner dicts
        trips_list = df.where(pd.notna(df), None).to_dict('records')

        # Ensure each trip has a unique ID if loading older data without IDs
        for trip in trips_list:
            if trip.get('id') is None or trip.get('id') == '':
                # Generate a unique ID if missing
                trip['id'] = str(uuid.uuid4())

        st.session_state.trips = trips_list
        st.success(
            f"Trip data loaded from '{GSHEETS_TRIPS_WORKSHEET_NAME}' sheet.")
    except Exception as e:
        st.error(
            f"Error loading data from '{GSHEETS_TRIPS_WORKSHEET_NAME}' sheet: {e}")
        st.session_state.trips = []  # Initialize as empty list on error


def save_trips_to_gsheets():
    """Saves the current trip data from session state back to the Google Sheet (Full_route)."""
    worksheet = get_worksheet(GSHEETS_TRIPS_WORKSHEET_NAME)
    try:
        if not st.session_state.trips:
            # Clear the sheet if there are no trips
            worksheet.clear()
            # Write headers back
            worksheet.append_row(GSHEETS_TRIPS_COLUMNS)
        else:
            # Create a DataFrame from the current trips list
            df = pd.DataFrame(st.session_state.trips)

            # Ensure columns are in the correct order and all expected columns are present
            for col in GSHEETS_TRIPS_COLUMNS:
                if col not in df.columns:
                    df[col] = None  # Add missing column with None

            # Reorder columns
            df = df[GSHEETS_TRIPS_COLUMNS]

            # Convert DataFrame to a list of lists (including header) for gspread
            data_to_save = [df.columns.tolist()] + df.values.tolist()

            # Clear existing data and write the new data
            worksheet.clear()
            worksheet.append_rows(data_to_save)

        st.success(
            f"Trip data saved to '{GSHEETS_TRIPS_WORKSHEET_NAME}' sheet.")
    except Exception as e:
        st.error(
            f"Error saving data to '{GSHEETS_TRIPS_WORKSHEET_NAME}' sheet: {e}")


def load_vehicle_plates_from_gsheets():
    """Loads vehicle plate data from the Google Sheet (Vehicle plates) into session state."""
    worksheet = get_worksheet(GSHEETS_VEHICLES_WORKSHEET_NAME)
    try:
        # Get all records as a list of dictionaries
        records = worksheet.get_all_records()
        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Ensure all expected columns are present, add if missing
        for col in GSHEETS_VEHICLES_COLUMNS:
            if col not in df.columns:
                df[col] = None  # Add missing column with None values

         # Convert DataFrame back to list of dictionaries
        # Use .where(pd.notna, None) to replace NaN with None for cleaner dicts
        vehicle_plates_list = df.where(pd.notna(df), None).to_dict('records')

        # Store as DataFrame in session state for easier lookup in admin section
        st.session_state.df_vehicles = pd.DataFrame(vehicle_plates_list)
        st.success(
            f"Vehicle plate data loaded from '{GSHEETS_VEHICLES_WORKSHEET_NAME}' sheet.")
    except Exception as e:
        st.error(
            f"Error loading data from '{GSHEETS_VEHICLES_WORKSHEET_NAME}' sheet: {e}")
        st.session_state.df_vehicles = pd.DataFrame(
            columns=GSHEETS_VEHICLES_COLUMNS)  # Initialize empty DataFrame on error


def save_vehicle_plates_to_gsheets():
    """Saves the current vehicle plate data from session state back to the Google Sheet (Vehicle plates)."""
    worksheet = get_worksheet(GSHEETS_VEHICLES_WORKSHEET_NAME)
    try:
        df = st.session_state.df_vehicles.copy()

        # Ensure columns are in the correct order and all expected columns are present
        for col in GSHEETS_VEHICLES_COLUMNS:
            if col not in df.columns:
                df[col] = None  # Add missing column with None

        # Reorder columns
        df = df[GSHEETS_VEHICLES_COLUMNS]

        # Convert DataFrame to a list of lists (including header) for gspread
        data_to_save = [df.columns.tolist()] + df.values.tolist()

        # Clear existing data and write the new data
        worksheet.clear()
        worksheet.append_rows(data_to_save)

        st.success(
            f"Vehicle plate data saved to '{GSHEETS_VEHICLES_WORKSHEET_NAME}' sheet.")
    except Exception as e:
        st.error(
            f"Error saving data to '{GSHEETS_VEHICLES_WORKSHEET_NAME}' sheet: {e}")


# --- Helper Functions (Modified to call save_trips_to_gsheets) ---

# Function to initialize session state and load data
def initialize_state():
    """Initializes session state variables and loads data from Google Sheets."""
    # Initialize basic state variables first
    for key, value in INITIAL_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Load data from Google Sheets when the app initializes for the first time in a session
    if not st.session_state.get('data_loaded', False):
        load_trips_from_gsheets()
        load_vehicle_plates_from_gsheets()
        st.session_state.data_loaded = True  # Set flag


# Function to get store region mapping
def get_store_region_mapping():
    """Returns the dictionary mapping regions to stores. Used for reference."""
    return STORE_REGION_MAPPING

# List of drivers


def get_drivers_list():
    """Returns the list of available drivers."""
    return DRIVER_OPTIONS

# Function to get all stores


def get_all_stores():
    """Returns a sorted list of all stores from the mapping."""
    all_stores = [store for region_stores in STORE_REGION_MAPPING.values()
                  for store in region_stores]
    all_stores.sort()
    return all_stores

# --- Helper Function: Recalculate Accumulated KM for a Vehicle ---


def recalculate_accumulated_km(vehicle):
    """Recalculates the Accumulated KM for all trips of a vehicle in chronological order."""
    trips = [trip for trip in st.session_state.trips if trip.get(
        "Vehicle") == vehicle]
    if not trips:
        return

    # Sort trips by date
    trips_sorted = sorted(
        trips,
        key=lambda x: datetime.strptime(x["Date"], '%Y-%m-%d')
    )

    total_km = 0

    # Recalculate and update each trip's Accumulated KM
    for trip in trips_sorted:
        start_km = trip.get("Start KM", 0)
        end_km = trip.get("End KM", 0)
        delta = end_km - start_km
        total_km += delta
        trip["Accumulated KM"] = total_km

    save_trips_to_gsheets()  # Save updated trips to Google Sheets
# --- Add New Trip Function ---


def add_trip(date, vehicle, start_km, end_km, driver, route_list, remarks):
    """Adds a new trip record and recalculates accumulated KM for the vehicle."""
    if end_km < start_km:
        st.error("Error: End KM must be greater than or equal to Start KM.")
        return False

    route_string = ", ".join(route_list)

    current_plate = "N/A"
    if not st.session_state.df_vehicles.empty:
        vehicle_row = st.session_state.df_vehicles[st.session_state.df_vehicles['Vehicle'] == vehicle]
        if not vehicle_row.empty:
            plate_val = vehicle_row.get('License Plate', None)
            current_plate = plate_val.iloc[0] if plate_val is not None and not plate_val.empty and pd.notna(
                plate_val.iloc[0]) else "N/A"

    new_trip = {
        "id": str(uuid.uuid4()),  # Unique ID
        "Date": date.strftime('%Y-%m-%d'),
        "Vehicle": vehicle,
        "Start KM": start_km,
        "End KM": end_km,
        "Accumulated KM": 0,  # Will be set by recalculate_accumulated_km
        "Driver": driver,
        "Route": route_string,
        "Remarks": remarks,
        "Edited By": "",
        "Fleet Change": "",
        "License Plate at Trip Time": current_plate
    }

    st.session_state.trips.append(new_trip)
    # Recalculate all trips for this vehicle
    recalculate_accumulated_km(vehicle)

    st.success(
        f"Trip added successfully for Vehicle {vehicle} on {date.strftime('%Y-%m-%d')}!")
    return True

# --- Update Existing Trip Function ---


def update_trip(trip_id, date, vehicle, start_km, end_km, driver, route_list, remarks, edited_by, fleet_change):
    """Updates an existing trip and recalculates accumulated KM for the vehicle."""
    if end_km < start_km:
        st.error("Error: End KM must be greater than or equal to Start KM.")
        return False

    route_string = ", ".join(route_list)

    for trip in st.session_state.trips:
        if trip["id"] == trip_id:
            trip.update({
                "Date": date.strftime('%Y-%m-%d'),
                "Vehicle": vehicle,
                "Start KM": start_km,
                "End KM": end_km,
                "Accumulated KM": 0,
                "Driver": driver,
                "Route": route_string,
                "Remarks": remarks,
                "Edited By": edited_by,
                "Fleet Change": fleet_change
            })
            break

    # Recalculate all trips for this vehicle
    recalculate_accumulated_km(vehicle)
    st.success("Trip updated successfully!")
    return True

# --- Delete Trip Function ---


def delete_trip(trip_id):
    """Deletes a trip and recalculates accumulated KM for the associated vehicle."""
    trip_to_delete = next(
        (trip for trip in st.session_state.trips if trip["id"] == trip_id), None)

    if trip_to_delete:
        vehicle = trip_to_delete["Vehicle"]
        st.session_state.trips = [
            t for t in st.session_state.trips if t["id"] != trip_id]
        recalculate_accumulated_km(vehicle)  # Recalculate after deletion
        st.success("Trip deleted successfully!")
    else:
        st.error("Error: Could not find trip to delete.")

# Function to record a fleet change event as a trip
def record_fleet_change_trip(vehicle, old_plate, new_plate, admin_name):
    """Records a fleet change event as a special trip entry."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fleet_change_note = f"[{timestamp}] Plate changed for {vehicle}: {old_plate} -> {new_plate}"

    new_fleet_change_trip = {
        "id": str(uuid.uuid4()),  # Unique ID for this entry
        "Date": datetime.now().strftime('%Y-%m-%d'),  # Date of the change
        "Vehicle": vehicle,
        "Start KM": 0,  # N/A for this type of entry
        "End KM": 0,   # N/A
        "Accumulated KM": 0,  # N/A
        "Driver": "N/A",  # Or could be the admin's name if desired
        "Route": "Fleet Change Event",  # Indicate this is a fleet change event
        # Put the note in remarks or fleet change
        "Remarks": f"Admin Note: {fleet_change_note}",
        "Edited By": admin_name,  # The admin who made the change
        "Fleet Change": fleet_change_note,  # Put the specific change note here
        "License Plate at Trip Time": new_plate  # Record the new plate
    }
    st.session_state.trips.append(new_fleet_change_trip)
    save_trips_to_gsheets()  # Save the new entry to Google Sheets
    st.info(f"Recorded fleet change event for {vehicle}.")

# Function to count stores from route string
def count_stores_in_route(route_string):
    """Counts the number of stores in a comma-separated route string."""
    if not route_string:
        return 0
    # Simple approach: split by comma and count non-empty parts
    return len([store.strip() for store in route_string.split(',') if store.strip()])

# Function to filter trips by date range and vehicle
def filter_trips(trips, start_date, end_date, vehicle):
    """Filters a list of trips by date range and vehicle."""
    filtered = [
        trip for trip in trips
        if datetime.strptime(trip["Date"], '%Y-%m-%d').date() >= start_date and
        datetime.strptime(trip["Date"], '%Y-%m-%d').date() <= end_date
    ]
    if vehicle != "All":
        filtered = [trip for trip in filtered if trip["Vehicle"] == vehicle]
    return filtered
