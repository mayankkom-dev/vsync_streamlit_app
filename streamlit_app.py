import os, time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import streamlit.components.v1 as com
from flk_scrapper import scrape_lk
from rest_db import RestDB

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
    options.add_argument("--remote-debugging-pipe")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-web-security")
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
def run_syncup_logic(driver, usr, pwd, sync_status):
    ret = None
    driver = login_to_linkedin(usr, pwd, driver, sync_status)
    status, driver = scrape_lk(driver, sync_status)
    st.session_state.sync_status = status
    # ret = driver.page_source
    sync_status.write(st.session_state.sync_status)
    # return ret

def cache_safe_resync_saved_post(usr, pwd, sync_status):
    try:
        resync_saved_post(usr, pwd, sync_status) # keep only login in this block 
    except:
        # restart Chrome driver
        st.warning("Corrupt Driver.. Restarting")
        if 'driver' in st.session_state: del st.session_state['driver']
        resync_saved_post(usr, pwd, sync_status)

# Function to handle resync button click
def resync_saved_post(usr, pwd, sync_status):
    # Display a spinner while the function is running
    driver = get_or_create_driver()
    st.session_state.sync_status = "Got the driver"
    sync_status.info(st.session_state.sync_status)
    result = run_syncup_logic(driver, usr, pwd, sync_status)
    st.session_state.resync_values = {'result': result}

def login_to_linkedin(username, password, driver, sync_status):
    driver.get("https://www.linkedin.com/?original_referer=")
    time.sleep(3)
    # find username/email field and send the username itself to the input field
    driver.find_element("name", "session_key").send_keys(username)
    # find password input field and insert password as well
    driver.find_element("name", "session_password").send_keys(password)

    # click login button
    sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
    # Click the "Sign in" button
    time.sleep(2)
    sign_in_button.click()
    time.sleep(2)
    # check if on verification page authenticator page
    if 'Security Verification' in driver.title:
        st.session_state.sync_status = "On Verification page"
        sync_status.info(st.session_state.sync_status)
        time.sleep(10)
        sync_status.write(driver.page_source)
        time.sleep(10)
    # else:    
    # try:
    #     verification_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify')]")
    #     st.session_state.sync_status = "Clicked Verify"
    #     sync_status.write(driver.page_source)
    #     print("Inside verification page")
    #     verification_btn.click()
    #     time.sleep(2)
    #     # Display text
    #     text = driver.find_element(By.CSS_SELECTOR, "div.game_children_text").text 
    #     sync_status.write(text)
    #     time.sleep(2)
    #     # Display images
    #     ul_element = driver.find_elements(By.CSS_SELECTOR, "div.game_children_challenge")
    #     # Find all <li> elements within the <ul>
    #     li_elements = ul_element.find_elements_by_tag_name('li')
    #     # # Extract image URLs
    #     # image_urls = []
    #     # for li in li_elements:
    #     #     a_element = li.find_element_by_tag_name('a')
    #     #     image_url = a_element.get_attribute('aria-label')
    #     #     image_urls.append(image_url)
    #     # for i, image in enumerate(images):
    #     #     src = image.get_attribute("src")
    #     #     container.image(src, caption=f"Image {i+1}")


        
    # except:
    #     print("Not on verification page")
    #     pass
    
    
    print(f"Loged In to account : {username}")
    st.session_state.sync_status = "Successfully Logged In"
    sync_status.write(st.session_state.sync_status)
    time.sleep(15)
    sync_status.write(driver.page_source)
    time.sleep(15)
    st.session_state.sync_status = "Going to Scrape"
    sync_status.write(st.session_state.sync_status)
    time.sleep(15)
    return driver

@st.cache_data
def load_flipcard_css():
    with open("flipcard.css") as fp:
        css_code = fp.read()
    return f"<style>{css_code}</style>"

def fetch_match_items():
    with st.spinner("Scanning virtual memory !!"):
        db_client = RestDB()
        all_items_dump = db_client.fetch_all_items()
        st.session_state.search_item['result'] = all_items_dump #f'{list(range(20))}'   

@st.cache_data
def fetch_flipcard_layout():
    with open('flipcard.html') as fp:
        flipcard_html = fp.read()
    return flipcard_html

def gen_flipcard(val): # try except and clean cache for that val
    p_len = min(len(val.get('post_text', "No Text")), 380)
    flip_div = fetch_flipcard_layout()
    data = {"profile_img": val.get('writer_image', None), 
            "write_name":  val.get('write_name', ""),
            "write_details": val.get('writer_details', ""),
            "post_img": val.get('post_link_img', None),
            "post_text": val.get('post_text', "No Text")[:p_len],
            "post_link": val.get('post_link', None)
            }
    flip_div = flip_div.format(**data)
    return flip_div

