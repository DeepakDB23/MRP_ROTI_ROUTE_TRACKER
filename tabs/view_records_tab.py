# tabs/view_records_tab.py

import streamlit as st
import pandas as pd
from datetime import datetime
# count_stores_in_route is not used for this specific change
from utils import filter_trips
from config import VEHICLE_OPTIONS


def display_view_records_tab():
    """Displays the UI and handles logic for the View Records tab."""
    st.header("KM Records")

    # --- Filters ---
    st.subheader("Filter Records")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        filter_start_date = st.date_input("Start Date:", datetime.now().replace(
            day=1), key="filter_start_date")
    with col_date2:
        filter_end_date = st.date_input(
            "End Date:", datetime.now(), key="filter_end_date")

    filter_vehicle_selectbox = st.selectbox("Filter by Vehicle:", VEHICLE_OPTIONS + [
        "All"], index=len(VEHICLE_OPTIONS), key="filter_vehicle_select")

    filtered_trips_list = filter_trips(
        st.session_state.trips, filter_start_date, filter_end_date, filter_vehicle_selectbox
    )

    # --- Sorting Options ---
    st.subheader("Sort Records")
    sort_options = {
        "Date (Latest First)": ("Date", True),
        "Date (Oldest First)": ("Date", False),
        # Secondary sort (Date) Ascending
        "Vehicle then Date (A-Z)": ("Vehicle", False, "Date", True),
        # Secondary sort (Date) Ascending
        "Vehicle then Date (Z-A)": ("Vehicle", True, "Date", True),
    }
    sort_by = st.selectbox("Sort By:", options=list(
        sort_options.keys()), key="view_records_sort_by")

    # Make a mutable copy for sorting and modification
    processed_trips_for_display = list(filtered_trips_list)

    sort_params = sort_options[sort_by]
    if len(sort_params) == 2:
        try:
            # Ensure date conversion for sorting
            processed_trips_for_display.sort(
                key=lambda x: datetime.strptime(
                    x.get(sort_params[0], '1900-01-01'), '%Y-%m-%d')
                # Handle None dates
                if x.get(sort_params[0]) else datetime.min,
                reverse=sort_params[1]
            )
        except (ValueError, TypeError) as e:
            st.warning(
                f"Could not sort by {sort_params[0]}. Ensure date format is YYYY-MM-DD. Error: {e}")
    elif len(sort_params) == 4:  # Multi-level sort
        try:
            # Sort by secondary key (Date) first
            processed_trips_for_display.sort(
                key=lambda x: datetime.strptime(
                    x.get(sort_params[2], '1900-01-01'), '%Y-%m-%d')
                # Handle None dates
                if x.get(sort_params[2]) else datetime.min,
                reverse=sort_params[3]  # Date direction as per user choice
            )
            # Then sort by primary key (Vehicle)
            processed_trips_for_display.sort(
                # Handle None vehicle names
                key=lambda x: x.get(sort_params[0], ''),
                reverse=sort_params[1]
            )
        except (ValueError, TypeError) as e:
            st.warning(
                f"Could not perform multi-level sort. Ensure data integrity. Error: {e}")

    # --- NEW: Calculate Accumulated KM for Filtered Period ---
    if processed_trips_for_display:
        # Create a temporary list of trips sorted by Vehicle (asc), then Date (asc) for accurate calculation
        # This ensures chronological processing per vehicle regardless of display sort.
        trips_for_calc = sorted(
            processed_trips_for_display,
            key=lambda x: (
                x.get('Vehicle', ''),
                datetime.strptime(x.get('Date', '1900-01-01'),
                                  '%Y-%m-%d') if x.get('Date') else datetime.min
            )
        )

        vehicle_last_filtered_accum_km = {}
        trip_id_to_filtered_accum_km = {}  # Using trip ID as a robust key

        for trip in trips_for_calc:
            trip_id = trip.get("id")
            if not trip_id:  # Should not happen if IDs are always generated
                continue

            vehicle = trip.get("Vehicle")
            start_km_val = trip.get("Start KM", 0)
            end_km_val = trip.get("End KM", 0)

            try:
                # Ensure KM values are numeric, defaulting to 0 if problematic
                current_start_km = int(float(start_km_val)) if pd.notna(
                    start_km_val) and str(start_km_val).replace('.', '', 1).isdigit() else 0
                current_end_km = int(float(end_km_val)) if pd.notna(
                    end_km_val) and str(end_km_val).replace('.', '', 1).isdigit() else 0
            except (ValueError, TypeError):
                current_start_km = 0
                current_end_km = 0
                # st.warning(f"Invalid KM data for trip ID {trip_id} on {trip.get('Date')}. Using 0 for calculation.")

            daily_km_delta = current_end_km - current_start_km

            if vehicle not in vehicle_last_filtered_accum_km:
                trip_filtered_accum_km = daily_km_delta
            else:
                trip_filtered_accum_km = vehicle_last_filtered_accum_km[vehicle] + \
                    daily_km_delta

            vehicle_last_filtered_accum_km[vehicle] = trip_filtered_accum_km
            trip_id_to_filtered_accum_km[trip_id] = trip_filtered_accum_km

        # Add the calculated "Accumulated KM (Filtered)" to each trip in the display list
        for trip_in_display_list in processed_trips_for_display:
            calc_km = trip_id_to_filtered_accum_km.get(
                trip_in_display_list.get("id"))
            trip_in_display_list["Accumulated KM (Filtered)"] = calc_km if calc_km is not None else 0
    # --- END NEW ---

    latest_10_trips_display = processed_trips_for_display[:10]

    st.subheader("Latest 10 Trips (Filtered)")

    if latest_10_trips_display:
        df_display = pd.DataFrame(latest_10_trips_display)

        # Define columns to display, including the new one
        # Ensure "Accumulated KM" (overall) is also present if desired
        columns_to_display_ordered = [
            "Date", "Vehicle", "Start KM", "End KM",
            "Accumulated KM", "Accumulated KM (Filtered)",  # Added new column
            "Driver", "Route", "Remarks"
        ]
        # Ensure all columns in `columns_to_display_ordered` exist in `df_display`
        # This also sets the column order for the display
        final_columns_for_df = [
            col for col in columns_to_display_ordered if col in df_display.columns]

        column_config = {
            "Route": st.column_config.TextColumn("Route", width="medium", help="Stores visited"),
            "Remarks": st.column_config.TextColumn("Remarks", width="large"),
            "Accumulated KM": st.column_config.NumberColumn(label="Total Accum. KM"),
            "Accumulated KM (Filtered)": st.column_config.NumberColumn(label="Period Accum. KM", help="Accumulated KM for the selected filter period and vehicle."),
            "Start KM": st.column_config.NumberColumn(label="Start KM"),
            "End KM": st.column_config.NumberColumn(label="End KM"),
        }

        st.dataframe(
            df_display[final_columns_for_df],
            hide_index=True,
            column_config=column_config
        )
    else:
        st.info("No trip records found matching the filters.")

    # --- Download Options ---
    st.subheader("Download Options")

    if processed_trips_for_display:  # Use the full filtered and processed list for download
        df_filtered_download = pd.DataFrame(processed_trips_for_display)
        # Ensure the new column is in the CSV; it should be from the processing above

        csv_data_filtered = df_filtered_download.to_csv(
            index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Trip Records CSV",
            data=csv_data_filtered,
            file_name=f"rotiroute_filtered_records_{filter_start_date.strftime('%Y%m%d')}_to_{filter_end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_filtered_csv"
        )
    else:
        st.info("No filtered trips to download.")

    # Full Trip Records CSV Download (uses the complete trips list from session state)
    if st.session_state.trips:
        df_full_download = pd.DataFrame(st.session_state.trips)
        csv_data_full = df_full_download.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Full Trip Records CSV (All Data)",
            data=csv_data_full,
            file_name="rotiroute_full_records.csv",
            mime="text/csv",
            key="download_full_csv"
        )

    st.markdown("---")

    # Store Count CSV Download with Date Range
    st.subheader("Store Counts by Date Range")
    col_date3, col_date4 = st.columns(2)
    with col_date3:
        store_count_start_date = st.date_input("Start Date for Store Count:", datetime.now(
        ).replace(day=1), key="store_count_start_date")
    with col_date4:
        store_count_end_date = st.date_input(
            "End Date for Store Count:", datetime.now(), key="store_count_end_date")

    if st.button("Generate and Download Store Count CSV"):  # Key for this button implicit
        trips_in_range_for_store_count = filter_trips(st.session_state.trips, store_count_start_date,
                                                      store_count_end_date, "All")

        store_counts = {}
        for trip in trips_in_range_for_store_count:
            route_string = trip.get("Route", "")
            stores = [store.strip()
                      for store in route_string.split(',') if store.strip()]
            for store in stores:
                store_counts[store] = store_counts.get(store, 0) + 1

        if store_counts:
            df_store_counts = pd.DataFrame(
                list(store_counts.items()), columns=['Store', 'Count'])
            df_store_counts = df_store_counts.sort_values(
                by='Count', ascending=False)

            csv_data_stores = df_store_counts.to_csv(
                index=False).encode('utf-8')

            st.download_button(
                label="Click here to download Store Count CSV",
                data=csv_data_stores,
                file_name=f"rotiroute_store_counts_{store_count_start_date.strftime('%Y%m%d')}_to_{store_count_end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_store_count_csv_generated"  # Unique key
            )
        else:
            st.info("No trips found in the selected date range to count stores.")
