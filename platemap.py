import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import io

# Inject custom CSS for well plate styling
st.markdown("""
    <style>
    .ag-theme-alpine .ag-cell {
        border: 1px solid #ccc !important;
        text-align: center;
        padding: 4px;
    }
    .ag-theme-alpine .ag-header-cell {
        background-color: #f0f0f0 !important;
        font-weight: bold;
        border: 1px solid #ccc !important;
    }
    </style>
    """, unsafe_allow_html=True)

#############################
# Helper Functions
#############################

def create_initial_dataframe(rows, cols):
    num_rows = ord(rows[1]) - ord(rows[0]) + 1
    num_cols = cols[1] - cols[0] + 1

    # Create a DataFrame with an extra row and column for headers.
    df = pd.DataFrame(index=range(num_rows + 1), columns=[str(i) for i in range(num_cols + 1)])
    df.columns = df.columns.map(str)

    # Set row headers (e.g., 'A' to 'P')
    df.iloc[0, 0] = ''
    df.iloc[1:num_rows + 1, 0] = [chr(i) for i in range(ord(rows[0]), ord(rows[1]) + 1)]

    # Set column headers (e.g., '1' to '24')
    df.iloc[0, 1:num_cols + 1] = [str(i) for i in range(cols[0], cols[1] + 1)]

    # Fill editable cells with empty strings.
    df.iloc[1:, 1:] = ""
    return df

def display_and_process_aggrid(df, key):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(enableRangeSelection=True, singleClickEdit=True)

    # Configure the header (alphabetical) column with dark background and white text.
    gb.configure_column(
        df.columns[0],
        editable=False,
        resizable=True,
        minWidth=80,
        maxWidth=80,
        cellStyle={"fontWeight": "bold", "backgroundColor": "#333333", "color": "white", "border": "1px solid #ccc"}
    )

    # Configure all other columns.
    for col in df.columns[1:]:
        gb.configure_column(
            col,
            editable=True,
            resizable=True,
            minWidth=80,
            maxWidth=80,
            cellStyle={"border": "1px solid #ccc", "textAlign": "center", "padding": "4px"}
        )

    grid_options = gb.build()
    grid_options['rowHeight'] = 80  # Square cells

    # Calculate grid height based on DataFrame's number of rows.
    calculated_height = df.shape[0] * 80 + 50

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        key=key,
        theme="alpine",
        height=calculated_height
    )
    return grid_response['data']

def process_combined_changes(grid_data_list, value_labels):
    """
    Combines multiple grid data DataFrames into one output DataFrame.
    Each grid corresponds to one user-defined value.
    """
    # Assume each grid_data has the same shape.
    rows = grid_data_list[0].shape[0]
    cols = grid_data_list[0].shape[1]
    changes = []
    for r in range(1, rows):  # Skip header row
        for c in range(1, cols):  # Skip header column
            cell_values = [grid_data.iloc[r, c] for grid_data in grid_data_list]
            if any(str(v).strip() for v in cell_values):
                cell_position = f"{grid_data_list[0].iloc[r, 0]}{grid_data_list[0].columns[c]}"
                changes.append([cell_position] + cell_values)
    labels_df = pd.DataFrame(changes, columns=["Cell Position"] + value_labels)
    return labels_df

def download_data(labels_df):
    if st.button('Download Labels as Excel'):
        towrite = io.BytesIO()
        labels_df.to_excel(towrite, index=False, engine='xlsxwriter')
        towrite.seek(0)
        st.download_button(
            label="Download as Excel",
            data=towrite,
            file_name='labels.xlsx',
            mime='application/vnd.ms-excel'
        )
    if st.button('Download Labels as TXT'):
        towrite = io.StringIO()
        labels_df.to_csv(towrite, sep='\t', index=False)
        towrite.seek(0)
        st.download_button(
            label="Download as TXT",
            data=towrite.getvalue(),
            file_name='labels.txt',
            mime='text/plain'
        )

def plate_mapper(title, rows, cols, session_key_prefix):
    st.title(title)
    # Initialize dynamic value labels and counter if not set.
    if f"value_labels_{session_key_prefix}" not in st.session_state:
        st.session_state[f"value_labels_{session_key_prefix}"] = ["Gene", "Sample"]
    if f"new_value_counter_{session_key_prefix}" not in st.session_state:
        st.session_state[f"new_value_counter_{session_key_prefix}"] = 1

    st.write("### Define Value Labels")
    new_labels = []
    for i, label in enumerate(st.session_state[f"value_labels_{session_key_prefix}"]):
        new_label = st.text_input(f"Value {i+1} Label", label, key=f"value_label_{session_key_prefix}_{i}")
        new_labels.append(new_label)
    st.session_state[f"value_labels_{session_key_prefix}"] = new_labels

    # Button to add a new value field with a unique default label.
    if st.button(f"Add Value ({session_key_prefix})"):
        new_label = f"New Value {st.session_state[f'new_value_counter_{session_key_prefix}']}"
        st.session_state[f"value_labels_{session_key_prefix}"].append(new_label)
        st.session_state[f"new_value_counter_{session_key_prefix}"] += 1
        st.rerun()

    # Create the well plate dataframe.
    df = create_initial_dataframe(rows, cols)
    # Create a tab for each value label.
    tabs = st.tabs([f"{lbl}" for lbl in st.session_state[f"value_labels_{session_key_prefix}"]])
    grid_data_list = []
    for i, tab in enumerate(tabs):
        with tab:
            st.subheader(st.session_state[f"value_labels_{session_key_prefix}"][i])
            grid_data = display_and_process_aggrid(df.copy(), f"grid_{session_key_prefix}_{i}")
            grid_data_list.append(grid_data)

    # Combine all grids into a single dataframe.
    labels_df = process_combined_changes(grid_data_list, st.session_state[f"value_labels_{session_key_prefix}"])
    st.write("### Combined Labels")
    st.write(labels_df)
    download_data(labels_df)

#############################
# Plate Mapper Functions for Each Type
#############################

def plate_384():
    # 384 Well Plate: 16 rows (A-P), 24 columns (1-24)
    plate_mapper("384 Well Plate Mapper", ('A', 'P'), (1, 24), "384")

def plate_96():
    # 96 Well Plate: 8 rows (A-H), 12 columns (1-12)
    plate_mapper("96 Well Plate Mapper", ('A', 'H'), (1, 12), "96")

def plate_48():
    # 48 Well Plate: 6 rows (A-F), 8 columns (1-8)
    plate_mapper("48 Well Plate Mapper", ('A', 'F'), (1, 8), "48")

def plate_24():
    # 24 Well Plate: 4 rows (A-D), 6 columns (1-6)
    plate_mapper("24 Well Plate Mapper", ('A', 'D'), (1, 6), "24")

def plate_12():
    # 12 Well Plate: 3 rows (A-C), 4 columns (1-4)
    plate_mapper("12 Well Plate Mapper", ('A', 'C'), (1, 4), "12")

def plate_6():
    # 6 Well Plate: 2 rows (A-B), 3 columns (1-3)
    plate_mapper("6 Well Plate Mapper", ('A', 'B'), (1, 3), "6")
