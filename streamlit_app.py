import streamlit as st
from flk_scrapper import scrape_lk

# Streamlit UI
def main():
    st.title("VirtualSync")
    if st.button("Load"):
        ret = scrape_lk()
        print(ret)
        

if __name__ == "__main__":
    main()
