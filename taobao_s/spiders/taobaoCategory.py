# -*- coding: utf-8 -*-
import scrapy
import requests
from bs4 import BeautifulSoup
from taobao_s.items import TaobaoAllCategorysItem
from taobao_s.tools import register

class TaobaocategorySpider(scrapy.Spider):
    name = 'taobaoCategory'
    #allowed_domains = ['taobao.com']
    #start_urls = ['http://taobao.com/']
    base_url = ['https://s.taobao.com/search?q=']

    re_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT pages6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'referer': 'https://www.taobao.com/',
        'accept-encoding': 'gzip, deflate, b',
    }
    def start_requests(self):
        keys = self.settings.get('KEYS')
        self.browser, self.cookies = register()  # 包含登录后获得的cookies的字典
        self.browser.get(self.base_url[0] + keys)  # 访问页面 （搜索“手机”关键字页面）
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        url_i = self.browser.current_url
        html = self.browser.page_source

        # 开始爬取
        print('-------start scrapy--------')
        yield scrapy.Request(url=self.base_url[0] + keys, headers=self.re_headers, cookies=self.cookies,
                             callback=self.parse,
                             meta={'html': html, 'i': 0, 'url': url_i})


    def parse(self, response):

        html = response.meta.get('html')
        item = TaobaoAllCategorysItem()
        soup = BeautifulSoup(html, 'html.parser')
        trade_market = soup.select('#J_NavCommonRowItems_0 > a')
        phone_type = soup.select('#J_NavCommonRowItems_1 > a')
        phone_ROM = soup.select('#J_NavCommonRowItems_2 > a')
        phone_RAM = soup.select('#J_NavCommonRowItems_3 > a')
        item['trade_market_list'] = self.get_category(trade_market)
        item['phone_type_list'] = self.get_category(phone_type)
        item['phone_ROM_list'] = self.get_category(phone_ROM)
        item['phone_RAM_list'] = self.get_category(phone_RAM)
        item['network_type'] = None
        item['cpu_num'] = None
        item['pixel'] = None
        item['os_type'] = None

        return item

    def get_category(self,list):
        lists = []
        for l in list:
            lists.append(l.select_one('span.text').get_text().strip())
        return lists

