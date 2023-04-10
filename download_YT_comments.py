import sys
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_video_id(url):
    video_id = re.search('(?:v=|youtu\.be/)([^&?/]+)', url)
    return video_id.group(1) if video_id else None

def get_comments(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'comments'))
        )
    except TimeoutException:
        print('Could not load comments')
        driver.quit()
        return []

    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    print('scrolling page')
    while True:
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
        time.sleep(0.5)
        print('scrolling...')
        new_height = driver.execute_script('return document.documentElement.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height

    #comments_elements = driver.find_elements_by_xpath('//*[@id="content-text"]')
    comments_elements = driver.find_elements_by_css_selector('#content-text')
    comments = [comment.text for comment in comments_elements]
    driver.quit()

    return comments

def main():
    if len(sys.argv) < 2:
        print('Usage: python scrape_comments.py <YouTube Video URL>')
        sys.exit(1)

    url = sys.argv[1]
    video_id = get_video_id(url)
    if not video_id:
        print('Invalid YouTube video URL')
        sys.exit(1)

    try:
        comments = get_comments(url)
        with open(f'comments_{video_id}.txt', 'w', encoding='utf-8') as f:
            for comment in comments:
                f.write(comment + '\n')
        print(f'Successfully scraped {len(comments)} comments for video {video_id}')
    except Exception as error:
        print(f'An error occurred: {error}')
        sys.exit(1)

if __name__ == '__main__':
    main()
