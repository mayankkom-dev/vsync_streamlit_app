import streamlit as st
from flk_scrapper import scrape_lk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import shutil, os

@st.cache_resource(show_spinner=False)
def get_webdriver_options():
    # Set up Chrome options
    # Set up Chrome options
    chrome_options = Options()
    # Run in headless mode
    chrome_options.add_argument("--headless")

    # Set the window size (optional)
    chrome_options.add_argument("--window-size=1920x1080")

    # Disable GPU (optional, might help with headless issues)
    chrome_options.add_argument("--disable-gpu")

    # Disable images to speed up page loading (optional)
    # chrome_options.add_argument("--blink-settings=imagesEnabled=false")

    # Set the User-Agent header to mimic a regular Chrome browser
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Disable notifications (optional)
    chrome_options.add_argument("--disable-notifications")

    # Disable infobars (optional)
    chrome_options.add_argument("--disable-infobars")

    # Disable extensions (optional)
    chrome_options.add_argument("--disable-extensions")

    # Disable sandboxing (optional, use with caution)
    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--ignore-certificate-errors")
    return chrome_options

@st.cache_resource(show_spinner=False)
def get_logpath():
    return os.path.join(os.getcwd(), 'selenium.log')


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

@st.cache_resource(show_spinner=False)
def get_chromedriver_path():
    # return shutil.which('chromedriver')
    chrome_version = "120.0.6099.109"  # Use the actual version of your Chrome browser
    driver_path = ChromeDriverManager(driver_version=chrome_version).install()
    return driver_path


def get_webdriver_service(logpath):
    service = Service(
        executable_path=get_chromedriver_path(),
        log_output=logpath,
    )
    return service

# @st.cache
# def get_driver():
    
#     chrome_version = "92.0.4515.107"
#     # Use webdriver_manager to install and manage ChromeDriver
#     driver_path = ChromeDriverManager(driver_version=chrome_version).install()
#     # Specify the path to the Chrome binary
#     chrome_options.binary_location = driver_path

#     print(driver_path)
#     print("Web Driver created") 
#     return webdriver.Chrome(service=Service(driver_path), options=chrome_options)
#     # return driver

# def run_selenium(logpath):
#     name = str()
#     with webdriver.Chrome(options=get_webdriver_options(), service=get_webdriver_service(logpath=logpath)) as driver:
#         url = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
#         driver.get(url)
#         xpath = '//*[@class="ui-mainview-block eventpath-wrapper"]'
#         # Wait for the element to be rendered:
#         element = WebDriverWait(driver, 10).until(lambda x: x.find_elements(by=By.XPATH, value=xpath))
#         name = element[0].get_property('attributes')[0]['name']
#     return name

def get_driver(logpath):
    return webdriver.Chrome(options=get_webdriver_options(), service=get_webdriver_service(logpath=logpath))
    

# Streamlit UI
def main():
    st.title("VirtualSync")
    if st.button("Load"):
        # result = run_selenium(logpath=logpath)
        driver = get_driver(logpath=logpath)
        ret = scrape_lk(driver)
        print(ret)
        # st.info(f'Result -> {result}')
        # st.info('Successful finished. Selenium log file is shown below...')
        show_selenium_log(logpath=logpath)
        

if __name__ == "__main__":
    logpath=get_logpath()
    delete_selenium_log(logpath=logpath)
    main()
