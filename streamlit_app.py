import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from app_utils import *


# Function to get or create the WebDriver
def get_or_create_driver():
    # Check if the driver is already stored in the session state
    if 'driver' not in st.session_state:
        logpath = get_logpath()
        # Create a new driver if not exists
        service = get_webdriver_service(logpath)
        options = get_webdriver_options()
        driver = webdriver.Chrome(service=service, options=options)
        # Store the driver in the session state
        st.session_state.driver = driver
    return st.session_state.driver

# Function to run sync-up logic
def run_syncup_logic(driver):
    driver.get('https://www.linkedin.com')
    ret = driver.page_source
    return ret

def cache_safe_resync_saved_post():
    try:
        resync_saved_post()
    except:
        # restart Chrome driver
        print("Corrupt Driver.. Restarting")
        del st.session_state['driver']
        resync_saved_post()

# Function to handle resync button click
def resync_saved_post():
    # Display a spinner while the function is running
    with st.spinner("Syncing up..."):
        driver = get_or_create_driver()
        result = run_syncup_logic(driver)
    # # Use st.empty() to create a placeholder
    # result_container = st.empty()
    # # Now update the content within the placeholder
    # with result_container:
    #     st.write(result)
    #     st.info('Successfully finished. Selenium log file is shown below...')
    #     show_selenium_log(logpath=logpath)
        st.session_state.resync_values = {'result': result}

# Function to load Streamlit page
def load_st_page():
    st.set_page_config(page_title="VirtualSync", page_icon='🫡', initial_sidebar_state='collapsed')
    st.title('VirtualSync')
    st.markdown('''Interact with your virtual memory and find things faster and efficient
        ''', unsafe_allow_html=True)
    st.markdown('---')
    st.balloons()
    resync_btn = st.button('ReSync', on_click=cache_safe_resync_saved_post)
    # Create a session state to store values across sessions
    if 'resync_values' not in st.session_state:
        st.session_state.resync_values = {'result': None}
    
    # Display result and log file content
    if st.session_state.resync_values['result'] is not None:
        st.write(st.session_state.resync_values['result'])
        st.info('Successfully finished. Selenium log file is shown below...')
        show_selenium_log(logpath=logpath)



# Main flow of the Streamlit app
def main_flow():
    load_st_page()

if __name__ == "__main__":
    # Set logger and last step to connect to log viewer
    logpath = get_logpath()
    # delete_selenium_log(logpath=logpath)
    main_flow()
