# utils.py

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from config import STORE_REGION_MAPPING, DRIVER_OPTIONS  # Import from config

# Function to initialize session state with necessary data structures


def initialize_state():
    """Initializes session state variables if they don't exist."""
    from config import INITIAL_STATE  # Import here to avoid circular dependency if config imports utils
    for key, value in INITIAL_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

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

# Function to add a new trip


def add_trip(date, vehicle, start_km, end_km, driver, route_list, remarks):
    """Adds a new trip record to the session state."""
    # Basic validation
    if end_km < start_km:
        st.error("Error: End KM must be greater than or equal to Start KM.")
        return False

    accumulated_km = end_km - start_km
    # Convert list of stores to a comma-separated string
    route_string = ", ".join(route_list)

    # Get current license plate for the vehicle at the time of trip creation
    current_plate = "N/A"
    vehicle_row = st.session_state.df_vehicles[st.session_state.df_vehicles['Vehicle'] == vehicle]
    if not vehicle_row.empty:
        plate_val = vehicle_row['License Plate'].iloc[0]
        current_plate = plate_val if plate_val and pd.notna(
            plate_val) else "N/A"

    new_trip = {
        "id": str(uuid.uuid4()),  # Generate a unique ID
        "Date": date.strftime('%Y-%m-%d'),  # Format date as string
        "Vehicle": vehicle,
        "Start KM": start_km,
        "End KM": end_km,
        "Accumulated KM": accumulated_km,
        "Driver": driver,
        "Route": route_string,
        "Remarks": remarks,
        "Edited By": "",  # New field, populated on edit by admin
        # New field, populated on edit by admin (e.g., license plate change note)
        "Fleet Change": "",
        "License Plate at Trip Time": current_plate  # Store plate at time of trip entry
    }
    st.session_state.trips.append(new_trip)
    st.success(
        f"Trip added successfully for Vehicle {vehicle} on {date.strftime('%Y-%m-%d')}!")
    return True

# Function to update an existing trip


def update_trip(trip_id, date, vehicle, start_km, end_km, driver, route_list, remarks, edited_by, fleet_change):
    """Updates an existing trip record in the session state."""
    # Basic validation
    if end_km < start_km:
        st.error("Error: End KM must be greater than or equal to Start KM.")
        return False

    accumulated_km = end_km - start_km
    # Convert list of stores to a comma-separated string
    route_string = ", ".join(route_list)

    # Find the trip by ID and update
    for trip in st.session_state.trips:
        if trip["id"] == trip_id:
            trip["Date"] = date.strftime('%Y-%m-%d')  # Format date as string
            trip["Vehicle"] = vehicle
            trip["Start KM"] = start_km
            trip["End KM"] = end_km
            trip["Accumulated KM"] = accumulated_km
            trip["Driver"] = driver
            trip["Route"] = route_string
            trip["Remarks"] = remarks
            trip["Edited By"] = edited_by
            trip["Fleet Change"] = fleet_change
            # Note: License Plate at Trip Time is not updated here, it reflects the plate when the trip was *added*
            st.success("Trip updated successfully!")
            return True
    st.error("Error: Could not find trip to update.")
    return False

# Function to delete a trip


def delete_trip(trip_id):
    """Deletes a trip record from the session state."""
    # Filter out the trip to be deleted
    st.session_state.trips = [
        trip for trip in st.session_state.trips if trip["id"] != trip_id]
    st.success("Trip deleted successfully!")

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
