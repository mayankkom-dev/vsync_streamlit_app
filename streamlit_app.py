import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from app_utils import *

# Function to get the log path
def get_logpath(logpath='selenium.log'):
    return os.path.join(os.getcwd(), logpath)

# Function to delete the Selenium log
def delete_selenium_log(logpath):
    if os.path.exists(logpath):
        os.remove(logpath)

# Function to get the WebDriver options
def get_webdriver_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    return options

# Function to get the WebDriver service
def get_webdriver_service(logpath):
    service = Service(log_output=logpath)
    return service


# Function to show Selenium log
def show_selenium_log(logpath):
    if os.path.exists(logpath):
        with open(logpath) as f:
            content = f.read()
            st.code(body=content, language='log', line_numbers=True)
    else:
        st.warning('No log file found!')

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
    ret = None
    driver.get('https://www.linkedin.com')
    ret = driver.page_source
    return ret

def cache_safe_resync_saved_post():
    try:
        resync_saved_post()
    except:
        # restart Chrome driver
        st.warning("Corrupt Driver.. Restarting")
        if 'driver' in st.session_state: del st.session_state['driver']
        resync_saved_post()

# Function to handle resync button click
def resync_saved_post():
    # Display a spinner while the function is running
    with st.spinner("Syncing up..."):
        driver = get_or_create_driver()
        result = run_syncup_logic(driver)
        st.session_state.resync_values = {'result': result}

# Main flow of the Streamlit app
def main_flow():
    st.set_page_config(page_title="VirtualSync", page_icon='🫡', initial_sidebar_state='collapsed')
    st.title('VirtualSync')
    st.markdown('''Interact with your virtual memory and find things faster and efficient
        ''', unsafe_allow_html=True)
    st.markdown('---')
    # add ballon to session
    if 'first_start' not in st.session_state: st.session_state.first_start = {'value': None}
    if st.session_state.first_start['value'] is None: st.balloons()
    if 'resync_values' not in st.session_state: st.session_state.resync_values = {'result': None}
    st.button('ReSync', on_click=cache_safe_resync_saved_post)
   
    result_container = st.empty()
    log_container = st.empty()
    
    result = st.session_state.resync_values['result']
    if result is not None:
        with result_container:
          st.write(result)
    if st.session_state.first_start['value'] is not None:
        with log_container:  
            show_selenium_log(logpath=logpath)
    
    st.session_state.first_start['value'] = True

if __name__ == "__main__":
    # Set logger and last step to connect to log viewer
    logpath = get_logpath()
    # delete_selenium_log(logpath=logpath)
    main_flow()
