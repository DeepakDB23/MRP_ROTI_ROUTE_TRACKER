# tabs/edit_trip_tab.py

import streamlit as st
from datetime import datetime
# Import necessary functions
from utils import get_all_stores, get_drivers_list, update_trip, delete_trip
from config import VEHICLE_OPTIONS  # Import vehicle options


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
        # A more robust way would be to store IDs in the selectbox options, but this works for now
        for trip in st.session_state.trips:
            if f"{trip['Date']} - {trip['Vehicle']} - {trip['Start KM']} to {trip['End KM']}" == selected_trip_display:
                selected_trip = trip
                break

    if selected_trip:
        all_stores = get_all_stores()
        drivers = get_drivers_list()

        with st.form("edit_trip_form"):
            # Use the ID from the selected trip
            edit_trip_id = selected_trip["id"]

            # Populate form with selected trip data
            # Convert date string back to datetime object for date_input
            edit_date = st.date_input("Date:", datetime.strptime(
                selected_trip["Date"], '%Y-%m-%d'))
            # Find the correct index for the selectbox based on the current value
            try:
                # Use vehicle options from config, excluding the empty default for editing
                vehicle_options_clean = [v for v in VEHICLE_OPTIONS if v]
                vehicle_index = vehicle_options_clean.index(
                    selected_trip["Vehicle"])
            except ValueError:
                vehicle_index = 0  # Default to first option if value not found
            edit_vehicle = st.selectbox(
                "Vehicle:", vehicle_options_clean, index=vehicle_index)

            edit_start_km = st.number_input(
                "Start KM:", min_value=0, value=selected_trip["Start KM"], step=1)
            edit_end_km = st.number_input(
                "End KM:", min_value=0, value=selected_trip["End KM"], step=1)

            # Use selectbox for driver, set default to the current driver
            try:
                driver_index = drivers.index(selected_trip["Driver"])
            except ValueError:
                driver_index = 0  # Default to empty string if driver not in list
            edit_driver = st.selectbox(
                "Driver Name:", options=drivers, index=driver_index)

            # Convert route string back to list for multiselect
            current_route_list = [
                store.strip() for store in selected_trip["Route"].split(',') if store.strip()]
            edit_route_list = st.multiselect(
                "Route (Select Stores):", options=all_stores, default=current_route_list)

            edit_remarks = st.text_area(
                "Remarks:", value=selected_trip["Remarks"])

            # Admin fields - only editable if logged in (though visible to all for simplicity here)
            st.subheader("Admin Edit Fields")
            # Use .get for safety in case older entries don't have these keys
            edit_edited_by = st.text_input(
                "Edited By (Admin):", value=selected_trip.get("Edited By", ""))
            edit_fleet_change = st.text_area(
                "Fleet Change (Admin Notes):", value=selected_trip.get("Fleet Change", ""))

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("Save Changes")
            with col2:
                # Streamlit forms require a submit button, so we'll use a regular button outside the form for delete
                pass  # Delete button is handled outside the form below

        if save_button:
            # Check if required fields are filled (Vehicle, Driver, and at least one store in Route)
            if edit_vehicle and edit_driver and edit_route_list:
                update_trip(edit_trip_id, edit_date, edit_vehicle, edit_start_km, edit_end_km,
                            edit_driver, edit_route_list, edit_remarks, edit_edited_by, edit_fleet_change)
                # Reset delete confirmation for this trip
                st.session_state[f'confirm_delete_{edit_trip_id}'] = False
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
                delete_trip(edit_trip_id)
                st.session_state[confirm_state_key] = False  # Reset confirmation
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
