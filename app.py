import streamlit as st
import pandas as pd

# Function to clean and extract information for each course and time slot
def extract_timetable_data(df):
    timetable_data = []
    
    for index, row in df.iterrows():
        if pd.notna(row['Date']):  # If the Date column is not NaN
            # Check if the date is already a string or a datetime object
            if isinstance(row['Date'], pd.Timestamp):
                current_date = row['Date'].strftime('%Y-%m-%d')  # Convert datetime to string (YYYY-MM-DD)
            else:
                current_date = row['Date']  # Already a string
        
        for time_slot in ['9:00 to 10:00 AM', '10:20 to 11:20 AM', '11:40 to 12:40 PM', 
                          '01:00 to 02:00 PM', '02:30 to 03:30 PM', '03:40 to 04:40 PM', 
                          '5:00 to 6:00 PM', '6:20 to 7:20 PM']:
            
            if pd.notna(row[time_slot]):  # If the time slot has course information
                course_info = row[time_slot].split('\n')
                
                if len(course_info) >= 2:
                    course_code = course_info[0].strip()
                    course_name = course_info[1].strip()
                    departments_sections = course_info[2:]
                    
                    # Clean departments and sections
                    cleaned_departments = []
                    for dept_section in departments_sections:
                        dept_section = dept_section.strip()
                        if dept_section:  # Ignore empty sections
                            cleaned_departments.append(dept_section)
                    
                    # Store structured data in a dictionary
                    entry = {
                        'Date': current_date,  # The date is now a string or remains a string if it already was
                        'Time': time_slot,
                        'Course Code': course_code,
                        'Course Name': course_name,
                        'Departments & Sections': cleaned_departments
                    }
                    timetable_data.append(entry)

    return timetable_data

# Main Streamlit application
st.title("Timetable Viewer Application")

# Initialize session state to keep track of file upload and course data
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False

# File upload step
if not st.session_state.uploaded:
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        # Load and clean the data
        df = pd.read_excel(uploaded_file, header=None)
        
        # Skip the first 3 rows, and assume row 3 contains the correct headers for time slots
        df = df[3:]

        # Set the column names explicitly based on the provided headers
        df.columns = ["Date", "9:00 to 10:00 AM", "Gap1", "10:20 to 11:20 AM", "Gap2", 
                      "11:40 to 12:40 PM", "Gap3", "01:00 to 02:00 PM", "Gap4", 
                      "02:30 to 03:30 PM", "Gap5", "03:40 to 04:40 PM", "Gap6", 
                      "5:00 to 6:00 PM", "Gap7", "6:20 to 7:20 PM"]

        # Drop any rows that are fully NaN
        df = df.dropna(how='all')

        # Extract the timetable data and save it to session state
        st.session_state.timetable_data = extract_timetable_data(df)
        st.session_state.uploaded = True

# Course selection and display step
if st.session_state.uploaded:
    # Move course selection to the sidebar for better layout and visibility
    with st.sidebar:
        st.write("### Course Selection")
        # Extract all course names and course codes for selection
        course_options = [f"{entry['Course Code']} - {entry['Course Name']}" for entry in st.session_state.timetable_data]
        selected_courses = st.multiselect("Select the courses you want to view the timetable for:", course_options)

    # Group courses by date
    grouped_by_date = {}
    if selected_courses:
        for selected_course in selected_courses:
            course_code, course_name = selected_course.split(" - ")
            
            # Find the matching course data
            filtered_courses = [entry for entry in st.session_state.timetable_data if entry['Course Code'] == course_code]
            
            for course in filtered_courses:
                date = course['Date']
                if date not in grouped_by_date:
                    grouped_by_date[date] = []
                grouped_by_date[date].append(course)

    # Display timetable grouped by date
    if grouped_by_date:
        for date, courses in grouped_by_date.items():
            st.markdown(f"## {date}")
            columns = st.columns(3)  # Display 3 columns per row
            
            for i, course in enumerate(courses):
                with columns[i % 3]:  # Rotate through columns
                    st.markdown(
                        f"""
                        <div style="border: 2px solid #4CAF50; padding: 8px; border-radius: 10px; margin-bottom: 10px; font-size: 0.9rem;">
                            <h4 style="color: #4CAF50; font-size: 1.1rem;">{course['Course Code']} - {course['Course Name']}</h4>
                            <p><strong style="color: #e74c3c;">Time:</strong> <span style="font-weight: bold;">{course['Time']}</span></p>
                        </div>
                        """, unsafe_allow_html=True
                    )
