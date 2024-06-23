import streamlit as st
import requests
import os

deploy_result = None


def deploy(company_name: str, url: str) -> bool:
    # make a post request to backend to deploy an agent for this company
    r1 = requests.post(
        os.environ["FLASK_URL"] + "/api/customerify/store",
        json={"company_name": company_name, "url": url},
        timeout=60,
    )
    r2 = requests.post(
        "https://" + os.environ["NGROK_URL"] + "/deploy",
        data={"company_name": company_name, "url": url},
    )
    return r1.status_code == 200 and r2.status_code == 200


# Initialize session state to store submissions
if "additional_submissions" not in st.session_state:
    st.session_state["additional_submissions"] = []

if "main_submissions" not in st.session_state:
    st.session_state["main_submissions"] = []

# Title of the app
st.title("Customerify Portal")

st.write(
    "Welcome to your Customerify portal.\n\n From here, you can configure a specialized customer service agent"
    " for your company. Simply enter your company name and URLs to be indexed and deployed as customers."
    " Simply enter your business's name, select your information source, and hit deploy!"
    " Once your agent is deployed, customers can call in and receive answers from your agent in real time.",
)

# Additional text input box
# TODO - if we have time, setup some sort of auth (even if its just a dummy login page) so that
# we can get company name from that instead of this input
company_input = st.text_input("Company Name:", key="company_name")

# website url
url_input = st.text_input(
    "Website URL:",
    key="website_url",
    help="This acts as the primary source of information for your customer service agent",
)

# Submit button for the main text input box
if st.button(
    "Deploy",
):
    if url_input:  # Ensure the input is not empty
        st.session_state["url"] = url_input
        st.success(f"Company {company_input} and URL {url_input} submitted!")
        deploy_result = deploy(company_input, url_input)
    else:
        st.error("Please a URL before submitting.")

if deploy_result:
    phone_number = os.environ["PHONE_NUMBER"]
    st.write(f"Deployed at {phone_number}! Just call {phone_number} to get started.")
elif deploy_result == False:
    st.error("Failed to deploy. check your url and try again.")


# Display all submissions for the main text input box
if st.session_state["main_submissions"]:
    st.write("### URLs submitted:")
    for i, submission in enumerate(st.session_state["main_submissions"], 1):
        st.write(f"{i}. {submission}")
