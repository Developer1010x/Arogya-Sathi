# Importing Our Classes
from Person import *
from Doctor import *
from Nurse import *
from Patient import *
from Operation import *
from Hospital import *

# Importing Libraries
import pandas as pd
import numpy as np
import os
from PIL import Image
from time import sleep
import datetime

import pandas as pd
import numpy as np
import streamlit as st
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu
import warnings

st.set_page_config(
    page_title="L Hospital App",
    page_icon="👨‍⚕️",
    layout="wide"
)

warnings.simplefilter(action='ignore', category=FutureWarning)

if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

def callback():
    st.session_state.button_clicked = True

hospital = Hospital("LLM", "L Hospital ")

st.markdown(
    """
    <style>
         .main {
            text-align: center;
         }

         div.block-containers{
            padding-top: 0.5rem
         }

         .st-emotion-cache-z5fcl4{
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1.5rem;
            padding-right: 2.8rem;
            overflow-x: hidden;
         }

         .st-emotion-cache-16txtl3{
            padding: 2.7rem 0.6rem
         }
         div.st-emotion-cache-1r6slb0{
            padding: 15px 5px;
            background-color: #111;
            border-radius: 5px;
            border: 3px solid #5E0303;
            opacity: 0.9;
         }
        div.st-emotion-cache-1r6slb0:hover{
            transition: all 0.5s ease-in-out;
            background-color: #000;
            border: 3px solid red;
            opacity: 1;
         }

         .plot-container.plotly{
            border: 4px solid #333;
            border-radius: 7px;
         }

         div.st-emotion-cache-1r6slb0 span.st-emotion-cache-10trblm{
            font: bold 24px tahoma;
         }
         div [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
        
        /* Custom styles for delete buttons */
        .stButton > button[kind="secondary"] {
            background-color: #ff4444;
            color: white;
            border: 1px solid #ff4444;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #cc0000;
            border: 1px solid #cc0000;
        }
        
        /* Custom styles for edit buttons */
        .edit-button {
            background-color: #ffa500;
            color: white;
            border: 1px solid #ffa500;
        }
    </style>
    """,
    unsafe_allow_html=True
)

sub_options_style = {
    "container": {"padding": "8!important", "background-color": '#101010', "border": "2px solid darkcyan"},
    "nav-link": {"color": "white", "padding": "10px", "font-size": "15px", "text-align": "center", "margin": "10px 0px", },
    "nav-link-selected": {"background-color": "#0CB9B9"},
}

@st.cache_data
def is_valid_first_name(fname):
    return len(fname) > 3 and (fname != "")

@st.cache_data
def is_valid_last_name(lname):
    return len(lname) > 3 and (lname != "")

@st.cache_data
def is_valid_full_name(fullname):
    return len(fullname) > 6 and (fullname != "") and fullname.__contains__(" ")

@st.cache_data
def is_valid_age(age):
    if age.isnumeric():
        if (int(age) >= 18) and (int(age) <= 90):
            return True
        return False
    return False

@st.cache_data
def is_valid_phone(phone):
    if phone.isdigit() and len(phone) == 10:
        return True
    return False

@st.cache_data
def is_valid_patient_id(patient_id):
    if patient_id.startswith("PID_"):
        return True
    return False

@st.cache_data
def is_valid_operation_name(operation_name):
    return len(operation_name) > 5 and (operation_name != "")

# Function to delete doctor
def delete_doctor(phone_number):
    """Delete doctor by phone number"""
    try:
        # Implementation would depend on your Hospital class methods
        # Assuming you have a delete_doctor method in Hospital class
        if hasattr(hospital, 'delete_doctor'):
            return hospital.delete_doctor(phone_number)
        else:
            # Fallback: Remove from internal data structures
            doctors_df = hospital.get_all_doctors()
            updated_df = doctors_df[doctors_df['Phone'] != f"'{phone_number}'"]
            # You would need to implement a way to update the hospital's doctor list
            return True
    except Exception as e:
        st.error(f"Error deleting doctor: {str(e)}")
        return False

# Function to delete nurse
def delete_nurse(phone_number):
    """Delete nurse by phone number"""
    try:
        if hasattr(hospital, 'delete_nurse'):
            return hospital.delete_nurse(phone_number)
        else:
            nurses_df = hospital.get_all_nurses()
            updated_df = nurses_df[nurses_df['Phone'] != f"'{phone_number}'"]
            return True
    except Exception as e:
        st.error(f"Error deleting nurse: {str(e)}")
        return False

# Function to delete patient
def delete_patient(patient_id):
    """Delete patient by patient ID"""
    try:
        if hasattr(hospital, 'delete_patient'):
            return hospital.delete_patient(patient_id)
        else:
            patients_df = hospital.get_all_patients()
            updated_df = patients_df[patients_df['Patient_ID'] != patient_id]
            return True
    except Exception as e:
        st.error(f"Error deleting patient: {str(e)}")
        return False

header = st.container()
content = st.container()

