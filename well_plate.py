import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import io

def plate_384():
    st.title("384 Well Plate Mapper")
    rows, cols = ('A', 'P'), (1, 24)
    df1 = create_initial_dataframe(rows, cols)
    df2 = create_initial_dataframe(rows, cols)

    value_column_label_1 = st.text_input("First Value", "Gene")
    value_column_label_2 = st.text_input("Second Value", "Sample")

    st.write("First Value:")
    df1_updated = display_and_process_aggrid(df1, "grid1")

    st.write("Second Value:")
    df2_updated = display_and_process_aggrid(df2, "grid2")

    labels_df = process_combined_changes(df1_updated, df2_updated, value_column_label_1, value_column_label_2)
    st.write("Labels:", labels_df)
    download_data(labels_df)

def plate_96():
    st.title("96 Well Plate Mapper")
    rows, cols = ('A', 'H'), (1, 12)
    df1 = create_initial_dataframe(rows, cols)
    df2 = create_initial_dataframe(rows, cols)

    value_column_label_1 = st.text_input("First Value", "Gene")
    value_column_label_2 = st.text_input("Second Value", "Sample")

    st.write("First Editable Table:")
    df1_updated = display_and_process_aggrid(df1, "grid1")

    st.write("Second Editable Table:")
    df2_updated = display_and_process_aggrid(df2, "grid2")

    labels_df = process_combined_changes(df1_updated, df2_updated, value_column_label_1, value_column_label_2)
    st.write("Labels:", labels_df)
    download_data(labels_df)

# Other functions (create_initial_dataframe, display_and_process_aggrid, download_excel) remain the same.



def create_initial_dataframe(rows, cols):
    num_rows = ord(rows[1]) - ord(rows[0]) + 1
    num_cols = cols[1] - cols[0] + 1

    # Create an empty DataFrame with specified dimensions
    df = pd.DataFrame(index=range(num_rows + 1), columns=[str(i) for i in range(num_cols + 1)])

    # Convert all column indices to strings
    df.columns = df.columns.map(str)

    # Set the row headers (e.g., 'A' to 'P' for 384-well plate)
    df.iloc[0, 0] = ''
    df.iloc[1:num_rows + 1, 0] = [chr(i) for i in range(ord(rows[0]), ord(rows[1]) + 1)]

    # Set the column headers ('1' to '24' for 384-well plate)
    df.iloc[0, 1:num_cols + 1] = [str(i) for i in range(cols[0], cols[1] + 1)]

    # Fill the cells with empty strings for the editable cells
    df.iloc[1:, 1:] = ""

    return df



def display_and_process_aggrid(df, key):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(enableRangeSelection=True, singleClickEdit=True)

    # Set the first column to be non-editable (header)
    gb.configure_column(df.columns[0], editable=False, resizable=True, minWidth=50, maxWidth=50)

    # Make other columns editable and adjust their width
    for col in df.columns[1:]:
        gb.configure_column(col, editable=True, resizable=True, minWidth=50, maxWidth=50)

    grid_options = gb.build()
    grid_response = AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.VALUE_CHANGED, key=key)
    return grid_response['data']



def process_combined_changes(df1, df2, label1, label2):
    changes = []
    for row in range(1, len(df1)):
        for col in range(1, len(df1.columns)):
            value1 = df1.iloc[row, col]
            value2 = df2.iloc[row, col]
            if value1 or value2:
                cell_position = f"{df1.iloc[row, 0]}{df1.columns[col]}"
                changes.append([cell_position, value1, value2])

    labels_df = pd.DataFrame(changes, columns=['Cell Position', label1, label2])
    return labels_df


def download_data(labels_df):
    # Excel Download
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

    # Text File Download
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

