import streamlit as st
st.set_page_config(layout="wide")  # Use wide mode by default

# Detailed usage instructions in the sidebar
st.sidebar.title("Plate Mapper Instructions")
st.sidebar.markdown("""
**Usage Instructions:**

1. **Select Plate Type:**  
   - Use the dropdown menu below to choose the type of well plate you wish to map.
   - Options include: 384, 96, 48, 24, 12, and 6 well plates.

2. **Define Value Labels:**  
   - In the main area, you'll see default value labels (e.g., "Gene" and "Sample").
   - Edit these labels as needed by typing in the text fields.
   - Click **"Add Value"** to add additional value fields. Each new field is given a unique default name (e.g., "New Value 1", "New Value 2", etc.) to avoid duplicate labels.

3. **Mapping the Well Plate:**  
   - The well plate is displayed in a grid layout that mimics the physical plate.
   - Each value label appears as a separate tab—click on a tab to fill in data for that particular value.
   - Each cell in the grid corresponds to a well on the plate. Enter your data in the appropriate cells.

4. **Review & Download:**  
   - A combined table of all entered values is generated and displayed below the grids.
   - Use the download buttons to export the combined data as an Excel or TXT file.

**Note:**  
- The grid dimensions (number of rows and columns) match the selected plate type.
- Ensure your data is entered according to the well plate layout as shown.
""", unsafe_allow_html=True)

import platemap

def main():
    st.sidebar.title("Plate Type Selection")
    plate_type = st.sidebar.selectbox("Choose the plate type", [
        "Select or Reset", 
        "384 Well Plate", 
        "96 Well Plate", 
        "48 Well Plate", 
        "24 Well Plate", 
        "12 Well Plate", 
        "6 Well Plate"
    ])
    
    if plate_type == "384 Well Plate":
        platemap.plate_384()
    elif plate_type == "96 Well Plate":
        platemap.plate_96()
    elif plate_type == "48 Well Plate":
        platemap.plate_48()
    elif plate_type == "24 Well Plate":
        platemap.plate_24()
    elif plate_type == "12 Well Plate":
        platemap.plate_12()
    elif plate_type == "6 Well Plate":
        platemap.plate_6()

if __name__ == "__main__":
    main()