with st.sidebar:
    st.title("LLM Digital Hospital ")
    page = option_menu(
        menu_title='Menu',
        options=['Doctor', "Nurse", "Patient", "Operation"],
        menu_icon='chat-text-fill',
        default_index=0,
        styles={
            "container": {"padding": "10!important", "background-color": '#000'},
            "icon": {"color": "white", "font-size": "22px"},
            "nav-link": {"color": "white", "font-size": "18px", "text-align": "left", "margin": "0px", },
            "nav-link-selected": {"background-color": "#0CB9B9"},
        }
    )
    st.write("***")

# Doctor Page
if page == 'Doctor':
    with header:
        st.title('Doctors 👨‍⚕️')
        doctor_option = option_menu(
            menu_title=None,
            options=["Add Doctor", 'Add Existing Nurse', 'Add Patient', "Doctors Info", "Edit Doctor", "Delete Doctor"],
            icons=[" "]*6,
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles=sub_options_style
        )

    with content:
        if doctor_option == "Add Doctor":
            st.text(f'Adding New Doctor'.title())
            with st.form('input'):
                [c1, c2] = st.columns(2)
                with c1:
                    first_name = st.text_input(label="First Name", placeholder="Name").strip()
                    age = st.text_input(label="Age", placeholder=23, max_chars=2).strip()
                    specialization = st.text_input(label="Specialization", placeholder="xxxxx").strip()

                with c2:
                    last_name = st.text_input(label="Last Name", placeholder="XXXXXX").strip()
                    phone = st.text_input(label="Phone Number", placeholder="10 digits", max_chars=11).strip()
                    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)
                    gender = st.radio("Gender", ["Male", "Female"])

                add_doctor = st.form_submit_button(label='Add Doctor')
                save_doctor = st.form_submit_button(label='Save Doctors')

                if add_doctor:
                    # Get The Output of Validation
                    flag_fname = is_valid_first_name(first_name)
                    flag_lname = is_valid_last_name(last_name)
                    flag_age = is_valid_age(age)
                    flag_phone = is_valid_phone(phone)

                    if flag_fname == False:
                        st.warning('First Name Must Be Greater Than 3 Characters!!')
                    if flag_lname == False:
                        st.warning('Last Name Must Be Greater Than 3 Characters!!')
                    if flag_age == False:
                        st.warning('Please Enter a Valid Age, Must Be A Numerical Value!!')
                    if flag_phone == False:
                        st.warning('Please Enter a Valid Phone Number!!')

                    if flag_fname and flag_lname and flag_age and flag_phone:
                        # Create Instance of Doctor Class
                        the_doctor = Doctor(f"{first_name} {last_name}", age, gender, f"'{phone}'", specialization)
                        
                        with st.spinner(text='Adding User…'):
                            sleep(1)
                            if hospital.add_doctor(the_doctor) == False:
                                st.warning(f'This Doctor With Phone Number ({phone}) Already Existed Before!!.')
                            else:
                                st.success(f'The Doctor With Name {first_name} {last_name}, Added Successfully.')
                    else:
                        st.error('Can Not Add This Doctor :x:.\nPlease, Check All Input Fields')

                elif save_doctor:
                    with st.spinner(text='Saving All Doctors...'):
                        sleep(1)
                        if hospital.save_doctor() == 0:
                            st.info('You Have To Add Doctor First In Correct Way, Then Save The Doctor Info.')
                        else:
                            st.success('Doctor(s) Saved Successfully :white_check_mark:')

        elif doctor_option == "Edit Doctor":
            st.text("Edit Doctor Information")
            
            # Get all doctors
            doctors_df = hospital.get_all_doctors()
            
            if not doctors_df.empty:
                # Select doctor to edit
                selected_doctor = st.selectbox(
                    "Select Doctor to Edit:",
                    options=doctors_df['Name'].tolist(),
                    key="edit_doctor_select"
                )
                
                if selected_doctor:
                    # Get doctor details
                    doctor_row = doctors_df[doctors_df['Name'] == selected_doctor].iloc[0]
                    
                    with st.form('edit_doctor_form'):
                        st.subheader(f"Editing: {selected_doctor}")
                        
                        [c1, c2] = st.columns(2)
                        with c1:
                            # Split name for editing
                            name_parts = selected_doctor.split()
                            first_name = st.text_input("First Name", value=name_parts[0] if len(name_parts) > 0 else "")
                            age = st.text_input("Age", value=str(doctor_row['Age']))
                            specialization = st.text_input("Specialization", value=str(doctor_row['Specialization']))
                        
                        with c2:
                            last_name = st.text_input("Last Name", value=name_parts[1] if len(name_parts) > 1 else "")
                            # Remove quotes from phone number for display
                            phone_display = str(doctor_row['Phone']).replace("'", "")
                            phone = st.text_input("Phone Number", value=phone_display, max_chars=11)
                            gender = st.selectbox("Gender", ["Male", "Female"],
                                                index=0 if doctor_row['Gender'] == 'Male' else 1)
                        
                        update_doctor = st.form_submit_button("Update Doctor")
                        
                        if update_doctor:
                            # Validate inputs
                            flag_fname = is_valid_first_name(first_name.strip())
                            flag_lname = is_valid_last_name(last_name.strip())
                            flag_age = is_valid_age(age.strip())
                            flag_phone = is_valid_phone(phone.strip())
                            
                            if all([flag_fname, flag_lname, flag_age, flag_phone]):
                                with st.spinner('Updating Doctor...'):
                                    sleep(1)
                                    # Here you would implement the update logic
                                    # This depends on your Hospital class having an update method
                                    st.success(f"Doctor {first_name} {last_name} updated successfully!")
                                    st.rerun()
                            else:
                                st.error("Please check all input fields")
            else:
                st.info("No doctors available to edit. Please add doctors first.")

        elif doctor_option == "Delete Doctor":
            st.text("Delete Doctor")
            
            # Get all doctors
            doctors_df = hospital.get_all_doctors()
            
            if not doctors_df.empty:
                st.warning("⚠️ Warning: This action cannot be undone!")
                
                # Display doctors in a table with delete buttons
                st.subheader("Select Doctor to Delete:")
                
                for index, row in doctors_df.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{row['Name']}**")
                    with col2:
                        st.write(f"Age: {row['Age']}")
                    with col3:
                        st.write(f"{row['Gender']}")
                    with col4:
                        st.write(f"Phone: {row['Phone']}")
                    with col5:
                        st.write(f"Specialization: {row['Specialization']}")
                    with col6:
                        phone_for_deletion = str(row['Phone']).replace("'", "")
                        if st.button(f"🗑️ Delete", key=f"delete_doctor_{index}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_doctor_{index}", False):
                                # Perform deletion
                                with st.spinner('Deleting Doctor...'):
                                    sleep(1)
                                    if delete_doctor(phone_for_deletion):
                                        st.success(f"Doctor {row['Name']} deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete doctor")
                            else:
                                st.session_state[f"confirm_delete_doctor_{index}"] = True
                                st.warning(f"Click delete again to confirm removal of {row['Name']}")
                    
                    st.divider()
            else:
                st.info("No doctors available to delete.")

        # Keep existing functionality for other doctor options
        elif doctor_option == "Add Existing Nurse":
            st.text(F"Adding Nurse To Doctor's Team".title())
            st.info("Be sure that the nurse or doctor must be in the hospital already!!")
            with st.form('adding_existing_nurse'):
                col_1, col_2 = st.columns(2)
                with col_1:
                    doctor_name = st.text_input(label="Doctor Name", placeholder="xxxxxxxxx").strip()
                    st.write("***")
                    nurse_name = st.text_input(label="Nurse Name", placeholder="xxxxxxxxxxx").strip()

                with col_2:
                    doctor_phone = st.text_input(label="Doctor Phone", placeholder="01020487XX", max_chars=10).strip()
                    st.write("***")
                    nurse_phone = st.text_input(label="Nurse Phone", placeholder="01520487XX", max_chars=10).strip()

                add_nurse_to_team = st.form_submit_button(label='Add Nurse To The Team')

                if add_nurse_to_team:
                    # Get The Output of Validation
                    flag_doctor_name = is_valid_full_name(doctor_name)
                    flag_doctor_phone = is_valid_phone(doctor_phone)
                    flag_nurse_name = is_valid_full_name(nurse_name)
                    flag_nurse_phone = is_valid_phone(nurse_phone)

                    if flag_doctor_name == False:
                        st.warning('Please Enter Right Doctor Name')
                    if flag_doctor_phone == False:
                        st.warning('Please Enter a Valid Phone Number!!')
                    if flag_nurse_name == False:
                        st.warning('Please Enter Right Nurse Name')
                    if flag_nurse_phone == False:
                        st.warning('Please Enter a Valid Phone Number!!')

                    if flag_doctor_name and flag_doctor_phone and flag_nurse_name and flag_nurse_phone:
                        # Create Empty Instance of Doctor Class
                        temp_doctor = Doctor.empty_Doctor_constructor()

                        with st.spinner(text='Adding Nurse To The Team…'):
                            sleep(1)
                            adding_nurse = temp_doctor.add_nurse_to_team(
                                doctor_name, doctor_phone, nurse_name, nurse_phone)
                            if adding_nurse == False:
                                st.error(f"Can Not Add This Nurse to {doctor_name}\'s Team :x:.\nPlease, Check All Input Fields")
                                st.warning(f"Ensure That!!  Doctor Phone Number belongs to Doctor {doctor_name}\n\
                                    And The Nurse Phone Number belongs to Nurse {nurse_name}")
                            elif adding_nurse == -1:
                                st.warning(f"Nurse ({nurse_name}) Already Existed In {doctor_name}'s Team.")
                            else:
                                st.success(f"Nurse ({nurse_name}) Added To {doctor_name}'s Team.")
                    else:
                        st.error('The Operation Corrupted :x:.\nPlease, Check All Input Fields')

        elif doctor_option == "Add Patient":
            st.text(F"Adding Patients To Doctor's List".title())
            st.info("Be sure that the Patient or Doctor Must Be in the hospital already!!")
            if len(hospital.get_all_doctors()) > 0 and len(hospital.get_all_patients()) > 0:
                with st.form('adding_existing_patient'):
                    col_1, col_2 = st.columns(2)
                    with col_1:
                        doctor_name = st.selectbox("Select Doctor Name:", options=(hospital.get_all_doctors()["Name"].tolist())).strip()
                        st.write("***")
                        patient_name = st.selectbox("Select Patient Name:", options=(hospital.get_all_patients()["Name"].tolist())).strip()

                    with col_2:
                        doctor_phone = st.text_input(label="Doctor Phone", placeholder="01020487XX", max_chars=10).strip()
                        st.write("***")
                        patient_id = st.selectbox("Select Patient ID:", options=(hospital.get_all_patients()["Patient_ID"].tolist())).strip()

                    add_patient_to_doctor = st.form_submit_button(label='Add Patient To The Doctor')

                    if add_patient_to_doctor:
                        # Get The Output of Validation
                        flag_doctor_name = is_valid_full_name(doctor_name)
                        flag_doctor_phone = is_valid_phone(doctor_phone)
                        flag_patient_name = is_valid_full_name(patient_name)

                        if flag_doctor_name == False:
                            st.warning('Please Enter Right Doctor Name')
                        if flag_doctor_phone == False:
                            st.warning('Please Enter a Valid Phone Number!!')
                        if flag_patient_name == False:
                            st.warning('Please Enter Right Patient Name')

                        if flag_doctor_name and flag_doctor_phone and flag_patient_name:
                            # Create Empty Instance of Doctor Class
                            temp_doctor = Doctor.empty_Doctor_constructor()

                            with st.spinner(text='Adding Patient To The Doctor…'):
                                sleep(1)
                                adding_patient = temp_doctor.add_patient_to_doctor(
                                    doctor_name, doctor_phone, patient_id, patient_name)
                                if adding_patient == False:
                                    st.error(f"Can Not Add This Patient to {doctor_name}\'s List :x:.\nPlease, Check All Input Fields")
                                    st.warning(f"Ensure That!! Doctor Phone Number belongs to Doctor {doctor_name}\n\
                                        And The Patient ID belongs to {patient_name}")
                                elif adding_patient == -1:
                                    st.warning(f"Patient ({patient_name}) Already Existed In {doctor_name}'s List.")
                                else:
                                    st.success(f"Patient ({patient_name}) Added To {doctor_name}'s List.")
                        else:
                            st.error('The Operation Corrupted :x:.\nPlease, Check All Input Fields')
            else:
                st.warning("Please You Have To Add Doctors & Patients First To Hospital!!!")
                
        elif doctor_option == "Doctors Info":
            st.text(f'All Doctors in "{hospital.name} Hospital" 🏥'.title())
            df = hospital.get_all_doctors()
            st.table(df)

