# tabs/add_trip_tab.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta  # Added timedelta
from utils import get_drivers_list, add_trip
from config import VEHICLE_OPTIONS, STORE_REGION_MAPPING
import time


def get_latest_end_km(vehicle):
    """Finds the End KM of the latest trip for a given vehicle."""
    if not vehicle or vehicle == "" or 'trips' not in st.session_state or not st.session_state.trips:
        return 0
    latest_trip_for_vehicle = None
    try:
        valid_trips = [
            trip for trip in st.session_state.trips
            if isinstance(trip.get("Date"), str) and trip.get("Date")
        ]
        parsed_trips = []
        for trip in valid_trips:
            try:
                datetime.strptime(trip["Date"], '%Y-%m-%d')
                parsed_trips.append(trip)
            except ValueError:
                pass
        sorted_trips = sorted(
            parsed_trips,
            key=lambda x: datetime.strptime(x["Date"], '%Y-%m-%d'),
            reverse=True
        )
    except TypeError as e:
        st.error(f"Error processing trip data structure: {e}.")
        return 0

    for trip in sorted_trips:
        if trip.get("Vehicle") == vehicle:
            latest_trip_for_vehicle = trip
            break
    if latest_trip_for_vehicle:
        end_km = latest_trip_for_vehicle.get("End KM", 0)
        try:
            if pd.notna(end_km):
                end_km_str = str(end_km).strip()
                if end_km_str.replace('.', '', 1).isdigit():
                    return int(float(end_km_str))
                else:
                    return 0
            else:
                return 0
        except (ValueError, TypeError):
            return 0
    else:
        return 0


