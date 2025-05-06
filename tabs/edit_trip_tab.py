# tabs/edit_trip_tab.py

import streamlit as st
import pandas as pd  # Import pandas
from datetime import datetime
# Import necessary functions
from utils import get_drivers_list, update_trip, delete_trip
from config import VEHICLE_OPTIONS, STORE_REGION_MAPPING  # Import from config


def display_edit_trip_tab():
    """Displays the UI and handles logic for the Edit Existing Trip tab."""
    st.header("Edit Existing Trip")

    # Create a list of options for the selectbox
    edit_options = ["-- Select a Trip --"] + [
        f"{trip['Date']} - {trip['Vehicle']} - {trip['Start KM']} to {trip['End KM']}"
        for trip in st.session_state.trips
    ]
    # Use a unique key for the selectbox
    selected_trip_display = st.selectbox(
        "Select Trip to Edit:", edit_options, key="edit_trip_select")

    # Find the selected trip object
    selected_trip = None
    if selected_trip_display != "-- Select a Trip --":
        # Find the trip based on the display string (this assumes display strings are unique enough)
        for trip in st.session_state.trips:
            if f"{trip['Date']} - {trip['Vehicle']} - {trip['Start KM']} to {trip['End KM']}" == selected_trip_display:
                selected_trip = trip
                break  # Found the latest trip for this vehicle

    if selected_trip:
        store_mapping = STORE_REGION_MAPPING
        drivers = get_drivers_list()  # Get the list of drivers

        with st.form("edit_trip_form"):
            # Use the ID from the selected trip
            edit_trip_id = selected_trip["id"]

            # Populate form with selected trip data
            # Convert date string back to datetime object for date_input
            edit_date = st.date_input("Date:", datetime.strptime(
                selected_trip["Date"], '%Y-%m-%d'), key=f"edit_date_input_{edit_trip_id}")  # Added key
            # Find the correct index for the selectbox based on the current value
            try:
                # Use vehicle options from config, excluding the empty default for editing
                vehicle_options_clean = [v for v in VEHICLE_OPTIONS if v]
                vehicle_index = vehicle_options_clean.index(
                    selected_trip["Vehicle"])
            except ValueError:
                vehicle_index = 0  # Default to first option if value not found
            edit_vehicle = st.selectbox("Vehicle:", vehicle_options_clean, index=vehicle_index,
                                        key=f"edit_vehicle_select_{edit_trip_id}")  # Added key

            # --- Ensure Start KM and End KM are read correctly ---
            edit_start_km_input = st.number_input(
                "Start KM:", min_value=0, value=selected_trip["Start KM"], step=1, key=f"edit_start_km_input_{edit_trip_id}")  # Added key
            edit_end_km_input = st.number_input(
                "End KM:", min_value=0, value=selected_trip["End KM"], step=1, key=f"edit_end_km_input_{edit_trip_id}")  # Added key
            # --- End Ensure Start KM and End KM are read correctly ---

            # Use selectbox for driver, set default to the current driver
            try:
                driver_index = drivers.index(selected_trip["Driver"])
            except ValueError:
                driver_index = 0  # Default to empty string if driver not in list
            edit_driver = st.selectbox("Driver Name:", options=drivers, index=driver_index,
                                       key=f"edit_driver_select_{edit_trip_id}")  # Added key

            # --- Regional Store Selection for Edit ---
            st.subheader("Route (Select Stores by Region)")
            selected_stores = []
            # Convert route string back to list of currently selected stores
            current_route_list = [
                store.strip() for store in selected_trip["Route"].split(',') if store.strip()]

            # Iterate through regions and their stores to create multiselects per region
            for region, stores in store_mapping.items():
                # Sort stores within each region alphabetically
                stores.sort()
                # Determine which stores in this region are currently selected for the trip
                default_selection = [
                    store for store in stores if store in current_route_list]
                # Use a unique key for each regional multiselect based on trip ID and region
                selected_region_stores = st.multiselect(
                    f"{region}:", options=stores, default=default_selection, key=f"edit_route_select_{edit_trip_id}_{region}")
                # Add selected stores from this region to the main list
                selected_stores.extend(selected_region_stores)

            # The 'edit_route_list' variable for update_trip function will be 'selected_stores'
            edit_route_list = selected_stores
            # --- End of Regional Store Selection for Edit ---

            edit_remarks = st.text_area(
                "Remarks:", value=selected_trip["Remarks"], key=f"edit_remarks_input_{edit_trip_id}")  # Added key

            # Admin fields - only editable if logged in (though visible to all for simplicity here)
            st.subheader("Admin Edit Fields")

            # --- Edited By (Admin) Selectbox ---
            # Use selectbox for Edited By, pre-populated with drivers
            try:
                # Add an empty string option to the beginning of the drivers list
                # Ensure no duplicate empty string
                edited_by_options = [""] + [d for d in drivers if d != ""]
                # Find the index of the current 'Edited By' value in the options
                edited_by_index = edited_by_options.index(
                    selected_trip.get("Edited By", ""))
            except ValueError:
                edited_by_index = 0  # Default to empty string if current value not in list

            edit_edited_by = st.selectbox("Edited By (Admin):", options=edited_by_options,
                                          index=edited_by_index, key=f"edit_edited_by_select_{edit_trip_id}")  # Added key
            # --- End of Edited By Selectbox ---

            # Use .get for safety in case older entries don't have these keys
            edit_fleet_change = st.text_area("Fleet Change (Admin Notes):", value=selected_trip.get(
                "Fleet Change", ""), key=f"edit_fleet_change_input_{edit_trip_id}")  # Added key

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("Save Changes")
            with col2:
                # Streamlit forms require a submit button, so we'll use a regular button outside the form for delete
                pass  # Delete button is handled outside the form below

        if save_button:
            # --- Safely read and cast KM values from input widgets ---
            try:
                 start_km_value = int(edit_start_km_input)
                 end_km_value = int(edit_end_km_input)
            except (ValueError, TypeError):
                st.error("Please enter valid numbers for Start KM and End KM.")
                st.stop()  # Stop execution if KM values are invalid
             # --- End Safely read and cast KM values ---

             # Check if required fields are filled (Vehicle, Driver, and at least one store in Route)
            if edit_vehicle and edit_driver and edit_route_list:
                # update_trip now handles saving to GSheets internally
                update_trip(edit_trip_id, edit_date, edit_vehicle, start_km_value, end_km_value,
                            edit_driver, edit_route_list, edit_remarks, edit_edited_by, edit_fleet_change)
                # Reset delete confirmation for this trip
                if f'confirm_delete_{edit_trip_id}' in st.session_state:
                    del st.session_state[f'confirm_delete_{edit_trip_id}']
                st.rerun()  # Rerun to update the display and reset form
            else:
                 st.error(
                     "Please fill in all required fields (Vehicle, Driver Name, and select at least one Store for Route).")

        # Delete button outside the form
        # Use a unique key for the delete button based on the selected trip ID
        # Check if the confirmation state exists and is True for THIS trip
        confirm_state_key = f'confirm_delete_{selected_trip["id"]}'
        if st.button("Delete Trip", key=f"delete_btn_{selected_trip['id']}"):
            if st.session_state.get(confirm_state_key, False):
                # delete_trip now handles saving to GSheets internally
                delete_trip(edit_trip_id)
                if confirm_state_key in st.session_state:
                    del st.session_state[confirm_state_key]  # Reset confirmation
                st.rerun()  # Rerun to update the selectbox
            else:
                st.warning("Click 'Delete Trip' again to confirm.")
                st.session_state[confirm_state_key] = True  # Set confirmation
                 # Need to rerun to show the warning message immediately
                st.rerun()

    else:
        st.info("Select a trip from the dropdown to edit.")
        # Reset all delete confirmations when no trip is selected
        for key in list(st.session_state.keys()):
            if key.startswith('confirm_delete_'):
                del st.session_state[key]