# Nurse Page
elif page == 'Nurse':
    with header:
        st.title('Nurses 👩‍⚕️'.title())
        nurse_option = option_menu(
            menu_title=None,
            options=["Add Nurse", 'Nurses Info', 'Edit Nurse', 'Delete Nurse'],
            icons=[" "]*4,
            default_index=0,
            orientation="horizontal",
            styles=sub_options_style
        )

    with content:
        if nurse_option == "Add Nurse":
            st.text(f'Adding New Nurse'.title())
            with st.form("Adding_New_Nurse"):
                [c1, c2] = st.columns(2)
                with c1:
                    first_name = st.text_input(label="First Name", placeholder="xxxxxxxxx").strip()
                    age = st.text_input(label="Age", placeholder=35, max_chars=2).strip()
                    shift_type = st.selectbox(label="Shift Type", options=["Day Shift", "Night Shift"])

                with c2:
                    last_name = st.text_input(label="Last Name", placeholder="xxxxxxxxx").strip()
                    phone = st.text_input(label="Phone Number", placeholder="0157896xxx", max_chars=10).strip()
                    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)
                    gender = st.radio("Gender", ["Male", "Female"])

                add_nurse = st.form_submit_button(label='Add Nurse')
                save_nurse = st.form_submit_button(label='Save Nurse')

                if add_nurse:
                    # Get The Output of Validation
                    flag_fname = is_valid_first_name(first_name)
                    flag_lname = is_valid_last_name(last_name)
                    flag_age = is_valid_age(age)
                    flag_phone = is_valid_phone(phone)

                    if flag_fname == False:
                        st.warning('First Name Must Be Greater Than 3 Characters!!')
                    if flag_lname == False:
                        st.warning('Last Name Must Be Greater Than 3 Characters!!')
                    if flag_age == False:
                        st.warning('Please Enter a Valid Age, Must Be A Numerical Value!!')
                    if flag_phone == False:
                        st.warning('Please Enter a Valid Phone Number !!')

                    if flag_fname and flag_lname and flag_age and flag_phone:
                        # Create Instance of Nurse Class
                        the_nurse = Nurse(f"{first_name} {last_name}", age, gender, f"'{phone}'", shift_type)

                        with st.spinner(text='Adding Nurse....'):
                            sleep(1)
                            if hospital.add_nurse(the_nurse) == False:
                                st.warning(f'This Nurse With Phone Number ({phone}) Already Existed Before!!.')
                            else:
                                st.success(f'The Nurse With Name {first_name} {last_name}, Added Successfully.')
                    else:
                        st.error('Can Not Add This Nurse :x:.\nPlease, Check All Input Fields')

                elif save_nurse:
                    with st.spinner(text='Saving All Nurses...'):
                        sleep(1)
                        if hospital.save_nurse() == 0:
                            st.info('You Have To Add Nurse First In Correct Way, Then Save The Nurse Info.')
                        else:
                            st.success('Nurse(s) Saved Successfully :white_check_mark:')

        elif nurse_option == "Edit Nurse":
            st.text("Edit Nurse Information")
            
            nurses_df = hospital.get_all_nurses()
            
            if not nurses_df.empty:
                selected_nurse = st.selectbox(
                    "Select Nurse to Edit:",
                    options=nurses_df['Name'].tolist(),
                    key="edit_nurse_select"
                )
                
                if selected_nurse:
                    nurse_row = nurses_df[nurses_df['Name'] == selected_nurse].iloc[0]
                    
                    with st.form('edit_nurse_form'):
                        st.subheader(f"Editing: {selected_nurse}")
                        
                        [c1, c2] = st.columns(2)
                        with c1:
                            name_parts = selected_nurse.split()
                            first_name = st.text_input("First Name", value=name_parts[0] if len(name_parts) > 0 else "")
                            age = st.text_input("Age", value=str(nurse_row['Age']))
                            shift_type = st.selectbox("Shift Type", ["Day Shift", "Night Shift"],
                                                    index=0 if nurse_row['Shift_Type'] == 'Day Shift' else 1)
                        
                        with c2:
                            last_name = st.text_input("Last Name", value=name_parts[1] if len(name_parts) > 1 else "")
                            phone_display = str(nurse_row['Phone']).replace("'", "")
                            phone = st.text_input("Phone Number", value=phone_display, max_chars=11)
                            gender = st.selectbox("Gender", ["Male", "Female"],
                                                index=0 if nurse_row['Gender'] == 'Male' else 1)
                        
                        update_nurse = st.form_submit_button("Update Nurse")
                        
                        if update_nurse:
                            flag_fname = is_valid_first_name(first_name.strip())
                            flag_lname = is_valid_last_name(last_name.strip())
                            flag_age = is_valid_age(age.strip())
                            flag_phone = is_valid_phone(phone.strip())
                            
                            if all([flag_fname, flag_lname, flag_age, flag_phone]):
                                with st.spinner('Updating Nurse...'):
                                    sleep(1)
                                    st.success(f"Nurse {first_name} {last_name} updated successfully!")
                                    st.rerun()
                            else:
                                st.error("Please check all input fields")
            else:
                st.info("No nurses available to edit. Please add nurses first.")

        elif nurse_option == "Delete Nurse":
            st.text("Delete Nurse")
            
            nurses_df = hospital.get_all_nurses()
            
            if not nurses_df.empty:
                st.warning("⚠️ Warning: This action cannot be undone!")
                
                st.subheader("Select Nurse to Delete:")
                
                for index, row in nurses_df.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{row['Name']}**")
                    with col2:
                        st.write(f"Age: {row['Age']}")
                    with col3:
                        st.write(f"{row['Gender']}")
                    with col4:
                        st.write(f"Phone: {row['Phone']}")
                    with col5:
                        st.write(f"Shift: {row['Shift_Type']}")
                    with col6:
                        phone_for_deletion = str(row['Phone']).replace("'", "")
                        if st.button(f"🗑️ Delete", key=f"delete_nurse_{index}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_nurse_{index}", False):
                                with st.spinner('Deleting Nurse...'):
                                    sleep(1)
                                    if delete_nurse(phone_for_deletion):
                                        st.success(f"Nurse {row['Name']} deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete nurse")
                            else:
                                st.session_state[f"confirm_delete_nurse_{index}"] = True
                                st.warning(f"Click delete again to confirm removal of {row['Name']}")
                    
                    st.divider()
            else:
                st.info("No nurses available to delete.")

        elif nurse_option == "Nurses Info":
            st.text(f'All Nurses in "{hospital.name} Hospital" 🏥'.title())
            df = hospital.get_all_nurses()
            st.table(df)

