import scrapy
import re
import os
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from restaurant_scraper.spiders import file
from bs4 import BeautifulSoup

from scrapy.dupefilters import RFPDupeFilter


class MyDupeFilter(RFPDupeFilter):
    def log(self, request, spider):
        file.write(f'{request.url} {str(request.headers.get("REFERER", "None"), "utf-8")}\n')
        super(MyDupeFilter, self).log(request, spider)


class RestaurantSpider(CrawlSpider):
    name = "restaurant_spider"
    start_urls = ['https://caviar.com', 'https://www.eater.com/',
                  'https://www.restaurant-hospitality.com/', 'https://www.restaurantji.com/tx/richardson/',
                  'https://getbento.com/', 'https://www.dineatthedistrict.com/',
                  'https://eat.chownow.com/discover/', 'https://gopuff.com/us/home?redirected_to_novus=true',
                  'https://www.ubereats.com', 'https://www.swiggy.com/restaurants', 'https://www.grubstreet.com/',
                  'https://www.restaurants.com/', 'http://www.restaurantnews.com/',
                  'https://directory.dmagazine.com/search/?sections=Restaurants&awards=50+Best+Restaurants',
                  'https://postmates.com/?irgwc=1&clickId=2g7SXETp3xyITYNTtE0xB1uAUkGVC9WPB21lxg0&utm_source=impact&'
                  'utm_medium=impact&utm_campaign=ImpactRadius_AFF_AFF_ImpactRadius_All_All_CPM_All_All_Digital%20T'
                  'rends.&pid=impactradius_int',  'https://familydestinationsguide.com/',
                  'https://www.tripsavvy.com/food-travel-4138707',
                  'https://www.foodnetwork.com/restaurants/photos/most-popular-dish-at-americas-top-chain-restaurants',
                  'https://dallas.eater.com/maps/best-restaurants-in-richardson',
                  'https://goroundrock.com/', 'https://trip101.com/article/indian-restaurants-in-richardson',
                  'http://richardsoneats.com/', 'https://www.opentable.com/','https://restaurantsnearmenow.org/',
                  'https://www.businessinsider.com/the-20-best-chain-restaurants-in-america-2016-7',
                  'https://deliveroo.co.uk/restaurants/london/strand?fulfillment_method=DELIVERY&geohash=gcpvj0e6mbuq',
                  'https://www.ranker.com/list/the-top-bar-and-grill-restaurant-chains/restaurant-chains',
                  'https://www.telecomcorridor.com/news/new-restaurants-at-cityline-richardson-restaurant-park-and-more',
                  'https://www.bestfoodfeed.com/dallas-tx', 'https://guide.michelin.com/us/en/restaurants',
                  'https://www.eatthis.com/restaurants/', 'https://www.goldbelly.com/',
                  'https://www.dallasobserver.com/best-of/2021/readers-choice/best-all-around-restaurant-north-dallas-'
                  'addison-richardson-farmers-branch-12431092', 'https://www.thrillist.com/eat',
                  'https://www.travelandleisure.com/food-drink',
                  'https://tampamagazines.com/best-restaurants-list-2022/', 'https://www.yummly.com/']
    rules = (Rule(LinkExtractor(),
                  callback='parse_start_url',
                  follow=True),)
    ctr = 1
    N = 150000
    if not os.path.exists("crawl_data"):
        os.mkdir("crawl_data")

    def remove_tags(self, html):
        # parse html content
        soup = BeautifulSoup(html, "html.parser")

        for data in soup(['style', 'script']):
            # Remove tags
            data.decompose()

        # return data by retrieving the tag content
        return ' '.join(soup.stripped_strings)

    def parse_start_url(self, response, **kwargs):
        body_txt = response.xpath("//body").get()
        # selector = scrapy.Selector(text=body_txt, type="html")  # Create HTML doc from HTML text
        # all_body_txt = selector.xpath('//body/descendant-or-self::*/text()').getall()
        # body = re.sub(r'\W+', ' ', ''.join(_ for _ in all_body_txt).strip())
        body_txt = body_txt.split()
        body = " ".join(body_txt)
        # print(body)
        # body = re.sub("<script>.*</script>", "", body)
        # body = re.sub('<[^>]+>', '', body)
        body = self.remove_tags(body)
        # body = re.sub("[\\d+]", "", body)
        if body:
            title_txt = response.xpath("//title").get()
            selector = scrapy.Selector(text=title_txt, type="html")  # Create HTML doc from HTML text
            all_title_txt = selector.xpath('//title/descendant-or-self::*/text()').getall()
            title = re.sub(r'\W+', ' ', ''.join(_ for _ in all_title_txt).strip())
            page_url = response.url
            with open(f'crawl_data/{self.ctr}.txt', 'w') as f:
                f.write(f'{title}\n{page_url}\n{body}')
            # with open('links.txt', 'a') as f:
            file.write(f'{page_url} {str(response.request.headers.get("REFERER", "None"), "utf-8")} {self.ctr}\n')
            self.log(f'Saved url content [{page_url}] at [{self.ctr}.txt]')
            if self.ctr % 1000 == 0:
                print(self.ctr)
            if self.ctr > self.N:
                raise CloseSpider(f"Scraped {self.N} items. Eject!")
            self.ctr += 1