def display_add_trip_tab():
    """Displays the UI and handles logic for the Add New Trip tab."""

    # --- Reset vehicle select and bypass flag if trip was added ---
    if 'trip_added' in st.session_state and st.session_state.trip_added:
        st.session_state.add_trip_vehicle_select = ""
        st.session_state.trip_added = False
        # Clean up any bypass flags related to previous attempts
        for key in list(st.session_state.keys()):
            if key.startswith('bypass_warning_'):
                del st.session_state[key]
    # --------------------------------------------------

    st.header("Add New Trip")
    #st.warning("⚠️ Please ensure the dates are correct while filling the sheet")
    #st.warning(
        #"🔴 Always cross check the start kms matches the previous trip of the corresponding Vehicle type")

    drivers = get_drivers_list()
    store_mapping = STORE_REGION_MAPPING
    all_stores_flat = sorted(
        [store for region_stores in store_mapping.values() for store in region_stores])

    selected_vehicle = st.selectbox(
        "Vehicle:",
        options=VEHICLE_OPTIONS,
        key="add_trip_vehicle_select",
        index=0,
        format_func=lambda x: "Select Vehicle..." if x == "" else x
    )

    latest_end_km_value = 0
    if selected_vehicle and selected_vehicle != "":
        latest_end_km_value = get_latest_end_km(selected_vehicle)
        if latest_end_km_value > 0:
            st.markdown(
                f"The latest End KM recorded for **{selected_vehicle}** is: **{latest_end_km_value}**")
        else:
            st.markdown(
                f"No previous End KM found for **{selected_vehicle}**.")
    else:
        st.markdown(
            "*(Select a Vehicle above to see its latest recorded End KM)*")

    start_km_default = latest_end_km_value if latest_end_km_value > 0 else 0

    with st.form("add_trip_form"):
        add_date = st.date_input(
            "Date:", datetime.now().date(), key="add_trip_date_input")

        add_start_km_input = st.number_input(
            "Start KM:",
            min_value=0,
            value=start_km_default,
            step=1,
            key="add_start_km_input"
        )

        current_start_km = st.session_state.get(
            "add_start_km_input", start_km_default)
        try:
            current_start_km_int = int(current_start_km)
        except (ValueError, TypeError):
            current_start_km_int = 0

        add_end_km_input = st.number_input(
            "End KM:",
            min_value=current_start_km_int,
            value=current_start_km_int,
            step=1,
            key="add_end_km_input"
        )

        add_driver = st.selectbox(
            "Driver Name:",
            options=drivers,
            key="add_trip_driver_select",
            index=0,
            format_func=lambda x: "Select Driver..." if x == "" else x
        )

        st.subheader("Route (Select Stores by Region)")
        selected_stores = []
        for region, stores in store_mapping.items():
            stores.sort()
            selected_region_stores = st.multiselect(
                f"{region}:", options=stores, key=f"add_route_select_{region}")
            selected_stores.extend(selected_region_stores)

        add_route_list = selected_stores
        add_remarks = st.text_area("Remarks:", key="add_trip_remarks_input")

        submitted = st.form_submit_button("Add Trip")
        if submitted:
            try:
                start_km_value = int(st.session_state.add_start_km_input)
                end_km_value = int(st.session_state.add_end_km_input)
            except (ValueError, TypeError, KeyError):
                st.error("Please enter valid numbers for Start KM and End KM.")
                st.stop()

            error_messages = []
            final_selected_vehicle = st.session_state.add_trip_vehicle_select
            final_selected_driver = st.session_state.add_trip_driver_select

            if not final_selected_vehicle or final_selected_vehicle == "":
                error_messages.append("Vehicle is required.")
            if start_km_value < 0:
                error_messages.append("Start KM cannot be negative.")
            if end_km_value < start_km_value:
                error_messages.append("End KM cannot be less than Start KM.")
            if not final_selected_driver or final_selected_driver == "":
                error_messages.append("Driver Name is required.")
            if not add_route_list:
                error_messages.append(
                    "Please select at least one Store for the Route.")

            # --- NEW: Previous Day Check ---
            previous_day_not_filled_warning_triggered = False
            bypass_flag_key = f'bypass_warning_{final_selected_vehicle}_{add_date.strftime("%Y%m%d")}'

            if final_selected_vehicle and final_selected_vehicle != "":
                previous_day_date_obj = add_date - timedelta(days=1)
                previous_day_str = previous_day_date_obj.strftime('%Y-%m-%d')
                found_previous_day_trip = False
                if 'trips' in st.session_state and st.session_state.trips:
                    for trip_item in st.session_state.trips:
                        if trip_item.get("Vehicle") == final_selected_vehicle and \
                           trip_item.get("Date") == previous_day_str:
                            found_previous_day_trip = True
                            break
                if not found_previous_day_trip:
                    previous_day_not_filled_warning_triggered = True

            if previous_day_not_filled_warning_triggered and not st.session_state.get(bypass_flag_key, False):
                st.warning(
                    f"Previous day ({previous_day_date_obj.strftime('%Y-%m-%d')}) has not been filled for Vehicle {final_selected_vehicle}. "
                    "Ensure the date is correct. Click 'Add Trip' again to bypass this warning and submit."
                )
                # Set flag to bypass on next click
                st.session_state[bypass_flag_key] = True
                st.stop()  # Stop current submission, user needs to click again
            # --- END NEW: Previous Day Check ---

            final_latest_end_km = 0  # Recalculate for current vehicle just in case
            if final_selected_vehicle and final_selected_vehicle != "":
                final_latest_end_km = get_latest_end_km(final_selected_vehicle)

            if final_selected_vehicle and final_latest_end_km > 0 and start_km_value != final_latest_end_km:
                error_messages.append(
                    f"Start KM ({start_km_value}) must match the latest recorded End KM ({final_latest_end_km}) for {final_selected_vehicle}.")

            if error_messages:
                for msg in error_messages:
                    st.error(msg)
                # If other errors occurred AFTER the bypass flag was set for previous day warning,
                # we might want to unset it to force re-acknowledgment if those other errors are fixed.
                # However, for simplicity, we'll let it persist as the user already acknowledged it once.
            else:
                if add_trip(add_date, final_selected_vehicle, start_km_value, end_km_value, final_selected_driver, add_route_list, add_remarks):
                    st.session_state.trip_added = True  # This will trigger cleanup at the top
                    # Explicitly clean the specific bypass flag that was used for this successful submission
                    if bypass_flag_key in st.session_state:
                        del st.session_state[bypass_flag_key]
                    st.success("Trip added successfully! ✅")
                    time.sleep(1)  # Reduced sleep time
                    st.rerun()
