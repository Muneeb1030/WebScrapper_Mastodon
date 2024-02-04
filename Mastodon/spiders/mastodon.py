from scrapy import Spider
from time import sleep

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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
    new_entry_list =[]
    def parse(self,response):
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.driver.get("https://mastodon.social/explore")
        self.Pages = WebDriverWait(self.driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH,"//*[@class = 'account__section-headline']//a")))
        
        self.CreateDirectories()
        #self.pasrse_HashTags(self.Pages[1])
        self.Scrolling(self.Pages[0])
        #self.parse_Timeline()
        
        
        self.driver.close()
   
    def Scrolling(self,page):
        self.driver.get(page.get_attribute("href"))
        
        CSVPath = os.path.join('output_data\\Timeline\\ScrappedTimeline.csv')
        
        self.count = 1;
        Posts = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH,'//*[@role="feed"]/article')))
        scroll = True
        while scroll:
            for _ in Posts:
                try:
                    target_element = self.driver.find_element(By.XPATH, f'.//*[@aria-posinset="{self.count}"]')
                    target_element.location_once_scrolled_into_view
                    
                    sleep(2)
                    self.count+=1
                    self.parse_Timeline(target_element, CSVPath)
                except NoSuchElementException:
                    scroll =False
                    break

    def parse_Timeline(self, post,Path):
        
        try:
            Author = post.find_element(By.XPATH,'.//*[@class="display-name"]/span').text
        except:
            Author="None"

        try:
            UploadTime = post.find_element(By.TAG_NAME,'time').get_attribute('title')
        except:
            UploadTime="None"
        
        try:
            ActiveTimeWhenScrapped = post.find_element(By.TAG_NAME,'time').text
        except:
            ActiveTimeWhenScrapped="None"
        
        try:
            content = post.find_element(By.CLASS_NAME,'status__content').text
            content = ' '.join(content.split())
        except:
            content ="None"
        
        hash_tags = self.extract_tags(post.find_element(By.CLASS_NAME, 'status__wrapper').get_attribute('aria-label'))  
        
        try:
            Reply = post.find_element(By.XPATH,'.//*[@class = "status__action-bar"]/button[@title="Reply"]').text
        except:
            Reply="0"
            
        try:
            Boost =  post.find_element(By.XPATH,'.//*[@class = "status__action-bar"]/button[@title="Boost"]').text
        except:
            Boost="0"
            
        try:
            Favorite = post.find_element(By.XPATH,'.//*[@class = "status__action-bar"]/button[@title="Favorite"]').text
        except:
            Favorite="0"
         
        try:
            media_url = post.find_element(By.CLASS_NAME, 'media-gallery').find_element(By.TAG_NAME, 'img').get_attribute('src')
            media_alt = post.find_element(By.CLASS_NAME, 'media-gallery').find_element(By.TAG_NAME, 'img').get_attribute('alt')
        except NoSuchElementException:
            try:
                media_url = post.find_element(By.CLASS_NAME, 'media-gallery').find_element(By.TAG_NAME, 'video').get_attribute('src')
                media_alt = post.find_element(By.CLASS_NAME, 'media-gallery').find_element(By.TAG_NAME, 'video').get_attribute('alt')
            except NoSuchElementException:
                media_url = "None"  
                media_alt = "None"

        if media_alt != "None":
            media_alt= ' '.join(media_alt.split())
                 
        new_entry = {
                'Author': Author,
                'UploadTime': UploadTime,
                'ActiveTimeWhenScrapped': ActiveTimeWhenScrapped,
                'Title': content,
                'Tags': hash_tags,
                'Reply': Reply,
                'Boost': Boost,
                'Favorite': Favorite,
                'ThumbnailDesc': media_alt,
                'ThumbnailURL': media_url
            }
        self.new_entry_list.append(new_entry)
        if media_url != "None":
            self.download_image(media_url,content[:20],os.path.join('output_data\\Timeline'))

        if self.count % 20 == 0:
            print(self.new_entry_list)
            try:
              df = pd.read_csv(Path)
            except FileNotFoundError:
              df = pd.DataFrame(columns=['Author', 'UploadTime','ActiveTimeWhenScrapped','Title','Tags','Reply','Boost','Favorite','ThumbnailDesc','ThumbnailURL']) 
            df = pd.concat([df,pd.DataFrame(self.new_entry_list)], ignore_index=True)
            df.to_csv(Path, index=False, mode='a', header=not pd.io.common.file_exists(Path))
            self.new_entry_list.clear()
        
    def extract_tags(self, text):
        pattern = r'^(.*?), (.+), (.+), (.+)$'
        match = re.match(pattern, text)

        if match:
            content_tags_datetime_account = match.group(2)
            tags_list = re.findall(r'#\w+', content_tags_datetime_account)
            tags = ' '.join(tags_list)
            return tags
        else:
            return "None"
       
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
        
        self.parse_Timeline(self.Pages[0])
              
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
        
        self.parse_News(self.Pages[2])

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