@st.cache_data
def gen_flip_js():
    return """<script>
            function flipCard(card) {
                card.classList.toggle('is-flipped');
            }

            function openLink(event) {
                // Prevent the card from flipping when clicking on the link
                event.stopPropagation();
            }
            //function openPopup(url) {
            // Show the popup
            //document.getElementById('popup').style.display = 'block';

            // Load the content into the iframe
            //document.getElementById('popupFrame').src = url;
            //}

            //function closePopup() {
            // Hide the popup
            //document.getElementById('popup').style.display = 'none';

            // Clear the iframe content
            //document.getElementById('popupFrame').src = 'about:blank';
            //}
            </script> """


# Main flow of the Streamlit app
def main_flow():
    st.set_page_config(page_title="VirtualSync", page_icon='🫡', initial_sidebar_state='collapsed')
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title('VirtualSync')
        st.markdown('''Interact with your virtual memory and find things faster and efficient
            ''', unsafe_allow_html=True)
    with col2:
        st.image('logo.png')
    st.markdown('---')
    # add ballon to session
    if 'first_start' not in st.session_state: st.session_state.first_start = {'value': None}
    if st.session_state.first_start['value'] is None: st.balloons()
    
    if 'resync_values' not in st.session_state: st.session_state.resync_values = {'result': None}
    # initialise a boolean attr in session state
    if "button" not in st.session_state: st.session_state.button = False
    if "search_item" not in st.session_state: st.session_state.search_item = {'result': None}
    if "sync_status" not in st.session_state: st.session_state.sync_status = ""
    #  .st-emotion-cache-0{
    #                 visibility: hidden;
    #                 }
    if not st.session_state.button:
        st.markdown("""<style>
                   .st-emotion-cache-0.eqpbllx5 {
                        visibility: collapse;
                    }
                    </style>
                    """, unsafe_allow_html=True)
    # write a function for toggle functionality
    def toggle():
        st.session_state.button = not st.session_state.button        

    
    col1, col2, col3 = st.columns([0.7, 0.1, 0.2], gap="medium")
    
    text_input = col1.text_input(label="search_box", 
                                   value="What are you looking for today?", 
                                   label_visibility="collapsed")
    fetch_item_btn = col2.button("🔍", on_click=fetch_match_items)
    sync_btn = col3.button("Syncup", on_click=toggle)
    
    with st.expander('SyncUp LinkedIn', expanded=st.session_state.button):
        col1, col2 = st.columns(2)
        username = col1.text_input("username",  key='usrname')
        pwd = col2.text_input("password",  key='pwd', type="password") # type="password"
        sync_status = st.empty()
        if st.session_state.sync_status:
            if st.session_state.sync_status != 'Completed Scrapping!': st.session_state.sync_status = ""
            sync_status.info(st.session_state.sync_status)
        
        col2.button('Submit', args=(username, pwd, sync_status), on_click=cache_safe_resync_saved_post)
    
    search_result = st.empty()
    
    
    if st.session_state.search_item['result'] is not None:
        n_cols = 2
        col1, col2 = search_result.columns(n_cols) # , col3
        css_design = load_flipcard_css()
        js_script = gen_flip_js()
        all_items = st.session_state.search_item['result']
        # st.write(all_items)
        
        n_rows = len(all_items)//n_cols
        row_idx, st_idx = 0, 0
        while row_idx < n_rows:
            row_items = all_items[st_idx:st_idx+n_cols]
            with col1:
                com.html(f"{css_design}\n{js_script}\n{gen_flipcard(row_items[0])}", height=300, width=350)
                # st.markdown(f"{css_design}\n{gen_flipcard(row_items[0])}", unsafe_allow_html=True)
            with col2:
                com.html(f"{css_design}\n{js_script}\n{gen_flipcard(row_items[1])}", height=300, width=350)
                # st.markdown(f"{css_design}\n{gen_flipcard(row_items[1])}", unsafe_allow_html=True)
            # with col3:
            #     com.html(f"{css_design}\n{js_script}\n{gen_flipcard(row_items[2])}", height=300, width=224)
              

            st_idx = st_idx + n_cols
            row_idx += 1
        
        remaining_item = all_items[st_idx:]
        if remaining_item and len(remaining_item)==1: 
            with col1:
                com.html(f"{css_design}\n{js_script}\n{gen_flipcard(row_items[0])}", height=300, width=350)
        # if remaining_item and len(remaining_item)==2:
        #     with col1:
        #         com.html(f"{css_design}\n{js_script}\n{gen_flipcard(row_items[st_idx])}", height=300, width=224)
        #     with col2:
        #         com.html(f"{css_design}\n{js_script}\n{gen_flipcard(row_items[st_idx+1])}", height=300, width=224)

    result_container = st.empty()
    log_container = st.empty()
    
    result = st.session_state.resync_values['result']
    if result is not None:
        with result_container:
          st.session_state.sync_status = 'Sync Completed Successfully'
          sync_status.info(st.session_state.sync_status)
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
