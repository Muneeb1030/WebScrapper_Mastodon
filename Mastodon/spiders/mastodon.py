import scrapy


class MastodonSpider(scrapy.Spider):
    name = "mastodon"
    allowed_domains = ["mastodon.social"]
    start_urls = ["https://mastodon.social/explore"]

    def parse(self, response):
        pass
