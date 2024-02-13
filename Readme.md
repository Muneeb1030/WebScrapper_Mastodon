# Mastodon Social Platform Scraper

## Overview
The Mastodon Social Platform Scraper is a Python-based web scraping tool designed to explore and extract valuable data from the Mastodon social platform. Leveraging the Scrapy framework for structured data extraction and Selenium for dynamic content handling, this project provides a comprehensive solution for harvesting information from Mastodon's explore page.

## Key Features
1. **Hashtag Scraper:** Extracts trending hashtags on Mastodon, providing insights into popular topics.
2. **News Scraper:** Collects news data from the explore page, facilitating the analysis of current events.
3. **Timeline Scraper:** Dynamically scrolls through the timeline, scraping post details and reactions for a holistic view of user activity.
4. **Efficient Data Management:** Utilizes Pandas for organized and efficient storage of scraped data.

## Requirements
- **Python 3.x**
- **Scrapy**
- **Selenium**
- **Chrome WebDriver**

## Getting Started
1. **Clone the Repository:**
    ```
    git clone [YourGitHubProjectLink]
    ```

2. **Install Dependencies:**
    ```
    pip install scrapy selenium pandas requests
    ```

3. **Set Chrome WebDriver Path:**
    Update the `chrome_driver_path` variable in the code with the path to your Chrome WebDriver.

4. **Run the Scraper:**
    ```
    scrapy crawl mastodon
    ```

## Additional Information
- **Customization:**
    - Tailor the scraper to your needs by modifying the Scrapy spiders.
- **GitHub Repository:**
    - Explore, contribute, and stay updated on the [GitHub repository](https://github.com/Muneeb1030/WebScrapper_Mastodon.git).


## Disclaimer
This project is intended for educational purposes and strictly adheres to Mastodon's terms of service. Users are advised to deploy the scraper responsibly and in compliance with platform policies.

## Additional Resources

Explore the project in detail through my [Medium blog](https://medium.com/@m.muneeb.ur.rehman.2000/exploring-mastodon-a-web-scraping-journey-with-scrapy-and-selenium-f96bf4af7029), where I share insights, motivation, and in-depth explanations about the Mastodon Social Platform Scraper.

## Contributors
- M Muneeb ur Rehman

Feel free to fork, contribute, and enhance the capabilities of this Mastodon scraper. Happy scraping! 🌐💻
