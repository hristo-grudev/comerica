import scrapy

from scrapy.loader import ItemLoader

from ..items import ComericaItem
from itemloaders.processors import TakeFirst


class ComericaSpider(scrapy.Spider):
	name = 'comerica'
	start_urls = ['https://comerica.mediaroom.com/news-releases']

	def parse(self, response):
		post_links = response.xpath('//div[@class="wd_item_wrapper"]')
		for post in post_links:
			url = post.xpath('.//a/@href').get()
			date = post.xpath('.//div[@class="wd_date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[@aria-label="Show next page"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="wd_title wd_language_left"]/text()').get()
		description = response.xpath('//div[@class="wd_body wd_news_body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ComericaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
