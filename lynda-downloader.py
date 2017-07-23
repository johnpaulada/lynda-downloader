import time
import re
import os
import urllib2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LYNDA_URL = "https://www.lynda.com/portal/sip?org=houstonlibrary.org"
USERNAME = "xx"
PASSWORD = "xx"
USERNAME_FIELD_ID = "card-number"
PASSWORD_FIELD_ID = "card-pin"
LINKS_URL = "../links.txt"
COURSES_DIR = 'courses'

driver = webdriver.Chrome()
driver.wait = WebDriverWait(driver, 10)

def open_page(link):
    driver.get(link)

def enter_credentials(username, password, username_field_id, password_field_id):
    number_field = driver.find_element_by_id(username_field_id)
    number_field.send_keys(username)

    password_field = driver.find_element_by_id(password_field_id)
    password_field.send_keys(password)

    password_field.submit()

def download_courses(links_url):
    if not os.path.exists(COURSES_DIR):
        os.mkdir(COURSES_DIR)
    os.chdir(COURSES_DIR)

    for link in open(links_url):
        if link != '':
            download_course(link)

def download_course(link):
    driver.get(link)

    course_title_element = driver.find_element_by_css_selector('.default-title')
    course_title = course_title_element.text

    print("Downloading {title}...".format(title = course_title))

    if not os.path.exists(course_title):
        os.mkdir(course_title)
    os.chdir(course_title)

    chapter_lis = driver.find_elements_by_css_selector('.course-toc > li')
    chapters = get_chapters(chapter_lis)
    download_chapters(chapters)

    os.chdir('..')

    print("{title} complete.".format(title = course_title))

def get_chapters(chapter_lis):
    chapters = []

    for chapter_li in chapter_lis:
        chapter_details = get_chapter_details(chapter_li)
        chapters.append(chapter_details)

    return chapters

def get_chapter_details(chapter_li):
    chapter_header = chapter_li.find_element_by_css_selector('.chapter-row h4')
    chapter_header_text = chapter_header.text

    video_links = chapter_li.find_elements_by_css_selector('.video-name')
    video_urls = []
    for video_link in video_links:
        video_title = video_link.text
        video_url = video_link.get_attribute('href')
        video_info = (video_title, video_url)
        video_urls.append(video_info)

    return (chapter_header_text, video_urls)

def download_chapters(chapters):
    for chapter in chapters:
        download_chapter(chapter)

def download_chapter(chapter):
    CHAPTER_TITLE_INDEX = 0
    VIDEO_LIST_INDEX = 1

    chapter_title = chapter[CHAPTER_TITLE_INDEX]
    video_list = chapter[VIDEO_LIST_INDEX]

    print("  Downloading {chapter}...".format(chapter = chapter_title))

    if not os.path.exists(chapter_title):
        os.mkdir(chapter_title)
    os.chdir(chapter_title)

    for video in video_list:
        download_video(video)

    print("  {chapter} complete.".format(chapter = chapter_title))

    os.chdir('..')

def download_video(video):
    VIDEO_TITLE_INDEX = 0
    VIDEO_PAGE_INDEX = 1

    video_title = video[VIDEO_TITLE_INDEX]
    video_filename = video_title + '.mp4'
    video_page = video[VIDEO_PAGE_INDEX]

    if not os.path.exists(video_filename):
        print("    Downloading {title}...".format(title = video_title))
        video_url = get_video(video_page)
        save_video(video_title, video_url)
        print("    {title} complete.".format(title = video_title))
    else:
        print("    {title} exists.".format(title = video_title))

def get_video(video_page):
    driver.get(video_page)

    play_button = driver.find_element_by_css_selector('.banner-play-icon')
    play_button.click()

    settings_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "player-settings")))
    settings_button.click()

    hd_link = driver.find_element_by_css_selector('.stream-qualities li:last-of-type a')
    hd_link.click()

    video_element = driver.find_element_by_css_selector('video')
    video_url = video_element.get_attribute('data-src')

    return video_url

def save_video(video_title, video_url):
    video_file = urllib2.urlopen(video_url)
    video_data = video_file.read()
    video_filename = video_title + ".mp4"
    with open(video_filename, "wb") as file_writer:
        file_writer.write(video_data)

open_page(LYNDA_URL)
enter_credentials(USERNAME, PASSWORD, USERNAME_FIELD_ID, PASSWORD_FIELD_ID)
download_courses(LINKS_URL)
