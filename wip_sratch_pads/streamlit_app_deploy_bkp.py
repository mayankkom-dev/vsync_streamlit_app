import os
import shutil
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


@st.cache_data(show_spinner=False)
def get_logpath():
    return os.path.join(os.getcwd(), 'selenium.log')

@st.cache_data(show_spinner=False)
def get_chromedriver_path():
    return shutil.which('chromedriver')

def get_webdriver_options():
    # options = Options()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    return options

def get_webdriver_service(logpath):
    service = Service(executable_path=get_chromedriver_path(), log_output=logpath)
    return service

def delete_selenium_log(logpath):
    if os.path.exists(logpath):
        os.remove(logpath)

def show_selenium_log(logpath):
    if os.path.exists(logpath):
        with open(logpath) as f:
            content = f.read()
            st.code(body=content, language='log', line_numbers=True)
    else:
        st.warning('No log file found!')

def run_selenium(logpath):
    name = str()
    # with webdriver.Chrome(service=get_webdriver_service(logpath), options=get_webdriver_options()) as driver:
    #     url = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
    #     driver.get(url)
    #     xpath = '//*[@class="ui-mainview-block eventpath-wrapper"]'
    #     try:
    #         element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    #         name = element.get_property('attributes')[0]['name']
    #     except TimeoutException:
    #         st.error("Timed out waiting for the element to be rendered")
    # return name
    # Navigate to the URL
    # ##########################################
    # Install ChromeDriver using ChromeDriverManager
    # name = ChromeDriverManager(url="").install()
    # st.write(name)
    # # Create a Chrome WebDriver instance
    # driver = webdriver.Chrome(options=get_webdriver_options(), service=get_webdriver_service(logpath))
    
    # driver.get('https://www.linkedin.com')

    # # Display the page source
    # st.write(driver.page_source)
    # return driver.page_source
    ###############################################
    service = Service(log_output=logpath)
    options = get_webdriver_options()

    driver = webdriver.Chrome(service=service, options=options)

    driver.get('https://www.linkedin.com')
    ret = driver.page_source
    # Display the page source
    st.write(ret)
    driver.quit()
    return ret

if __name__ == "__main__":
    logpath = get_logpath()
    delete_selenium_log(logpath=logpath)
    st.set_page_config(page_title="Selenium Test", page_icon='✅', initial_sidebar_state='collapsed')
    st.title('🔨 Selenium on Streamlit Cloud')
    st.markdown('''This app is only a very simple test for **Selenium** running on **Streamlit Cloud** runtime.<br>
        The suggestion for this demo app came from a post on the Streamlit Community Forum.<br>
        <https://discuss.streamlit.io/t/issue-with-selenium-on-a-streamlit-app/11563><br><br>
        This is just a very very simple example and more a proof of concept.<br>
        A link is called and waited for the existence of a specific class to read a specific property.
        If there is no error message, the action was successful.
        Afterwards the log file of chromium is read and displayed.
        ''', unsafe_allow_html=True)
    st.markdown('---')

    st.balloons()
    if st.button('Start Selenium run'):
        st.warning('Selenium is running, please wait...')
        result = run_selenium(logpath=logpath)
        st.info(f'Result -> {result}')
        st.info('Successful finished. Selenium log file is shown below...')
        show_selenium_log(logpath=logpath)
