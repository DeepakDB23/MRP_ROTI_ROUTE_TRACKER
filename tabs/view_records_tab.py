# tabs/view_records_tab.py

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import filter_trips, count_stores_in_route  # Import necessary functions
from config import VEHICLE_OPTIONS  # Import vehicle options


def display_view_records_tab():
    """Displays the UI and handles logic for the View Records tab."""
    st.header("KM Records")  # Changed title slightly

    # --- Filters ---
    st.subheader("Filter Records")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        # Date input will default to today based on the server's time zone
        filter_start_date = st.date_input("Start Date:", datetime.now().replace(
            day=1), key="filter_start_date")  # Default to start of current month
    with col_date2:
        filter_end_date = st.date_input(
            "End Date:", datetime.now(), key="filter_end_date")  # Default to today

    # Filter by Vehicle
    filter_vehicle = st.selectbox("Filter by Vehicle:", VEHICLE_OPTIONS + [
                                  "All"], index=len(VEHICLE_OPTIONS), key="filter_vehicle_select")  # Added key

    # Apply filters using the utility function
    # filter_trips now works with the data loaded into st.session_state.trips
    filtered_trips = filter_trips(
        st.session_state.trips, filter_start_date, filter_end_date, filter_vehicle)

    # --- Sorting Options ---
    st.subheader("Sort Records")
    sort_options = {
        "Date (Latest First)": ("Date", True),
        "Date (Oldest First)": ("Date", False),
        # Sort by Vehicle ascending, then Date descending
        "Vehicle then Date (A-Z)": ("Vehicle", False, "Date", True),
        # Sort by Vehicle descending, then Date descending
        "Vehicle then Date (Z-A)": ("Vehicle", True, "Date", True),
    }
    sort_by = st.selectbox("Sort By:", options=list(
        sort_options.keys()), key="view_records_sort_by")

    # Apply sorting
    sort_params = sort_options[sort_by]
    if len(sort_params) == 2:  # Simple sort by one column
        # Ensure the key exists before attempting to sort
        try:
            filtered_trips.sort(key=lambda x: datetime.strptime(
                x.get(sort_params[0], '1900-01-01'), '%Y-%m-%d'), reverse=sort_params[1])
        except (ValueError, TypeError):
            # Handle cases where date might be in an unexpected format or missing
            st.warning(
                f"Could not sort by {sort_params[0]}. Ensure date format is YYYY-MM-DD.")
            # Fallback to no sorting or a default sort
            pass  # Or implement a fallback sort

    elif len(sort_params) == 4:  # Sort by two columns
        # Sort by the secondary key first (Date)
        try:
            filtered_trips.sort(key=lambda x: datetime.strptime(
                x.get(sort_params[2], '1900-01-01'), '%Y-%m-%d'), reverse=sort_params[3])
        except (ValueError, TypeError):
            st.warning(
                f"Could not sort by {sort_params[2]}. Ensure date format is YYYY-MM-DD.")
            pass  # Or implement a fallback sort

        # Then sort by the primary key (Vehicle), preserving the order of the secondary sort
        try:
            filtered_trips.sort(key=lambda x: x.get(
                sort_params[0], ''), reverse=sort_params[1])
        except (ValueError, TypeError):
            st.warning(f"Could not sort by {sort_params[0]}.")
            pass  # Or implement a fallback sort

    # --- Display only the latest 10 trips ---
    # Take the first 10 after sorting and filtering
    latest_10_trips = filtered_trips[:10]

    # Indicate this is a limited view
    st.subheader("Latest 10 Trips (Filtered)")

    # Display table
    if latest_10_trips:
        # Create a pandas DataFrame for display
        df_display = pd.DataFrame(latest_10_trips)
        # Drop columns that should not be displayed in the main table
        columns_to_display = [col for col in df_display.columns if col not in [
            "id", "Edited By", "Fleet Change", "License Plate at Trip Time"]]

        # --- Apply text wrapping and column width hints ---
        # Streamlit's st.dataframe has limited direct styling.
        # We can provide column configurations as a hint, but exact rendering depends on Streamlit.
        column_config = {
            # Hint for medium width
            "Route": st.column_config.Column("Route", width="medium"),
            # Hint for large width
            "Remarks": st.column_config.Column("Remarks", width="large"),
            # Add other columns if needed
        }
        # Note: Text wrapping is often handled automatically by st.dataframe
        # within the column width constraints it determines.

        st.dataframe(df_display[columns_to_display],
                     hide_index=True, column_config=column_config)
    else:
        st.info("No trip records found matching the filters.")

    # --- Download Options ---
    st.subheader("Download Options")

    # Download Filtered Trip Records CSV
    if filtered_trips:  # Only show button if there are filtered trips to download
        df_filtered_download = pd.DataFrame(
            filtered_trips)  # Use the filtered list here
        csv_data_filtered = df_filtered_download.to_csv(
            index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Trip Records CSV",
            data=csv_data_filtered,
            file_name=f"rotiroute_filtered_records_{filter_start_date.strftime('%Y%m%d')}_to_{filter_end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_filtered_csv"  # Unique key
        )
    else:
        st.info("No filtered trips to download.")

    # Full Trip Records CSV Download (uses the complete trips list)
    # Create a DataFrame with all columns for download
    df_full_download = pd.DataFrame(
        st.session_state.trips)  # Use the complete list here
    csv_data_full = df_full_download.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Trip Records CSV (All Data)",  # Clarified label
        data=csv_data_full,
        file_name="rotiroute_full_records.csv",
        mime="text/csv",
        key="download_full_csv"  # Unique key for the download button
    )

    st.markdown("---")  # Separator

    # Store Count CSV Download with Date Range
    st.subheader("Store Counts by Date Range (for download)")
    # Use new columns for this date range to avoid key conflicts
    col_date3, col_date4 = st.columns(2)
    with col_date3:
        store_count_start_date = st.date_input("Start Date for Store Count:", datetime.now(
        ).replace(day=1), key="store_count_start_date")
    with col_date4:
        store_count_end_date = st.date_input(
            "End Date for Store Count:", datetime.now(), key="store_count_end_date")

    # Generate and Download Store Count CSV button
    if st.button("Generate and Download Store Count CSV"):
        # Filter trips by date range for store count using the utility function
        trips_in_range = filter_trips(st.session_state.trips, store_count_start_date,
                                      store_count_end_date, "All")  # Store count is for all vehicles

        # Count stores
        store_counts = {}
        for trip in trips_in_range:
            route_string = trip["Route"]
            stores = [store.strip()
                      for store in route_string.split(',') if store.strip()]
            for store in stores:
                store_counts[store] = store_counts.get(store, 0) + 1

        # Create DataFrame for store counts
        df_store_counts = pd.DataFrame(
            list(store_counts.items()), columns=['Store', 'Count'])
        df_store_counts = df_store_counts.sort_values(
            by='Count', ascending=False)  # Sort by count

        if not df_store_counts.empty:
            csv_data_stores = df_store_counts.to_csv(
                index=False).encode('utf-8')
            st.download_button(
                label="Click here to download Store Count CSV",
                data=csv_data_stores,
                file_name=f"rotiroute_store_counts_{store_count_start_date.strftime('%Y%m%d')}_to_{store_count_end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_store_count_csv"  # Unique key
            )
        else:
            st.info("No trips found in the selected date range to count stores.")
