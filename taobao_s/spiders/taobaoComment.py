# -*- coding: utf-8 -*-
import scrapy
from taobao_s.items import TaobaoCommentItem
import random
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
import re
import json
from taobao_s.tools import  register, not_item_taobao_com, skulist_find, get_id


class TaobaocommentSpider(scrapy.Spider):
    name = 'taobaoComment'
    #allowed_domains = ['taobao.com']
    #start_urls = ['http://taobao.com/']
    base_url = ['https://s.taobao.com/search?q=']
    pages = 100
    re_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT pages6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'referer': 'https://www.taobao.com/',
        'accept-encoding': 'gzip, deflate, b',
    }
    i = 0

    def start_requests(self):
        keys = self.settings.get('KEYS')
        self.browser, self.list = register()  # list 是包含登录后获得的cookies的字典
        self.browser.get(self.base_url[0] + keys)  # 访问页面 （搜索“手机”关键字页面）
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        url_i = self.browser.current_url
        html = self.browser.page_source

        # 开始爬取
        print('-------start scrapy--------')
        yield scrapy.Request(url=self.base_url[0] + keys, headers=self.re_headers, cookies=self.list,
                             callback=self.parse,
                             meta={'html': html, 'i': self.i, 'url': url_i})
    def parse(self, response):
        time.sleep(10)
        html = response.meta.get('html')
        i = response.meta.get("i")
        url_i = response.meta.get("url")
        i += 1
        if i > 10:
            return
        try:
            soup = BeautifulSoup(html, 'html.parser') #html解析器
            lists = soup.select('#mainsrp-itemlist > div > div > div > div') #获取该页面所有商品列表
            for list in lists:
                url_detail = list.find('a', attrs={'class': "pic-link J_ClickStat J_ItemPicA"}, href=not_item_taobao_com)
                if url_detail:
                    url_detail = 'https:'+url_detail.attrs.get('href')
                    #url_detail='https://detail.tmall.com/item.htm?id=598079959720&cm_id=140105335569ed55e27b&abbucket=7&sku_properties=10004:653780895;5919063:6536025'
                    self.browser.get(url_detail)  # 访问指定手机详情页面
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    url_i_detail = self.browser.current_url
                    html_detail = self.browser.page_source
                    header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
                    yield scrapy.Request(url=url_detail, headers=header, cookies=self.list, callback=self.parse_detail,
                                          meta={'html': html_detail, 'url': url_i_detail}, dont_filter=True)
            print('本页爬完。。。。。。！！！！！')
            button = self.browser.find_elements(By.XPATH, '//a[@class="J_Ajax num icon-tag"]')[-1]  #找到“下一页”按钮
            button.click()
            time.sleep(random.random()*2)
            # 移动到页面最底部
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            url_i = self.browser.current_url
            html = self.browser.page_source  #获取网页源码
            yield scrapy.Request(url=response.url, headers=self.re_headers, callback=self.parse, cookies=self.list,
                                 meta={'html': html, 'i': i, 'url': url_i}, dont_filter=True)
        except Exception as e:
            time.sleep(10)
            print(e)
            self.browser.close()
            self.browser, self.list = register()
            self.browser.get(url=url_i)
            time.sleep(random.random()*2)
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            html = self.browser.page_source
            yield scrapy.Request(url=response.url, headers=self.re_headers, callback=self.parse, cookies=self.list,
                                 meta={'html': html, 'i': i, 'url': url_i}, dont_filter=True)

    def parse_detail(self, response):
        #用于获取商品的详细信息
        time.sleep(10)
        html = response.meta.get('html')
        url_i = response.meta.get("url")
        soup = BeautifulSoup(html, 'html.parser')  # html解析器
        product_id = re.search('([?&])id=(.*?)&', url_i).group(2)
        shop_id = soup.find('input', id='dsr-userid')['value']
        header = {'Sec-Fetch-Mode': 'no-cors',
                  'referer': url_i,
                  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        url_comment = 'https://rate.tmall.com/list_detail_rate.htm?currentPage=%d&itemId=%s&sellerId=%s'%(1,product_id,shop_id)
        # 构造url的过程，get请求的参数
        params = {'currentPage': 1,
                  'itemId': product_id,
                  'sellerId': shop_id,
                  }
        yield scrapy.Request(url=url_comment, headers=header, cookies=self.list, callback=self.parse_commentFirst,
                             meta=params, dont_filter=True)

    def parse_commentFirst(self, response):
        time.sleep(10)
        start = re.search('{', response.text).span()
        response_json = json.loads(response.text[start[0]:-1])
        maxPage = response_json['rateDetail']['paginator']['lastPage']
        item_id, seller_id = get_id(response.url)

        header = {
            'Sec-Fetch-Mode': 'no-cors',
            'referer': 'https://detail.tmall.com/item.htm?spm=a230r.1.14.6.670d6fbeYKDOzW&id=598079959720&cm_id=140105335569ed55e27b&abbucket=6&sku_properties=10004:653780895;5919063:6536025',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        for p in range(maxPage):
            url_rate = 'https://rate.tmall.com/list_detail_rate.htm?currentPage=%d&itemId=%s&sellerId=%s'%(p+1,item_id,seller_id)
            params = {'currentPage': p+1,
                      'itemId': item_id,
                      'sellerId': seller_id,
                      }
            yield scrapy.Request(url=url_rate, cookies=self.list,  headers=header, callback=self.parse_commentSecond,
                                 meta=params, dont_filter=True)

    def parse_commentSecond(self, response):
        start = re.search('{', response.text).span()
        response_json = json.loads(response.text[start[0]:-1])
        item_id, seller_id = get_id(response.url)
        comment_item = TaobaoCommentItem()
        comment_item['comment_info'] = response_json
        comment_item['item_id'] = item_id
        return comment_item

    def close(self, spider, reason):
        spider.browser.close()