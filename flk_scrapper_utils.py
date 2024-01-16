from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import time 
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import hashlib
import uuid
import requests
import json

def upload_restdb(pay_list):
    url = "https://virtualsync-63c9.restdb.io/rest/virtualsync"

    payload = json.dumps(pay_list)
    headers = {
        'content-type': "application/json",
        'x-apikey': "7998f5bbe9751602547c48197347d697354fe",
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    
    print(response.text)

def url_to_uuid(url):
    # Create an MD5 hash object
    hash_object = hashlib.md5()

    # Update the hash object with the URL
    hash_object.update(url.encode('utf-8'))

    # Convert the hexadecimal digest to a UUID
    generated_uuid = uuid.UUID(hash_object.hexdigest())

    return generated_uuid


def login_to_linkedin(username, password, driver):
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
    print(f"Loged In to account : {username}")

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def process_post(post_element):
    print('\033[92m- ' * 12 + "\033[0m")
    post = {}
    # print("\033[91m\ninserted : "+str(i)+"\nposts_counter : "+str(posts_counter)+"#\n\033[0m")
    if post_element:
        try:
            post['id_'] = ""
            post['writer_image'] = post['write_name'] = post["writer_link"] = post["writer_details"] = ""
            post["post_text"] = post["post_title"] = post["post_link"] \
                = post['post_link_img'] = ""
            
            html_content = post_element.get_attribute("outerHTML")
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the parent div with class 'display-flex'
            display_flex_div = soup.find('div', class_='display-flex')
            display_top_level_divs = display_flex_div.find_all('div', recursive=False)
            img_ = display_top_level_divs[0].find('img')
            if img_: post['writer_image'] = img_.get('src', "")
            post['writer_link'] = display_top_level_divs[0].find('a').get('href', "")
            profile_name_detail_divs = display_top_level_divs[1].find_all('div', recursive=False)
            post['write_name'] = profile_name_detail_divs[0].find_all('span', recursive=True)[3].text
            post['writer_details'] = profile_name_detail_divs[1].find_all('div', recursive=False)[0].text

            entity_result_div = soup.find('div', class_='entity-result__content-inner-container')
            if entity_result_div:
                entity_top_level_divs = entity_result_div.find_all('div', recursive=False)
                # if shared with an image and text
                if entity_top_level_divs and len(entity_top_level_divs)==1:
                    post['post_text'] = entity_top_level_divs[0].find('p').text
                
                if len(entity_top_level_divs)>1:
                    post['post_text'] = entity_top_level_divs[1].find('p').text
                    post["post_link"] = entity_top_level_divs[0].find('a').get('href', '')
                    post['post_link_img'] = entity_top_level_divs[0].find('img').get('src', '')
                else:
                    # if shared with an external link
                    entity_top_level_a = entity_result_div.find_all('a', recursive=False)
                    # logic for article img 
                    if entity_top_level_a:
                        post["post_link"] = entity_top_level_a[0].get('href', '')
                        doc_img_tag = entity_top_level_a[0].find('img')
                        if doc_img_tag: post['post_link_img'] = doc_img_tag.get('src')
                        doc_text_tag = entity_top_level_a[0].find('p')
                        if doc_text_tag: post['post_text'] = f"{post['post_text']}\n{doc_text_tag.text}"
                post['id_'] = str(url_to_uuid(post['post_link']))
        except:
            pass
        print(post)
        
        if not post["post_link"]:
            print("\033[91m#No Post Link\033[0m\n\n")
            return None  
        
        print(f"\033[92mProcessed post\033[0m\n")
        return post
        
