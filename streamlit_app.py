import os, time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import streamlit.components.v1 as com
from data_engineering import flk_scrapper
from db_utils import rest_db
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
from PIL import Image
from io import BytesIO
import sys
sys.path.append('ml_retrievers/')
import flash_retriever_utils, fastembed_wrap



# Function to get the log path
def get_logpath(logpath='logs/selenium.log'):
    return os.path.join(os.getcwd(), logpath)

# Function to delete the Selenium log
def delete_selenium_log(logpath):
    if os.path.exists(logpath):
        os.remove(logpath)

# Function to get the WebDriver options
def get_webdriver_options():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--remote-debugging-pipe")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-web-security")
    # Adding argument to disable the AutomationControlled flag 
    options.add_argument("--disable-blink-features=AutomationControlled") 
    # Exclude the collection of enable-automation switches 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    
    # Turn-off userAutomationExtension 
    options.add_experimental_option("useAutomationExtension", False) 
    
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
    
    driver = login_to_linkedin(usr, pwd, driver, sync_status)
    # status, driver = flk_scrapper.scrape_lk(driver, sync_status)
    # st.session_state.sync_status = status
    # # ret = driver.page_source
    # sync_status.write(st.session_state.sync_status)
    

def cache_safe_resync_saved_post(usr, pwd, sync_status):
    try:
        # Display a spinner while the function is running
        driver = get_or_create_driver()
        # resync_saved_post(usr, pwd, sync_status) # keep only login in this block 
    except:
        # restart Chrome driver
        st.warning("Corrupt Driver.. Restarting")
        if 'driver' in st.session_state: del st.session_state['driver']
        driver = get_or_create_driver()
    
    st.session_state.sync_status = "Got the driver"
    sync_status.info(st.session_state.sync_status)
    run_syncup_logic(driver, usr, pwd, sync_status)
    # st.session_state.resync_values = {'result': result}
    

# # Function to handle resync button click
# def resync_saved_post(usr, pwd, sync_status):
#     # Display a spinner while the function is running
#     driver = get_or_create_driver()
#     st.session_state.sync_status = "Got the driver"
#     sync_status.info(st.session_state.sync_status)
#     result = run_syncup_logic(driver, usr, pwd, sync_status)
#     st.session_state.resync_values = {'result': result}

def update_authorize(driver, sync_status):
    st.session_state.update_auth = False
    sync_status.info(f"getting {st.session_state.auth_key}")
    driver.find_element("name", "pin").send_keys(st.session_state.auth_key)
    auth_submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
    auth_submit_btn.click()
    time.sleep(20)
    sync_status.info(f"trying to resync")
    status, driver = flk_scrapper.scrape_lk(driver, sync_status)
    time.sleep(20)

def update_authorize_img(driver, all_clicks, sync_status):
    sync_status.info(f"getting {st.session_state.verif_text}")
    ans = int(st.session_state.verif_text)-1
    all_clicks[ans].click()
    time.sleep(10)
    driver.switch_to.default_content()
    sync_status.info(f"trying to resync")
    status, driver = flk_scrapper.scrape_lk(driver, sync_status)
    time.sleep(20)
    st.session_state.update_auth = False
    

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
    time.sleep(5.7)
    # sync_status.write(driver.page_source)
    # Wait for the page_source to be loaded
    
    # check if on verification page authenticator page
    if 'Security Verification' in driver.title:
        # st.session_state.update_auth =  True
        
        verification_type = driver.find_elements(By.CLASS_NAME, "form__subtitle")
        
        if verification_type and "verification code" in verification_type[0].text:
            st.session_state.sync_status = "On Auth page"
            sync_status.info(st.session_state.sync_status)
            #  check the type of verification page you are on
            time.sleep(10)
            col1, col2 = sync_status.columns(2)
            
            auth_txt = col1.text_input("Authenticator", key="auth_key")
            auth_submit_btn = col2.button("Authorize", args=(driver, sync_status,), on_click=update_authorize)
            
            while st.session_state.update_auth:
                print("Doing Nothing")
                time.sleep(1)
                
        else:
            st.session_state.sync_status = "On Verification page"
            sync_status.info(st.session_state.sync_status)
            time.sleep(2.5)
            # sync_status.write(driver.page_source)
            # time.sleep(10)
            # Locate the app__content element
            app_content_element = driver.find_element(By.CLASS_NAME, "app__content")


            # Find the iframe element inside app__content
            reach_final_iframe = False
            curr_iframe = app_content_element.find_element(By.TAG_NAME, 'iframe')
            driver.switch_to.frame(curr_iframe)
            
            while not reach_final_iframe:
                try:
                    curr_iframe = driver.find_element(By.TAG_NAME, 'iframe')
                    driver.switch_to.frame(curr_iframe)
                    #last_iframe_element = curr_iframe
                except:
                    reach_final_iframe = True

            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify')]")
            verify_button.click()

            while not st.session_state.clear_security_multi:
                time.sleep(2.5) # 
                
                verification_inst = driver.find_element(By.ID, "game_children_text")
                verif_text = verification_inst.text
                verification_img = driver.find_element(By.TAG_NAME, "img")

                # Assuming you already have the base64-encoded image data
                # Remove the "data:image/jpeg;base64," prefix
                img_src = verification_img.get_attribute('src')
                base64_data = img_src.split(',')[1]  
                # # Decode the base64 data
                binary_data = base64.b64decode(base64_data)

                # # Create a PIL Image from the binary data
                image = Image.open(BytesIO(binary_data))

                # Display the image in a Streamlit app
                all_clicks = driver.find_elements(By.TAG_NAME, "a")
                
                # user challenge solve input
                _col1, col3 = sync_status.columns(2)
                col1, col2 = _col1.columns(2)
                user_challenge_inp = col1.text_input(f"{verif_text}", key="verif_text")
                # auth_submit_btn = col2.button("Authorize", args=(driver, sync_status,), on_click=update_authorize)
                # button_html = f'<img src="{image}" alt="Authorize" style="width:300px;height:200px;"> Authorize'
                # auth_submit_btn = col2.markdown(label=button_html,
                #                                 args=(driver, all_clicks, sync_status,), 
                #                                 on_click=update_authorize_img)
                auth_submit_btn = col2.button(label='Authorize Img', 
                                              args=(driver, all_clicks, sync_status,),  
                                              on_click=update_authorize_img)
                auth_img = col3.image(image)
                while st.session_state.update_auth:
                    print("Doing Nothing")
                    time.sleep(1)
                
                if 'Security Verification' not in driver.title:
                    st.session_state.clear_security_multi = True
                    st.session_state.update_auth = True
                
    else:
        print(f"Loged In to account : {username}")
        st.session_state.sync_status = "Successfully Logged In"
        sync_status.write(st.session_state.sync_status)
        time.sleep(15)
        # sync_status.write(driver.page_source)
        # time.sleep(15)
        st.session_state.sync_status = "Going to Scrape"
        sync_status.write(st.session_state.sync_status)
        time.sleep(15)
        status, driver = flk_scrapper.scrape_lk(driver, sync_status)
        st.session_state.sync_status = status
        # ret = driver.page_source
        sync_status.write(st.session_state.sync_status)
    
    
    return driver