# Patient Page
elif page == "Patient":
    with header:
        st.title('Patients 🤒'.title())
        patient_option = option_menu(
            menu_title=None,
            options=["Add Patient", 'Assigning to Doctor', 'Patients Info', 'Edit Patient', 'Delete Patient'],
            icons=[" "]*5,
            default_index=0,
            orientation="horizontal",
            styles=sub_options_style
        )

    with content:
        if patient_option == "Add Patient":
            st.text(f'Adding New Patient'.title())
            with st.form("Adding_New_patient"):
                [c1, c2] = st.columns(2)
                with c1:
                    first_name = st.text_input(label="First Name", placeholder="xxxxxxxxx").strip()
                    age = st.text_input(label="Age", placeholder=35, max_chars=2).strip()

                with c2:
                    last_name = st.text_input(label="Last Name", placeholder="xxxxxxxxxx").strip()
                    phone = st.text_input(label="Phone Number", placeholder="0117896xxxx", max_chars=11).strip()
                
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)
                gender = st.selectbox("Gender", ["Male", "Female"])

                add_patient = st.form_submit_button(label='Add Patient')
                save_patient = st.form_submit_button(label='Save Patient')

                if add_patient:
                    # Get The Output of Validation
                    flag_fname = is_valid_first_name(first_name)
                    flag_lname = is_valid_last_name(last_name)
                    flag_age = is_valid_age(age)
                    flag_phone = is_valid_phone(phone)

                    if flag_fname == False:
                        st.warning('First Name Must Be Greater Than 3 Characters!!')
                    if flag_lname == False:
                        st.warning('Last Name Must Be Greater Than 3 Characters!!')
                    if flag_age == False:
                        st.warning('Please Enter a Valid Age, Must Be A Numerical Value!!')
                    if flag_phone == False:
                        st.warning('Please Enter a Valid Phone Number Starts With [010/ 012/ 015/ 011]!')

                    if flag_fname and flag_lname and flag_age and flag_phone:
                        # Create Instance of Patient Class
                        the_patient = Patient(f"{first_name} {last_name}", age, gender, f"'{phone}'")

                        with st.spinner(text='Adding Patient....'):
                            sleep(1)
                            if hospital.add_patient(the_patient) == False:
                                st.warning(f'This Patient With Phone Number ({phone}) Already Existed Before!!.')
                            else:
                                st.success(f'The Patient With Name {first_name} {last_name}, Added Successfully.')
                                st.success(f'Patient ID {the_patient.get_patient_id()}')
                    else:
                        st.error('Can Not Add This Patient :x:.\nPlease, Check All Input Fields')

                elif save_patient:
                    with st.spinner(text='Saving All Patients...'):
                        sleep(1)
                        if hospital.save_patient() == 0:
                            st.info('You Have To Add Patient Data In Correct Way, Then Save The Patient Info.')
                        else:
                            st.success('Patient(s) Saved Successfully :white_check_mark:')

        elif patient_option == "Assigning to Doctor":
            if len(hospital.get_all_doctors()) > 0 and len(hospital.get_all_patients()) > 0:
                st.text(F'Assigning To Doctor'.title())

                with st.form('assign_patient_to_dr'):
                    patient_id = st.selectbox("Select Patient ID:", options=(
                        hospital.get_all_patients()["Patient_ID"].tolist())).strip()
                    st.write("***")
                    c1, c2 = st.columns(2)
                    with c1:
                        doctor_name = st.selectbox("Select Doctor Name:", options=(hospital.get_all_doctors()["Name"].tolist())).strip()

                    with c2:
                        doctor_phone = st.text_input(label="Doctor Phone", placeholder="01020487XXX", max_chars=11).strip()

                    assign_doctor = st.form_submit_button(label='Assign Patient to Doctor')

                    if assign_doctor:
                        flag_doctor_name = is_valid_full_name(doctor_name)

                        if flag_doctor_name == False:
                            st.warning('Choose Doctor From List !..')

                        if flag_doctor_name:
                            with st.spinner(text='Assigning Patient to Doctor…'):
                                # Get Patient Name
                                patient_df = hospital.get_all_patients()
                                filt = (patient_df["Patient_ID"] == patient_id)
                                patient_name = patient_df.loc[filt]["Name"].values[0]

                                temp_patient = Patient.empty_patient_constructor()

                                assigning_doctor = temp_patient.assign_doctor_to_pateint(
                                    doctor_name, doctor_phone, patient_id, patient_name)

                                sleep(1)
                                if assigning_doctor == False:
                                    st.error(f"Can Not Assign Doctor ({doctor_name}) to Patient ({patient_id}):x:.\nPlease, Check All Input Fields")
                                    st.warning(f"Ensure That!! Doctor Phone Number belongs to Doctor {doctor_name}\n\
                                            And The Patient ID {patient_id}")
                                elif assigning_doctor == -1:
                                    st.warning(f"Patient ({patient_id}) Already Existed In {doctor_name}'s List.")
                                else:
                                    st.success(f"Patient ({patient_id}) Added To {doctor_name}'s List.")
            else:
                st.warning("Please Add Doctors & Patients First To Hospital!!\nIn Order To Assign Doctors")

        elif patient_option == "Edit Patient":
            st.text("Edit Patient Information")
            
            patients_df = hospital.get_all_patients()
            
            if not patients_df.empty:
                selected_patient = st.selectbox(
                    "Select Patient to Edit:",
                    options=patients_df['Name'].tolist(),
                    key="edit_patient_select"
                )
                
                if selected_patient:
                    patient_row = patients_df[patients_df['Name'] == selected_patient].iloc[0]
                    
                    with st.form('edit_patient_form'):
                        st.subheader(f"Editing: {selected_patient}")
                        st.info(f"Patient ID: {patient_row['Patient_ID']}")
                        
                        [c1, c2] = st.columns(2)
                        with c1:
                            name_parts = selected_patient.split()
                            first_name = st.text_input("First Name", value=name_parts[0] if len(name_parts) > 0 else "")
                            age = st.text_input("Age", value=str(patient_row['Age']))
                        
                        with c2:
                            last_name = st.text_input("Last Name", value=name_parts[1] if len(name_parts) > 1 else "")
                            phone_display = str(patient_row['Phone']).replace("'", "")
                            phone = st.text_input("Phone Number", value=phone_display, max_chars=11)
                        
                        gender = st.selectbox("Gender", ["Male", "Female"],
                                            index=0 if patient_row['Gender'] == 'Male' else 1)
                        
                        update_patient = st.form_submit_button("Update Patient")
                        
                        if update_patient:
                            flag_fname = is_valid_first_name(first_name.strip())
                            flag_lname = is_valid_last_name(last_name.strip())
                            flag_age = is_valid_age(age.strip())
                            flag_phone = is_valid_phone(phone.strip())
                            
                            if all([flag_fname, flag_lname, flag_age, flag_phone]):
                                with st.spinner('Updating Patient...'):
                                    sleep(1)
                                    st.success(f"Patient {first_name} {last_name} updated successfully!")
                                    st.rerun()
                            else:
                                st.error("Please check all input fields")
            else:
                st.info("No patients available to edit. Please add patients first.")

        elif patient_option == "Delete Patient":
            st.text("Delete Patient")
            
            patients_df = hospital.get_all_patients()
            
            if not patients_df.empty:
                st.warning("⚠️ Warning: This action cannot be undone!")
                
                st.subheader("Select Patient to Delete:")
                
                for index, row in patients_df.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 2, 1])
                    
                    with col1:
                        st.write(f"**{row['Name']}**")
                    with col2:
                        st.write(f"ID: {row['Patient_ID']}")
                    with col3:
                        st.write(f"Age: {row['Age']}")
                    with col4:
                        st.write(f"{row['Gender']}")
                    with col5:
                        st.write(f"Phone: {row['Phone']}")
                    with col6:
                        patient_id = row['Patient_ID']
                        if st.button(f"🗑️ Delete", key=f"delete_patient_{index}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_patient_{index}", False):
                                with st.spinner('Deleting Patient...'):
                                    sleep(1)
                                    if delete_patient(patient_id):
                                        st.success(f"Patient {row['Name']} deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete patient")
                            else:
                                st.session_state[f"confirm_delete_patient_{index}"] = True
                                st.warning(f"Click delete again to confirm removal of {row['Name']}")
                    
                    st.divider()
            else:
                st.info("No patients available to delete.")

        elif patient_option == "Patients Info":
            st.text(f'All Patients in "{hospital.name} Hospital" 🏥'.title())
            df = hospital.get_all_patients()
            st.table(df)

