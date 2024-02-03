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
from datetime import date

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
        self.Pages = self.driver.find_elements(By.XPATH,"//*[@class = 'account__section-headline']//a")
        
        self.CreateDirectories()
        #self.pasrse_HashTags(self.Pages[1])
        self.parse_News(self.Pages[2])
        
        self.driver.close()

    
    def parse_News(self,page):
        self.driver.get(page.get_attribute("href"))
        sleep(3)
        
        CSVPath = os.path.join('output_data\\News\\NewsData.csv')
        
        try:
            df = pd.read_csv(CSVPath)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Publisher', 'PublishingDate','SharedInfo','Title','ThumbnailURL'])

        News = self.driver.find_elements(By.CLASS_NAME, "story")
        print(len(News))
        new_data_list = []
        
        for news in News:
            URL = news.find_element(By.XPATH, './/*[@class = "story__thumbnail"]//img').get_attribute('src')
            Title = news.find_element(By.XPATH, './/*[@class = "story__details__title"]').text
            try:
                publishing_date = news.find_element(By.XPATH, './/*[@class = "story__details__publisher"]/time').get_attribute('title')
            except:
                publishing_date = date.today().strftime("%B %d, %Y")
            new_data = {
                'Publisher': news.find_element(By.XPATH, './/*[@class = "story__details__publisher"]/span').text,
                'PublishingDate': publishing_date,
                'SharedInfo': news.find_element(By.XPATH, './/*[@class = "story__details__shared"]').text,
                'Title': Title,
                'ThumbnailURL': URL
            }
            self.download_image(URL,Title,os.path.join('output_data\\News'))
            new_data_list.append(new_data)
            
        if new_data_list:
            df = pd.concat([df, pd.DataFrame(new_data_list)], ignore_index=True)
        
        df.to_csv(CSVPath, index=False,mode='a', header=not pd.io.common.file_exists(CSVPath))
        self.driver.back()
        sleep(3)    
    
    def download_image(self, image_url, Title,Path):
        download = requests.get(image_url, stream=True)

        Title = re.sub(r'[^\w\s]', '', Title)
        
        image_path = os.path.join(Path, f'{Title}.jpg')

        with open(image_path, 'wb') as f:
            for chunk in download.iter_content(chunk_size=128):
                f.write(chunk)
    
    def pasrse_HashTags(self,page):
        self.driver.get(page.get_attribute("href"))
        sleep(3)
        
        CSVPath = os.path.join('output_data\\Hashtag.csv')
        
        try:
            df = pd.read_csv(CSVPath)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['HashTag', 'Trending','Date'])

        Items = self.driver.find_elements(By.CLASS_NAME, "trends__item")
        new_data_list = []
        
        for item in Items:
            new_data = {
                'HashTag': item.find_element(By.XPATH, './/*[@class="trends__item__name"]/a').text,
                'Trending': item.find_element(By.XPATH, './/*[@class="trends__item__name"]/span').text,
                'Date': date.today().strftime("%B %d, %Y")
            }
            new_data_list.append(new_data)

        if new_data_list:
            df = pd.concat([df, pd.DataFrame(new_data_list)], ignore_index=True)
        
        df.to_csv(CSVPath, index=False,mode='a', header=not pd.io.common.file_exists(CSVPath))
        self.driver.back()
        sleep(3)

    def CreateDirectories(self):
        output_directory = 'output_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        articles_sub_directory = f'{output_directory}/News'
        if not os.path.exists(articles_sub_directory):
            os.makedirs(articles_sub_directory)  
        
        images_sub_directory = f'{output_directory}/Timeline'
        if not os.path.exists(images_sub_directory):
            os.makedirs(images_sub_directory) 