@st.cache_data
def load_flipcard_css():
    with open("ui_component/flipcard.css") as fp:
        css_code = fp.read()
    return f"<style>{css_code}</style>"

def fetch_match_items(input_query, mode='flash'):
    with st.spinner("Scanning virtual memory !!"):
        db_client = rest_db.RestDB()
        all_items_dump = db_client.fetch_all_items()
        if mode == 'flash':
            top_resp = flash_retriever_utils.fetch_flash_topn(input_query, all_items_dump)
        else:
            top_resp = fastembed_wrap.fetch_fast_topn(input_query) #todo: include fast method for retirever step
        # no pagination implement limiting to fix number of top n
        st.session_state.search_item['result'] = top_resp #f'{list(range(20))}'   

@st.cache_data
def fetch_flipcard_layout():
    with open('ui_component/flipcard.html') as fp:
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
    with open('ui_component/flipcard.js') as fp:
        flipcard_js = fp.read()
    return f"""{flipcard_js}"""


# Main flow of the Streamlit app
def main_flow():
    st.set_page_config(page_title="VirtualSync", page_icon='🫡', initial_sidebar_state='collapsed')
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title('VirtualSync')
        st.markdown('''Interact with your virtual memory and find things faster and efficient
            ''', unsafe_allow_html=True)
    with col2:
        st.image('ui_component/logo.png')
    st.markdown('---')
    # add ballon to session
    if 'first_start' not in st.session_state: st.session_state.first_start = {'value': None}
    if st.session_state.first_start['value'] is None: st.balloons()
    
    # if 'resync_values' not in st.session_state: st.session_state.resync_values = {'result': None}
    # initialise a boolean attr in session state
    if "button" not in st.session_state: st.session_state.button = False
    if "search_item" not in st.session_state: st.session_state.search_item = {'result': None}
    if "sync_status" not in st.session_state: st.session_state.sync_status = ""
    if "update_auth" not in st.session_state: st.session_state.update_auth = True
    if "clear_security_multi" not in st.session_state: st.session_state.clear_security_multi = False
    
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
    fetch_item_btn = col2.button("🔍", args=(text_input,), on_click=fetch_match_items)
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
    
    result_container = st.empty()
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

    
    log_container = st.empty()
    
    result = st.session_state.get('sync_status', None)
    if result is not None:
        with result_container:
        #   st.session_state.sync_status = 'Sync Completed Successfully'
        #   sync_status.info(st.session_state.sync_status)
          st.write(result)
          
    if st.session_state.first_start['value'] is not None and st.session_state.search_item['result'] is None:
        with log_container:  
            show_selenium_log(logpath=logpath)
    
    st.session_state.first_start['value'] = True

if __name__ == "__main__":
    # Set logger and last step to connect to log viewer
    logpath = get_logpath()
    # delete_selenium_log(logpath=logpath)
    main_flow()
