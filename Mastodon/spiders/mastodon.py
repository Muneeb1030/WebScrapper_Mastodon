from scrapy import Spider
from time import sleep

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import requests
import re
import pandas as pd

chrome_driver_path = r"D:\Projects\Assignments\DataScience\Web Scrapers\chromedriver.exe"

class MastodonSpider(Spider):
    name = "mastodon"
    allowed_domains = ["mastodon.social"]
    start_urls = ["https://mastodon.social/explore"]
     
    def parse(self,response):
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.driver.get("https://mastodon.social/explore")
        
        self.CreateDirectories()
        
        self.driver.close()

    
    



    def CreateDirectories(self):
        output_directory = 'output_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        articles_sub_directory = f'{output_directory}/detailed_news_articles'
        if not os.path.exists(articles_sub_directory):
            os.makedirs(articles_sub_directory)  
        
        images_sub_directory = f'{output_directory}/news_articles_Images'
        if not os.path.exists(images_sub_directory):
            os.makedirs(images_sub_directory) 