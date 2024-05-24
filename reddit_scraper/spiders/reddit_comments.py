import scrapy
import json

class RedditSpider(scrapy.Spider):
    name = "reddit"
    allowed_domains = ["reddit.com"]
    start_urls = ["https://www.reddit.com/r/missouricannabis/new/.json"]

    def parse(self, response):
        data = json.loads(response.text)
        for post in data['data']['children']:
            post_data = post['data']
            post_url = post_data['permalink']
            full_post_url = response.urljoin(post_url + ".json")
            yield scrapy.Request(full_post_url, callback=self.parse_post_comments)
        
        # Paginate to next set of posts
        after = data['data']['after']
        if after:
            next_page = f"https://www.reddit.com/r/missouricannabis/new/.json?after={after}"
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_post_comments(self, response):
        data = json.loads(response.text)
        post_info = data[0]['data']['children'][0]['data']
        post_title = post_info['title']
        post_url = post_info['permalink']
        
        comments = data[1]['data']['children']
        for comment in comments:
            if 'body' in comment['data']:
                yield {
                    'post_title': post_title,
                    'post_url': post_url,
                    'comment': comment['data']['body']
                }