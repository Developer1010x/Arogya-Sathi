import streamlit as st
import datetime
import pandas as pd
import base64
from io import BytesIO
import sys
import os
import json
from datetime import datetime

# Add the current directory to the path to import the ll module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from llm import ask_llm

def create_prescription_pdf(patient_data, prescription_data, observations, test_data=[]):
    """Generate a PDF of the prescription and return as base64 encoded string"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Add title
        title_style = styles["Heading1"]
        title_style.alignment = 1  # Center alignment
        elements.append(Paragraph("Medical Prescription", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Add doctor information
        doctor_style = styles["Normal"]
        doctor_style.alignment = 2  # Right alignment
        elements.append(Paragraph(f"Dr. {patient_data['doctor_name']}", doctor_style))
        elements.append(Paragraph(f"License: {patient_data['doctor_license']}", doctor_style))
        elements.append(Paragraph(f"Date: {patient_data['date']}", doctor_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Add patient information
        patient_style = styles["Normal"]
        elements.append(Paragraph(f"Patient: {patient_data['patient_name']}", patient_style))
        elements.append(Paragraph(f"Age: {patient_data['patient_age']} | Gender: {patient_data['patient_gender']}", patient_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Add observations
        obs_style = styles["Heading3"]
        elements.append(Paragraph("Observations:", obs_style))
        elements.append(Paragraph(observations, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Add prescription table
        elements.append(Paragraph("Prescribed Medications:", obs_style))
        
        data = [["Medication", "Dosage", "Timing", "Times/Day"]]
        for med in prescription_data:
            data.append([
                med["medicine_name"],
                med["dosage"],
                med["timing"],
                med["frequency"]
            ])
        
        table = Table(data, colWidths=[2.0*inch, 1.5*inch, 1.5*inch, 1.0*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Add recommended tests table if there are any tests
        if test_data:
            elements.append(Paragraph("Recommended Tests:", obs_style))
            
            test_table_data = [["Test Name", "Instructions/Notes"]]
            for test in test_data:
                test_table_data.append([
                    test["test_name"],
                    test["notes"]
                ])
            
            test_table = Table(test_table_data, colWidths=[3.0*inch, 3.0*inch])
            test_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(test_table)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Add signature
        signature_style = styles["Normal"]
        signature_style.alignment = 2  # Right alignment
        elements.append(Paragraph("Doctor's Signature:", signature_style))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("___________________", signature_style))
        elements.append(Paragraph(f"Dr. {patient_data['doctor_name']}", signature_style))
        
        # Build PDF
        doc.build(elements)
        pdf_content = buffer.getvalue()
        
        # Encode as base64
        encoded = base64.b64encode(pdf_content).decode()
        return encoded
    except ImportError:
        st.error("ReportLab is required for PDF generation. Install it with 'pip install reportlab'.")
        return None

def get_llm_suggestions(prompt):
    """Get prescription suggestions from LLM"""
    try:
        response = ask_llm(prompt)
        return response
    except Exception as e:
        st.error(f"Error connecting to LLM: {e}")
        return "Unable to connect to the LLM service. Please check your configuration."

def main():
    st.set_page_config(page_title="Medical Prescription Generator", layout="wide")
    
    st.title("Medical Prescription Generator")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Create Prescription", "LLM Assistant", "View Example"])
    
    with tab1:
        st.header("Generate a New Prescription")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Patient Information")
            patient_name = st.text_input("Patient Name")
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                patient_age = st.number_input("Age", min_value=0, max_value=120, value=30)
            with col1_2:
                patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        with col2:
            st.subheader("Doctor Information")
            doctor_name = st.text_input("Doctor Name")
            doctor_license = st.text_input("License Number")
            prescription_date = st.date_input("Date", datetime.now())
        
        st.subheader("Observations")
        observations = st.text_area("Clinical Observations", height=150)
        
        st.subheader("Prescriptions")
        
        # Create a container for dynamic medications
        medications_container = st.container()
        
        # Store medications and tests in session state
        if 'medications' not in st.session_state:
            st.session_state.medications = [{"id": 0}]
            
        if 'tests' not in st.session_state:
            st.session_state.tests = [{"id": 0}]
        
        # Function to add new medication
        def add_medication():
            last_id = st.session_state.medications[-1]["id"]
            st.session_state.medications.append({"id": last_id + 1})
        
        # Function to remove medication
        def remove_medication(med_id):
            st.session_state.medications = [med for med in st.session_state.medications if med["id"] != med_id]
            if not st.session_state.medications:
                st.session_state.medications = [{"id": 0}]
                
        # Function to add new test
        def add_test():
            last_id = st.session_state.tests[-1]["id"]
            st.session_state.tests.append({"id": last_id + 1})
        
        # Function to remove test
        def remove_test(test_id):
            st.session_state.tests = [test for test in st.session_state.tests if test["id"] != test_id]
            if not st.session_state.tests:
                st.session_state.tests = [{"id": 0}]
        
        # Display existing medications
        with medications_container:
            for i, med in enumerate(st.session_state.medications):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    med_key = f"med_name_{med['id']}"
                    if med_key not in st.session_state:
                        st.session_state[med_key] = ""
                    med["medicine_name"] = st.text_input("Medicine Name", key=med_key, value=st.session_state[med_key])
                
                with col2:
                    dosage_key = f"dosage_{med['id']}"
                    if dosage_key not in st.session_state:
                        st.session_state[dosage_key] = ""
                    med["dosage"] = st.text_input("Dosage", key=dosage_key, value=st.session_state[dosage_key])
                
                with col3:
                    timing_key = f"timing_{med['id']}"
                    if timing_key not in st.session_state:
                        st.session_state[timing_key] = "After Food"
                    med["timing"] = st.selectbox("Timing", ["After Food", "Before Food", "With Food"], key=timing_key, index=["After Food", "Before Food", "With Food"].index(st.session_state[timing_key]))
                
                with col4:
                    freq_key = f"freq_{med['id']}"
                    if freq_key not in st.session_state:
                        st.session_state[freq_key] = "1"
                    med["frequency"] = st.selectbox("Times/Day", ["1", "2", "3", "4", "SOS"], key=freq_key, index=["1", "2", "3", "4", "SOS"].index(st.session_state[freq_key]))
                
                with col5:
                    if len(st.session_state.medications) > 1:
                        st.button("Remove", key=f"remove_{med['id']}", on_click=remove_medication, args=(med["id"],))
        
        st.button("Add More Medications", on_click=add_medication)
        
        # Recommended Tests Section
        st.subheader("Recommended Tests")
        
        # Display existing tests
        tests_container = st.container()
        
        with tests_container:
            for i, test in enumerate(st.session_state.tests):
                col1, col2, col3 = st.columns([4, 3, 1])
                
                with col1:
                    test_name_key = f"test_name_{test['id']}"
                    if test_name_key not in st.session_state:
                        st.session_state[test_name_key] = ""
                    test["test_name"] = st.text_input("Test Name", key=test_name_key, value=st.session_state[test_name_key])
                
                with col2:
                    test_notes_key = f"test_notes_{test['id']}"
                    if test_notes_key not in st.session_state:
                        st.session_state[test_notes_key] = ""
                    test["notes"] = st.text_input("Notes/Instructions", key=test_notes_key, value=st.session_state[test_notes_key])
                
                with col3:
                    if len(st.session_state.tests) > 1:
                        st.button("Remove", key=f"remove_test_{test['id']}", on_click=remove_test, args=(test["id"],))
        
        st.button("Add More Tests", on_click=add_test)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Prescription"):
                if not patient_name or not doctor_name:
                    st.error("Please fill in patient and doctor information")
                else:
                    # Get medications from session state
                    prescription_data = []
                    for med in st.session_state.medications:
                        if med.get("medicine_name"):
                            prescription_data.append({
                                "medicine_name": med.get("medicine_name", ""),
                                "dosage": med.get("dosage", ""),
                                "timing": med.get("timing", "After Food"),
                                "frequency": med.get("frequency", "1")
                            })
                    
                    if not prescription_data:
                        st.error("Please add at least one medication")
                    else:
                                                        # Collect patient data
                        patient_data = {
                            "patient_name": patient_name,
                            "patient_age": patient_age,
                            "patient_gender": patient_gender,
                            "doctor_name": doctor_name,
                            "doctor_license": doctor_license,
                            "date": prescription_date.strftime("%Y-%m-%d")
                        }
                        
                        # Collect test data
                        test_data = []
                        for test in st.session_state.tests:
                            if test.get("test_name"):
                                test_data.append({
                                    "test_name": test.get("test_name", ""),
                                    "notes": test.get("notes", "")
                                })
                        
                        try:
                            # Generate PDF
                            pdf_content = create_prescription_pdf(patient_data, prescription_data, observations, test_data)
                            
                            if pdf_content:
                                # Save to session state
                                st.session_state.pdf_content = pdf_content
                                st.session_state.patient_data = patient_data
                                st.session_state.prescription_data = prescription_data
                                st.session_state.observations = observations
                                st.session_state.test_data = test_data
                                
                                # Display download button
                                st.success("Prescription generated successfully!")
                                st.download_button(
                                    label="Download Prescription",
                                    data=base64.b64decode(pdf_content),
                                    file_name=f"prescription_{patient_name.replace(' ', '_')}_{prescription_date}.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"Error generating prescription: {e}")
        
        with col2:
            if st.button("Clear Form"):
                # Reset session state
                st.session_state.medications = [{"id": 0}]
                st.session_state.tests = [{"id": 0}]
                for key in list(st.session_state.keys()):
                    if key.startswith(("med_name_", "dosage_", "timing_", "freq_", "test_name_", "test_notes_")):
                        del st.session_state[key]
                st.experimental_rerun()

    with tab2:
        st.header("LLM Medical Assistant")
        
        with st.expander("About this feature"):
            st.write("""
            The LLM Medical Assistant can help you with:
            - Suggesting medications based on symptoms
            - Providing dosage information
            - Generating observation notes
            
            Please note: This is for assistance only. and under testing in current 
            """)
        
        query_type = st.selectbox("What would you like help with?", [
            "Suggest medications for symptoms",
            "Generate observation notes",
            "Get dosage information",
            "Recommend tests based on symptoms"
        ])
        
        if query_type == "Suggest medications for symptoms":
            symptoms = st.text_area("Describe the patient's symptoms", height=100)
            if st.button("Get Suggestions"):
                if symptoms:
                    with st.spinner("Consulting LLM..."):
                        prompt = f"""
                        As a medical professional, suggest appropriate medications for a patient with the following symptoms:
                        {symptoms}
                        
                        Please format your response as a list of medications with dosages, timing, and frequency.
                        """
                        suggestions = get_llm_suggestions(prompt)
                        st.write("### Suggested Medications")
                        st.write(suggestions)
                else:
                    st.error("Please enter symptoms")
        
        elif query_type == "Generate observation notes":
            patient_details = st.text_area("Enter patient details and examination findings", height=100)
            if st.button("Generate Observations"):
                if patient_details:
                    with st.spinner("Generating observations..."):
                        prompt = f"""
                        Based on these patient details and examination findings, generate a comprehensive clinical observation note:
                        {patient_details}
                        
                        Format the observation professionally as it would appear in a medical chart.
                        """
                        observations = get_llm_suggestions(prompt)
                        st.write("### Generated Observations")
                        st.write(observations)
                else:
                    st.error("Please enter patient details")
        
        elif query_type == "Get dosage information":
            medication = st.text_input("Enter medication name")
            if st.button("Get Dosage Information"):
                if medication:
                    with st.spinner("Retrieving information..."):
                        prompt = f"""
                        Provide standard dosage information for {medication}, including:
                        - Typical adult dosage
                        - Pediatric dosage if applicable
                        - Timing (before/after food)
                        - Common frequency
                        - Precautions or side effects to note
                        """
                        dosage_info = get_llm_suggestions(prompt)
                        st.write("### Dosage Information")
                        st.write(dosage_info)
                else:
                    st.error("Please enter a medication name")
                    
        elif query_type == "Recommend tests based on symptoms":
            symptoms = st.text_area("Describe the patient's symptoms and condition", height=100)
            if st.button("Get Test Recommendations"):
                if symptoms:
                    with st.spinner("Consulting LLM..."):
                        prompt = f"""
                        As a medical professional, recommend appropriate diagnostic tests for a patient with the following symptoms and condition:
                        {symptoms}
                        
                        Please format your response as a list of recommended tests with brief explanations for why each test is recommended.
                        """
                        test_recommendations = get_llm_suggestions(prompt)
                        st.write("### Recommended Tests")
                        st.write(test_recommendations)
                else:
                    st.error("Please enter patient symptoms and condition")

    with tab3:
        st.header("Example Prescription")
        
        st.write("""
        This tab displays an example prescription to help you understand the format.
        """)
        
        # Sample data
        sample_patient = {
            "patient_name": "John Doe",
            "patient_age": 45,
            "patient_gender": "Male",
            "doctor_name": "Sarah Johnson",
            "doctor_license": "MD12345",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        sample_meds = [
            {
                "medicine_name": "Amoxicillin",
                "dosage": "500mg",
                "timing": "After Food",
                "frequency": "3"
            },
            {
                "medicine_name": "Paracetamol",
                "dosage": "650mg",
                "timing": "As needed",
                "frequency": "SOS"
            }
        ]
        
        sample_tests = [
            {
                "test_name": "Complete Blood Count",
                "notes": "Fasting, morning sample"
            },
            {
                "test_name": "Chest X-ray",
                "notes": "PA view"
            }
        ]
        
        sample_observations = "Patient presents with symptoms of upper respiratory tract infection including sore throat, mild fever (100.2°F), and nasal congestion for the past 3 days. No shortness of breath or chest pain. Throat appears red with mild inflammation. Lungs clear on auscultation."
        
        # Display sample prescription
        st.subheader("Sample Prescription Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Patient Information**")
            st.write(f"Name: {sample_patient['patient_name']}")
            st.write(f"Age: {sample_patient['patient_age']}")
            st.write(f"Gender: {sample_patient['patient_gender']}")
        
        with col2:
            st.write("**Doctor Information**")
            st.write(f"Name: Dr. {sample_patient['doctor_name']}")
            st.write(f"License: {sample_patient['doctor_license']}")
            st.write(f"Date: {sample_patient['date']}")
        
        st.write("**Observations**")
        st.write(sample_observations)
        
        st.write("**Prescribed Medications**")
        
        # Create DataFrame for medications
        med_df = pd.DataFrame(sample_meds)
        st.table(med_df)
        
        st.write("**Recommended Tests**")
        test_df = pd.DataFrame(sample_tests)
        st.table(test_df)
        
        # Try to generate PDF for example
        try:
            sample_pdf = create_prescription_pdf(sample_patient, sample_meds, sample_observations, sample_tests)
            if sample_pdf:
                st.download_button(
                    label="Download Sample Prescription",
                    data=base64.b64decode(sample_pdf),
                    file_name="sample_prescription.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Could not generate sample PDF: {e}")

if __name__ == "__main__":
    main()
