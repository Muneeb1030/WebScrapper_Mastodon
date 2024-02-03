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
        
        
        self.driver.close()