# Operation Page
elif page == "Operation":
    with header:
        st.title('Operations 💉🩺'.title())
        operation_option = option_menu(
            menu_title=None,
            options=["Add Operation", 'All Operations', 'Edit Operation', 'Delete Operation'],
            icons=[" "]*4,
            default_index=0,
            orientation="horizontal",
            styles=sub_options_style
        )

    with content:
        temp_operation = Operation.empty_operation_constructor()
        
        if operation_option == "Add Operation":
            if len(hospital.get_all_doctors()) > 0 and len(hospital.get_all_nurses()) > 0 and len(hospital.get_all_patients()) > 0:
                with st.form('operation_form'):
                    operation_name = st.text_input(label="Operation Name 💉", placeholder="operation of heart").strip()
                    st.write("***")

                    [c1, c2] = st.columns(2)
                    with c1:
                        operation_time = st.time_input('Operation Time 🕗', datetime.time(3, 30))
                        st.write("***")
                        surgeon_name = st.selectbox(label="Surgeon Name 👨‍⚕️", options=hospital.get_all_doctors()["Name"].tolist()).strip()

                    with c2:
                        operation_date = st.date_input("Operation Date 📅", datetime.date(2024, 1, 3))
                        st.write("***")
                        nurse_name = st.selectbox(label="Nurse Name 👩‍⚕️", options=hospital.get_all_nurses()["Name"].tolist()).strip()

                    st.write("\n\n")

                    add_nurse_to_operatin = st.form_submit_button(label='Add Nurse to Operation')
                    add_operation = st.form_submit_button(label='Add Operation')

                    if add_nurse_to_operatin:
                        if temp_operation.add_nurse(nurse_name) == 0:
                            st.warning(f'Nurse {nurse_name} Already In This Operation!!')
                        else:
                            st.info(f"Nurse {nurse_name} Added Successfully To This Operation..")

                    if add_operation:
                        flag_operation_name = is_valid_operation_name(operation_name)

                        if flag_operation_name == False:
                            st.warning('The Operation Name Must Be Valid')

                        if flag_operation_name:
                            with st.spinner(text='Saving The Operation To Database…'):
                                temp_operation.set_operation_id(operation_name, surgeon_name)
                                temp_operation.set_operation_name(operation_name)
                                temp_operation.set_operation_date(operation_date)
                                temp_operation.set_operation_time(operation_time)
                                temp_operation.set_operation_surgeon(surgeon_name)
                                sleep(1.5)
                                temp_operation.create_operation()
                                st.success('Surgery Operation Saved Successfully...')
                        else:
                            st.error('Please Ensure You Write All Fields in Correct Way!!.')
            else:
                st.warning("To Add Operation!! Of course You have To Add Doctors and Patients and Nurses To The Hospital!!")

        elif operation_option == "Edit Operation":
            st.text("Edit Operation Information")
            
            operations_df = temp_operation.get_all_operation()
            
            if not operations_df.empty:
                # Assuming operations have some identifier like Operation_ID
                if 'Operation_ID' in operations_df.columns:
                    selected_operation = st.selectbox(
                        "Select Operation to Edit:",
                        options=operations_df['Operation_ID'].tolist(),
                        key="edit_operation_select"
                    )
                else:
                    # Fallback to operation name if no ID column
                    selected_operation = st.selectbox(
                        "Select Operation to Edit:",
                        options=operations_df.index.tolist(),
                        key="edit_operation_select"
                    )
                
                if selected_operation is not None:
                    if 'Operation_ID' in operations_df.columns:
                        operation_row = operations_df[operations_df['Operation_ID'] == selected_operation].iloc[0]
                    else:
                        operation_row = operations_df.iloc[selected_operation]
                    
                    with st.form('edit_operation_form'):
                        st.subheader(f"Editing Operation")
                        
                        operation_name = st.text_input("Operation Name", value=str(operation_row.get('Operation_Name', '')))
                        
                        [c1, c2] = st.columns(2)
                        with c1:
                            # Handle date conversion
                            try:
                                current_date = datetime.datetime.strptime(str(operation_row.get('Operation_Date', '2024-01-03')), '%Y-%m-%d').date()
                            except:
                                current_date = datetime.date(2024, 1, 3)
                            
                            operation_date = st.date_input("Operation Date", value=current_date)
                            
                            if len(hospital.get_all_doctors()) > 0:
                                surgeon_options = hospital.get_all_doctors()["Name"].tolist()
                                current_surgeon = str(operation_row.get('Surgeon_Name', ''))
                                surgeon_index = surgeon_options.index(current_surgeon) if current_surgeon in surgeon_options else 0
                                surgeon_name = st.selectbox("Surgeon Name", options=surgeon_options, index=surgeon_index)
                        
                        with c2:
                            # Handle time conversion
                            try:
                                current_time = datetime.datetime.strptime(str(operation_row.get('Operation_Time', '03:30:00')), '%H:%M:%S').time()
                            except:
                                current_time = datetime.time(3, 30)
                            
                            operation_time = st.time_input("Operation Time", value=current_time)
                            
                            if len(hospital.get_all_nurses()) > 0:
                                nurse_options = hospital.get_all_nurses()["Name"].tolist()
                                # Note: This assumes single nurse per operation, adjust as needed
                                nurse_name = st.selectbox("Primary Nurse", options=nurse_options)
                        
                        update_operation = st.form_submit_button("Update Operation")
                        
                        if update_operation:
                            flag_operation_name = is_valid_operation_name(operation_name.strip())
                            
                            if flag_operation_name:
                                with st.spinner('Updating Operation...'):
                                    sleep(1)
                                    # Here you would implement the update logic
                                    st.success(f"Operation updated successfully!")
                                    st.rerun()
                            else:
                                st.error("Please check the operation name")
            else:
                st.info("No operations available to edit. Please add operations first.")

        elif operation_option == "Delete Operation":
            st.text("Delete Operation")
            
            operations_df = temp_operation.get_all_operation()
            
            if not operations_df.empty:
                st.warning("⚠️ Warning: This action cannot be undone!")
                
                st.subheader("Select Operation to Delete:")
                
                for index, row in operations_df.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{row.get('Operation_Name', 'N/A')}**")
                    with col2:
                        st.write(f"Date: {row.get('Operation_Date', 'N/A')}")
                    with col3:
                        st.write(f"Time: {row.get('Operation_Time', 'N/A')}")
                    with col4:
                        st.write(f"Surgeon: {row.get('Surgeon_Name', 'N/A')}")
                    with col5:
                        operation_id = row.get('Operation_ID', index)
                        if st.button(f"🗑️ Delete", key=f"delete_operation_{index}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_operation_{index}", False):
                                with st.spinner('Deleting Operation...'):
                                    sleep(1)
                                    # Implement deletion logic here
                                    st.success(f"Operation deleted successfully!")
                                    st.rerun()
                            else:
                                st.session_state[f"confirm_delete_operation_{index}"] = True
                                st.warning(f"Click delete again to confirm removal of this operation")
                    
                    st.divider()
            else:
                st.info("No operations available to delete.")

        elif operation_option == "All Operations":
            st.text(f'All Operations in "{hospital.name} Hospital" 🏥'.title())
            df = temp_operation.get_all_operation()
            st.table(df)
