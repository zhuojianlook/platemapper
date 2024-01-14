import streamlit as st
import well_plate

def main():
    st.sidebar.title("Plate Type Selection")
    plate_type = st.sidebar.selectbox("Choose the plate type", ["Select or Reset", "384 Well Plate", "96 Well Plate"])

    if plate_type == "384 Well Plate":
        well_plate.plate_384()
    elif plate_type == "96 Well Plate":
        well_plate.plate_96()

if __name__ == "__main__":
    main()
