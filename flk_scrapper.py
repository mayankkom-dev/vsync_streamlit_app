from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from dotenv import load_dotenv
import time
import os
from flk_scrapper_utils import *
import concurrent.futures
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
load_dotenv()



# Linkedin credentials
username = "mayankk.om@gmail.com" #"scratchai.blog@gmail.com"#
password = "Strong_pass1#" #os.getenv("LINKEDIN_PASS")

def scrape_lk(driver):
    
    login_to_linkedin(username, password, driver)
    time.sleep(20)
    print("\033[91msleeped\033[0m")
    # uuid using profile_url and see if the user is already onboarded 
    # if onboarded: find_delta and keep inseting unless you find pre-existing data
    driver.get("https://www.linkedin.com/my-items/saved-posts/")
    print("Open Your posts.")
    time.sleep(6)

    scroll_to_bottom(driver)
    total_scraped = 0
    valid_scraped = 0
    all_valid = []
    # all_complete_flag = False
    i = 1

    while True: #not all_complete_flag:
        if i%5==0:
            upload_restdb(all_valid)
            all_valid = []
        print('- ' * 8 + "\n")
        print("\033[91m#\nStarting\033[0m\n")
        # posts_elements = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, '.relative.entity-result__content-summary'))
        # )
        posts_elements = driver.find_elements(By.CLASS_NAME, "entity-result__content-container")
        if not posts_elements[total_scraped:]: 
            # all_complete_flag = True
            break
        batch_elements_len = len(posts_elements)
        
        # Number of threads you want to use
        num_threads = 5  # Adjust as needed

        # Create a ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit tasks to the thread pool
            processed_posts = list(executor.map(process_post, posts_elements[total_scraped:]))
        # processed_posts = []
        # for post_ in posts_elements[total_scraped:]:
        #     prep_post = process_post(post_)
        #     processed_posts.append(prep_post)
        
        total_scraped = batch_elements_len
        # Count the not None posts
        valid_posts = [post for post in processed_posts if post is not None]
        all_valid.extend(valid_posts)
        valid_scraped += len(valid_posts)
        print(f"Number of valid posts: {len(valid_posts)}")
        print("sleepingagain")
        time.sleep(3)
        # click_show_more_button()
        # time.sleep(3)
        
        scroll_to_bottom(driver)
        i += 1
        break

    if all_valid:
        print(all_valid)
        upload_restdb(all_valid)
    driver.quit()
    return "Done"