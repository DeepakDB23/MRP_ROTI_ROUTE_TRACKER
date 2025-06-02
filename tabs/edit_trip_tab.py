import streamlit as st
import pandas as pd
from datetime import datetime
from utils import get_drivers_list, update_trip, delete_trip
from config import VEHICLE_OPTIONS, STORE_REGION_MAPPING


def display_edit_trip_tab():
    st.header("Edit Existing Trip")

    # Sort trips by date in descending order (latest first)
    sorted_trips = sorted(st.session_state.trips,
                          key=lambda x: datetime.strptime(
                              x['Date'], '%Y-%m-%d'),
                          reverse=True)

    # Create options list for selectbox
    edit_options = ["-- Select a Trip --"] + [
        f"{trip['Date']} - {trip['Vehicle']} - {trip['Start KM']} to {trip['End KM']}"
        for trip in sorted_trips
    ]

    selected_trip_display = st.selectbox(
        "Select Trip to Edit:", edit_options, key="edit_trip_select")

    # Find selected trip object
    selected_trip = None
    if selected_trip_display != "-- Select a Trip --":
        for trip in sorted_trips:
            if f"{trip['Date']} - {trip['Vehicle']} - {trip['Start KM']} to {trip['End KM']}" == selected_trip_display:
                selected_trip = trip
                break

    if selected_trip:
        store_mapping = STORE_REGION_MAPPING
        drivers = get_drivers_list()

        # Create two columns - form and delete button
        form_col, delete_col = st.columns([3, 1])

        with form_col:
            with st.form("edit_trip_form"):
                edit_trip_id = selected_trip["id"]

                # Date input
                edit_date = st.date_input("Date:",
                                          datetime.strptime(
                                              selected_trip["Date"], '%Y-%m-%d'),
                                          key=f"edit_date_input_{edit_trip_id}")

                # Vehicle selection
                try:
                    vehicle_options_clean = [v for v in VEHICLE_OPTIONS if v]
                    vehicle_index = vehicle_options_clean.index(
                        selected_trip["Vehicle"])
                except ValueError:
                    vehicle_index = 0

                edit_vehicle = st.selectbox("Vehicle:",
                                            vehicle_options_clean,
                                            index=vehicle_index,
                                            key=f"edit_vehicle_select_{edit_trip_id}")

                # KM inputs
                edit_start_km_input = st.number_input("Start KM:",
                                                      min_value=0,
                                                      value=selected_trip["Start KM"],
                                                      step=1,
                                                      key=f"edit_start_km_input_{edit_trip_id}")

                edit_end_km_input = st.number_input("End KM:",
                                                    min_value=0,
                                                    value=selected_trip["End KM"],
                                                    step=1,
                                                    key=f"edit_end_km_input_{edit_trip_id}")

                # Driver selection
                try:
                    driver_index = drivers.index(selected_trip["Driver"])
                except ValueError:
                    driver_index = 0

                edit_driver = st.selectbox("Driver Name:",
                                           options=drivers,
                                           index=driver_index,
                                           key=f"edit_driver_select_{edit_trip_id}")

                # Route selection
                st.subheader("Route (Select Stores by Region)")
                selected_stores = []
                current_route_list = [
                    store.strip() for store in selected_trip["Route"].split(',') if store.strip()]

                for region, stores in store_mapping.items():
                    stores.sort()
                    default_selection = [
                        store for store in stores if store in current_route_list]
                    selected_region_stores = st.multiselect(
                        f"{region}:",
                        options=stores,
                        default=default_selection,
                        key=f"edit_route_select_{edit_trip_id}_{region}")
                    selected_stores.extend(selected_region_stores)

                edit_route_list = selected_stores

                # Remarks
                edit_remarks = st.text_area("Remarks:",
                                            value=selected_trip["Remarks"],
                                            key=f"edit_remarks_input_{edit_trip_id}")

                # Admin fields
                st.subheader("Admin Edit Fields")

                try:
                    edited_by_options = [""] + [d for d in drivers if d != ""]
                    edited_by_index = edited_by_options.index(
                        selected_trip.get("Edited By", ""))
                except ValueError:
                    edited_by_index = 0

                edit_edited_by = st.selectbox("Edited By (Admin):",
                                              options=edited_by_options,
                                              index=edited_by_index,
                                              key=f"edit_edited_by_select_{edit_trip_id}")

                edit_fleet_change = st.text_area("Fleet Change (Admin Notes):",
                                                 value=selected_trip.get(
                                                     "Fleet Change", ""),
                                                 key=f"edit_fleet_change_input_{edit_trip_id}")

                # Save button inside form
                save_button = st.form_submit_button("Save Changes")

        # Delete button in separate column outside form
        with delete_col:
            delete_button = st.button("Delete Trip",
                                      key=f"delete_btn_{selected_trip['id']}")

        # Handle save button logic
        if save_button:
            try:
                start_km_value = int(edit_start_km_input)
                end_km_value = int(edit_end_km_input)
            except (ValueError, TypeError):
                st.error("Please enter valid numbers for Start KM and End KM.")
                st.stop()

            if edit_vehicle and edit_driver and edit_route_list:
                update_trip(edit_trip_id, edit_date, edit_vehicle, start_km_value, end_km_value,
                            edit_driver, edit_route_list, edit_remarks, edit_edited_by, edit_fleet_change)
                if f'confirm_delete_{edit_trip_id}' in st.session_state:
                    del st.session_state[f'confirm_delete_{edit_trip_id}']
                st.rerun()
            else:
                st.error(
                    "Please fill in all required fields (Vehicle, Driver Name, and select at least one Store for Route).")

        # Handle delete button logic
        confirm_state_key = f'confirm_delete_{selected_trip["id"]}'
        if delete_button:
            if st.session_state.get(confirm_state_key, False):
                delete_trip(edit_trip_id)
                if confirm_state_key in st.session_state:
                    del st.session_state[confirm_state_key]
                st.rerun()
            else:
                st.warning("Click 'Delete Trip' again to confirm.")
                st.session_state[confirm_state_key] = True
                st.rerun()

    else:
        st.info("Select a trip from the dropdown to edit.")
        for key in list(st.session_state.keys()):
            if key.startswith('confirm_delete_'):
                del st.session_state[key]
