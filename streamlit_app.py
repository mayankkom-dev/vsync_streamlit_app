import streamlit as st
from flk_scrapper import scrape_lk

# Streamlit UI
def main():
    # with st.echo():
    #     from selenium import webdriver
    #     from selenium.webdriver.chrome.options import Options
    #     from selenium.webdriver.chrome.service import Service
    #     from webdriver_manager.chrome import ChromeDriverManager

    #     @st.experimental_singleton
    #     def get_driver():
    #         return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        
    #     driver = get_driver()
    #     print("Downloaded chromium")

    st.title("VirtualSync")
    if st.button("Load"):
        ret = scrape_lk()
        print(ret)
        

if __name__ == "__main__":
    main()
