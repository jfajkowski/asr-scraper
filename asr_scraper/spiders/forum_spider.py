import scrapy

BASE_URL = 'http://elka.mine.nu/'
FORM_DATA = {
    'username': '',
    'password': '',
    'login': 'Zaloguj'
}
FORUM_IDS = range(1, 1000)


class Spider(scrapy.Spider):
    name = "forum"
    start_urls = [BASE_URL]

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//input[@name="login"]',
            formdata=FORM_DATA,
            callback=self.after_login
        )

    def after_login(self, response):
        forum_ids = FORUM_IDS
        for forum_id in forum_ids:
            yield scrapy.Request(url='{}/viewforum.php?f={}'.format(BASE_URL, forum_id),
                                 callback=self.parse_forum,
                                 meta={'forum_id': forum_id})

    def parse_forum(self, response):
        topic_ids = response.xpath('//a[@class="topictitle"]/@href').re('\d+')
        for topic_id in topic_ids:
            yield scrapy.Request(url='{}/viewtopic.php?t={}'.format(BASE_URL, topic_id),
                                 callback=self.parse_topic,
                                 meta={'forum_id': response.meta.get('forum_id'),
                                       'topic_id': topic_id})

        next_page_href = response.xpath('//span[@class="nav"]/a[contains(text(),"Następny")]/@href')
        if next_page_href:
            next_page_href = next_page_href.extract_first()
            yield scrapy.Request(url=BASE_URL + next_page_href,
                                 callback=self.parse_forum,
                                 meta=response.meta)

    def parse_topic(self, response):
        posts = response.xpath('//span[@class="postbody"]')
        for post_id, post in enumerate(posts):
            yield {
                'forum_id': response.meta.get('forum_id'),
                'topic_id': response.meta.get('topic_id'),
                'text': post.xpath('.//text()').extract()
            }

        next_page_href = response.xpath('//span[@class="nav"]/a[contains(text(),"Następny")]/@href')
        if next_page_href:
            next_page_href = next_page_href.extract_first()
            yield scrapy.Request(url=BASE_URL + next_page_href,
                                 callback=self.parse_topic,
                                 meta=response.meta)
