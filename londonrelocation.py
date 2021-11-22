import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                          callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            # print("Area URL", area_url)
            yield Request(url=area_url,
                          callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        area_urls = response.xpath('.//div[contains(@class,"pagination-wrap")]//a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url,callback=self.parse_area_pages_titles)

    def parse_area_pages_titles(self, response):
        property_info_titles = response.xpath('.//div[contains(@class,"test-inline")]//h4/a/text()').extract()
        property_info_prices = response.xpath('.//div[contains(@class,"test-inline")]//h5/text()').extract()
        property_info_urls = response.xpath('.//div[contains(@class,"test-inline")]//a/@href').extract()
        what_to_print = []
        for i in range(len(property_info_titles)):
            what_to_print.append(
                {
                    "Title":str(property_info_titles[i]).strip(),
                    "Price":str(property_info_prices[i]).strip().replace("\u00a3 ", ""),
                    "URL":str(property_info_urls[i]).strip()
                }
            )
        for item in what_to_print:
            property = ItemLoader(item=Property())
            property.add_value('title', item.get("Title"))
            property.add_value('price', item.get("Price"))  # 420 per week
            property.add_value('url', str("https://londonrelocation.com" + item.get("URL")))
            yield property.load_item()
