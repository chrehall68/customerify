import streamlit as st

# Initialize session state to store submissions
if 'submissions' not in st.session_state:
    st.session_state['submissions'] = []

# Title of the app
st.title("Text Input Box with Multiple Submissions")

# Text input box
text_input = st.text_input("Enter your text here:")

# Submit button
if st.button("Submit"):
    if text_input:  # Ensure the input is not empty
        st.session_state['submissions'].append(text_input)
        st.success(f"Submitted: {text_input}")
    else:
        st.error("Please enter some text before submitting.")

# Display all submissions
if st.session_state['submissions']:
    st.write("### All Submissions:")
    for i, submission in enumerate(st.session_state['submissions'], 1):
        st.write(f"{i}. {submission}")
