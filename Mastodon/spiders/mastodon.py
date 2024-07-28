from scrapy import Spider
from time import sleep

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

#Additional libraries for proper working
import os
import requests
import re
import pandas as pd
from datetime import date

# Specify the path to the Chrome driver executable
chrome_driver_path = r"D:\Projects\Assignments\DataScience\Web Scrapers\chromedriver.exe"

class MastodonSpider(Spider):
    name = "mastodon"
    allowed_domains = ["mastodon.social"]
    start_urls = ["https://mastodon.social/explore"]
    
    # Initialize class variables for storing scraped data and counting content without text
    new_entry_list = []
    counter_for_no_content = 0 
    
    def parse(self, response):
        # Set up the Chrome WebDriver
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.driver.get(response.url)
        
        # Use WebDriverWait to ensure the presence of elements before proceeding
        self.Pages = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@class = 'account__section-headline']//a")))
        
        # Create directories for storing scraped data
        self.CreateDirectories()
        
        # Call functions to parse hashtags, news, and perform scrolling
        self.parse_hashtags(self.Pages[1])
        sleep(2)
        #Avoiding Stale Element Error
        self.Pages = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@class = 'account__section-headline']//a")))
        self.parse_news(self.Pages[2])
        sleep(1)
        #Avoiding Stale Element Error
        self.Pages = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@class = 'account__section-headline']//a")))
        self.scrolling(self.Pages[0])
        
        # Close the Chrome WebDriver
        self.driver.close()
   
    def scrolling(self, page):
        # Opening the Timeline Tab
        self.driver.get(page.get_attribute("href"))
        sleep(2) # wait

        # In this context, each post have a number as an id, to traverse each post once we are going to use this variable
        self.count = 1

        #scrollling logic
        while True:
            try: # When the count value exceeds the post count, the except will break the loop. Hence the scrolling stops
                # getting each post 
                target_element = self.driver.find_element(By.XPATH, f'.//*[@aria-posinset="{self.count}"]')
                target_element.location_once_scrolled_into_view # Making the post Focused
                # The challenges i was facing here is that post which is visible on screen can only be scrapped
                # hence making each to focus, solves this problem
                sleep(2) # wait
                # Extract Headline from the post, so that each post's csv and media file can be named same
                content = self.extract_headline(target_element)
                # Parse and process the timeline
                self.parse_timeline(target_element, content)
                # Opens a post, retrieves reactions, and updates an individual post CSV file.
                self.open_post(target_element, content)
                self.count += 1
            except NoSuchElementException:
                break

    def extract_headline(self, target_element):
        try:
            content = target_element.find_element(By.CLASS_NAME, 'status__content').text
            return ' '.join(content.split())
        except NoSuchElementException:
            return "None"

    def parse_timeline(self, post, content):
        csv_path = 'output_data/Timeline/ScrappedTimeline.csv'

        # Extract author information
        try:
            author = post.find_element(By.XPATH, './/*[@class="display-name"]/span').text
        except NoSuchElementException:
            author = "None"

        # Extract upload time information
        try:
            upload_time = post.find_element(By.TAG_NAME, 'time').get_attribute('title')
        except NoSuchElementException:
            upload_time = "None"

        # Extract active time when scrapped
        try:
            active_time_when_scrapped = post.find_element(By.TAG_NAME, 'time').text
        except NoSuchElementException:
            active_time_when_scrapped = "None"

        # Extract hashtags
        hash_tags = self.extract_tags(post.find_element(By.CLASS_NAME, 'status__wrapper').get_attribute('aria-label'))

        # Extract reply, boost, and favorite counts
        reply = self.get_button_text(post, 'Reply')
        boost = self.get_button_text(post, 'Boost')
        favorite = self.get_button_text(post, 'Favorite')

        # Extract media information
        media_url, media_alt = self.get_media_info(post)

        if media_alt is not None:
            media_alt = ' '.join(media_alt.split())

        # Create a new entry dictionary
        new_entry = {
            'Author': author,
            'UploadTime': upload_time,
            'ActiveTimeWhenScrapped': active_time_when_scrapped,
            'Title': content,
            'Tags': hash_tags,
            'Reply': reply,
            'Boost': boost,
            'Favorite': favorite,
            'ThumbnailDesc': media_alt,
            'ThumbnailURL': media_url
        }

        # Append the new entry to the list
        self.new_entry_list.append(new_entry)

        # Download the image if it is not None
        if media_url != "None":
            self.download_image(media_url, content[:20], os.path.join('output_data/Timeline'))

        # Write to CSV file every 20 entries
        if self.count % 20 == 0:
            try:
                df = pd.read_csv(csv_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=['Author', 'UploadTime', 'ActiveTimeWhenScrapped', 'Title', 'Tags', 'Reply',
                                        'Boost', 'Favorite', 'ThumbnailDesc', 'ThumbnailURL'])
            df = pd.concat([df, pd.DataFrame(self.new_entry_list)], ignore_index=True)
            df.to_csv(csv_path, index=False, mode='a', header=not os.path.isfile(csv_path))

            # Clear the list to avoid duplicates
            self.new_entry_list.clear()

    def get_button_text(self, post, button_title):
        try:
            button_text = post.find_element(By.XPATH, f'.//*[@class="status__action-bar"]/button[@title="{button_title}"]').text
            return button_text if button_text != "" else "0"
        except NoSuchElementException:
            return "0"

    def get_media_info(self, post):
        # Gets the media information from a post.
        try: # if img tag available
            media_element = post.find_element(By.CLASS_NAME, 'media-gallery')
            media_url = media_element.find_element(By.TAG_NAME, 'img').get_attribute('src')
            media_alt = media_element.find_element(By.TAG_NAME, 'img').get_attribute('alt')
        except NoSuchElementException:
            try: # else if video tag available
                media_element = post.find_element(By.CLASS_NAME, 'media-gallery')
                media_url = media_element.find_element(By.TAG_NAME, 'video').get_attribute('src')
                media_alt = media_element.find_element(By.TAG_NAME, 'video').get_attribute('alt')
            except NoSuchElementException: # if both are un avilable
                media_url = "None"
                media_alt = "None"

        return media_url, media_alt

    def open_post(self, post, Title):
        
        # Click on the 'More' button to access reactions
        post.find_element(By.XPATH, './/*[@class="status__action-bar"]/button[@title="More"]').click()
        sleep(3)

        # List to store entry information
        entry_list = []

        # Click on the 'Reactions' option in the dropdown menu
        self.driver.find_element(By.CLASS_NAME, 'dropdown-menu__item').click()
        sleep(3)

        try:
            # Wait for reactions to be present
            posts = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'status__wrapper')))

            # Iterate through each reaction
            for reaction in posts:
                try:
                    # Extract author information
                    author = reaction.find_element(By.XPATH, './/*[@class="display-name"]/span').text
                except NoSuchElementException:
                    author = "None"

                try:
                    # Extract upload time information
                    upload_time = reaction.find_element(By.TAG_NAME, 'time').get_attribute('title')
                except NoSuchElementException:
                    upload_time = "None"

                try:
                    # Extract active time when scrapped
                    active_time_when_scrapped = reaction.find_element(By.TAG_NAME, 'time').text
                except NoSuchElementException:
                    active_time_when_scrapped = "None"

                try:
                    # Extract content of the reaction
                    content = reaction.find_element(By.CLASS_NAME, 'status__content').text
                    content = ' '.join(content.split())
                except NoSuchElementException:
                    content = "None"

                try:
                    # Extract reply count
                    reply = reaction.find_element(By.XPATH, './/*[@class="status__action-bar"]/button[@title="Reply"]').text
                    reply = reply if reply != "" else "0"
                except NoSuchElementException:
                    reply = "0"

                # Create a new entry dictionary
                new_entry = {
                    'Author': author,
                    'UploadTime': upload_time,
                    'ActiveTimeWhenScrapped': active_time_when_scrapped,
                    'Title': content,
                    'Reply': reply
                }

                # Append the new entry to the list
                entry_list.append(new_entry)

        except Exception as e:
            # Handle exceptions (e.g., timeout or missing elements)
            print(f"Error: {e}")

        # Generate a sanitized title for file naming
        sanitized_title = re.sub(r'[^\w\s]', '', Title[:20])
        path = os.path.join(f'output_data/Timeline/IndividualPost/{sanitized_title}.csv')

        try:
            # Read the existing CSV file or create a new one
            df = pd.read_csv(path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Author', 'UploadTime', 'ActiveTimeWhenScrapped', 'Title', 'Reply'])

        # Concatenate the new entries to the DataFrame and write to CSV
        df = pd.concat([df, pd.DataFrame(entry_list)], ignore_index=True)
        df.to_csv(path, index=False, mode='a', header=not os.path.isfile(path))

        # Clear the entry list to avoid duplicates
        entry_list.clear()

        # Navigate back to the previous page
        self.driver.back()  
        
    def extract_tags(self, text):
        # Define a regex pattern to match a specific format in the text
        pattern = r'^(.*?), (.+), (.+), (.+)$'
        # Attempt to match the pattern in the given text
        match = re.match(pattern, text)
        if match:
            # Extract the part of the matched text containing tags, date, and account
            content_tags_datetime_account = match.group(2)
            # Find all hashtags using another regex pattern
            tags_list = re.findall(r'#\w+', content_tags_datetime_account)
            # Concatenate the extracted hashtags into a single string
            tags = ' '.join(tags_list)
            return tags
        else:
            # Return "None" if the pattern is not matched
            return "None"
       
    def parse_news(self, page):
        
        # Opening the News Tab
        self.driver.get(page.get_attribute("href"))
        sleep(3) # wait

        # Paths used for saving file
        csv_path = 'output_data/News/NewsData.csv'
        # Data Header (the content to be scrapped)
        columns = ['Publisher', 'PublishingDate', 'SharedInfo', 'Title', 'ThumbnailURL']
        # Getting relevant HTML content from the page
        news_elements = self.driver.find_elements(By.CLASS_NAME, "story")
        
        # From each Item in the Items Extracting the desired data
        if len(news_elements) > 0:
            new_data_list = []
            # From each Item in the Items Extracting the desired data
            for news in news_elements:
                
                Publisher = news.find_element(By.XPATH, './/*[@class="story__details__publisher"]/span').text
                
                # Some posts does not have time tag, in that case assigning the time of scrapping
                try:
                    publishing_date = news.find_element(By.XPATH, './/*[@class = "story__details__publisher"]/time').get_attribute('title')
                except:
                    publishing_date = date.today().strftime("%B %d, %Y")
                
                SharedInfo = news.find_element(By.XPATH, './/*[@class="story__details__shared"]').text
                Headline = news.find_element(By.XPATH, './/*[@class="story__details__title"]').text
                
                thumbnail_element = news.find_element(By.XPATH, './/*[@class="story__thumbnail"]//img')
                thumbnail_element_URL = thumbnail_element.get_attribute('src')

                new_data = {
                    'Publisher': Publisher,
                    'PublishingDate': publishing_date,
                    'SharedInfo': SharedInfo,
                    'Title': Headline,
                    'ThumbnailURL': thumbnail_element_URL
                }
                new_data_list.append(new_data)
                # Downloading Images (Thumbnails) of the News Articles
                self.download_image(thumbnail_element_URL, new_data['Title'], os.path.join('output_data/News'))
                

            # Make sure there is already a file or else create a new file to avaoid exception           
            try:
                df = pd.read_csv(csv_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=columns)
            
            # Adding data to dataframe and then writing in the csv file
            df = pd.concat([df, pd.DataFrame(new_data_list)], ignore_index=True)
            df.to_csv(csv_path, index=False, mode='a', header=not os.path.isfile(csv_path))
        # Going Back    
        self.driver.back()
              
    def download_image(self, image_url, Title, Path):
        # Download the image in chunks to handle large files efficiently
        download = requests.get(image_url, stream=True)
        # Sanitize the title by removing special characters
        title = re.sub(r'[^\w\s]', '', Title)
        # Construct the full path for saving the image with a sanitized filename
        image_path = os.path.join(Path, f'{title}.jpg')
        # Open the image file in binary write mode and write the downloaded content
        with open(image_path, 'wb') as f:
            for chunk in download.iter_content(chunk_size=128):
                f.write(chunk)
    
    def parse_hashtags(self, page):
        # Opening the HashTag Tab
        self.driver.get(page.get_attribute("href"))
        sleep(3) #wait

        # Paths used for saving file 
        csv_path = 'output_data/Hashtag.csv'
        # Data Header (the content to be scrapped)
        columns = ['HashTag', 'Trending', 'Date']

        # Getting relevant HTML content from the page
        items = self.driver.find_elements(By.CLASS_NAME, "trends__item")
        
        # if anything returns, only then we need following processing
        if len(items) > 0:
            # From each Item in the Items Extracting the desired data
            new_data_list = [
                {
                    'HashTag': item.find_element(By.XPATH, './/*[@class="trends__item__name"]/a').text,
                    'Trending': item.find_element(By.XPATH, './/*[@class="trends__item__name"]/span').text,
                    'Date': date.today().strftime("%B %d, %Y")
                }
                for item in items
            ]
            
            # Make sure there is already a file or else create a new file to avaoid exception
            try:
                df = pd.read_csv(csv_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=columns)
            
            # Adding data to dataframe and then writing in the csv file    
            df = pd.concat([df, pd.DataFrame(new_data_list)], ignore_index=True)
            df.to_csv(csv_path, index=False, mode='a', header=not os.path.isfile(csv_path))

        # Going Back
        self.driver.back()

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
            
        
        if not os.path.exists('output_data\\Timeline\\IndividualPost'):
            os.makedirs('output_data\\Timeline\\IndividualPost') 