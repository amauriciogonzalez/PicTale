from transformers import pipeline
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gtts import gTTS
import os
import streamlit as st


def img_to_caption(url):
    model = pipeline('image-to-text', model="Salesforce/blip-image-captioning-base", max_new_tokens=20)
    caption = model(url)[0]['generated_text']
    return caption


def caption_to_story(caption):
    class ChromeDriverSingleton:
        _instance = None

        @classmethod
        def get_instance(cls):
            if cls._instance is None:
                cls._instance = cls._create_instance()
            return cls._instance

        @classmethod
        def _create_instance(cls):
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run Chrome in headless mode
            options.add_argument('--disable-gpu')  # Disable GPU acceleration
            options.add_argument('--no-sandbox')  # Bypass OS security model
            options.add_argument('--disable-dev-shm-usage')  # Disable "DevShmUsage" flag
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            return webdriver.Chrome(options=options)

    driver = ChromeDriverSingleton.get_instance()
    driver.get("https://chat.chatgptdemo.net/")
    time.sleep(2) 
    textarea = driver.find_element(By.ID, "input-chat")
    textarea.send_keys("You are a story teller; you can generate a short story based on a simple narrative or character. The story should be no more than 200 words. CONTEXT: " + caption + ". STORY: ")
    time.sleep(2)
    textarea.send_keys(Keys.RETURN)
    time.sleep(10)

    try:
        response = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        return response.text
    finally:
        driver.quit()


def story_to_speech(story):
    language = 'en'
    myobj = gTTS(text=story, lang=language, slow=False)
    myobj.save("speech.mp3")


def main():
    st.set_page_config(page_title="Image to Story")

    st.header("Turn an Image into an Audible Story")
    uploaded_file = st.file_uploader("Upload an Image", type=['png', 'jpg'])

    if uploaded_file is not None:
        print(uploaded_file)
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name, "wb") as file:
            file.write(bytes_data)
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        caption = img_to_caption(uploaded_file.name)
        story = caption_to_story(caption)
        story_to_speech(story)

        with st.expander("Caption"):
            st.write(caption)
        with st.expander("Story"):
            st.write(story)

        st.audio("speech.mp3")


if __name__ == "__main__":
    main()