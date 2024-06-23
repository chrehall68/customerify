import streamlit as st

# Initialize session state to store submissions
if 'additional_submissions' not in st.session_state:
    st.session_state['additional_submissions'] = []

if 'main_submissions' not in st.session_state:
    st.session_state['main_submissions'] = []

# Title of the app
st.title("Customer Service App")

# Display phone number
st.write("### Phone Number")
st.text_input("Phone Number", value="867-5309", disabled=True)

# Additional text input box
additional_text_input = st.text_input("Enter company name here:", key="additional_input")

# Submit button for the additional text input box
if st.button("Submit company name"):
    if additional_text_input:  # Ensure the input is not empty
        st.session_state['additional_submissions'].append(additional_text_input)
        st.success(f"Company name submitted: {additional_text_input}")
    else:
        st.error("Please enter company name before submitting.")

# Main text input box
text_input = st.text_input("Enter URL here:", key="main_input")

# Submit button for the main text input box
if st.button("Submit URLs"):
    if text_input:  # Ensure the input is not empty
        st.session_state['main_submissions'].append(text_input)
        st.success(f"URL submitted: {text_input}")
    else:
        st.error("Please a URL before submitting.")

# Display all submissions for the main text input box
if st.session_state['main_submissions']:
    st.write("### URLs submitted:")
    for i, submission in enumerate(st.session_state['main_submissions'], 1):
        st.write(f"{i}. {submission}")
