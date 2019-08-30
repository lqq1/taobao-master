# -*- coding: utf-8 -*-
import scrapy
import random
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
import re
import json
import requests
from taobao_s.tools import data_cleaning, register, not_item_taobao_com, rateLabel, skulist_find, get_id
from taobao_s.items import TaobaoSItem, TaobaoCommentItem,TaobaoAllCategorysItem



class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    #allowed_domains = ['taobao.com', 'detail.tmall.com']
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
        self.browser,self.cookies= register()  #包含登录后获得的cookies的字典
        self.browser.get(self.base_url[0]+keys)   #访问页面 （搜索“手机”关键字页面）
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        url_i = self.browser.current_url
        html = self.browser.page_source

        #开始爬取
        print('-------start scrapy--------')
        yield scrapy.Request(url=self.base_url[0]+keys, headers=self.re_headers, cookies=self.cookies, callback=self.parse,
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
            if i==1:
                yield self.get_base_category(soup)
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
                    yield scrapy.Request(url=url_detail, headers=header, cookies=self.cookies, callback=self.parse_detail,
                                          meta={'html': html_detail, 'url': url_i_detail}, dont_filter=True)
            print('本页爬完。。。。。。！！！！！')
            button = self.browser.find_elements(By.XPATH, '//a[@class="J_Ajax num icon-tag"]')[-1]  #找到“下一页”按钮
            button.click()
            time.sleep(random.random()*2)
            # 移动到页面最底部
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            url_i = self.browser.current_url
            html = self.browser.page_source  #获取网页源码
            yield scrapy.Request(url=response.url, headers=self.re_headers, callback=self.parse, cookies=self.cookies,
                                 meta={'html': html, 'i': i, 'url': url_i}, dont_filter=True)
        except Exception as e:
            time.sleep(10)
            print(e)
            self.browser.close()
            self.browser, cookies = register()
            self.browser.get(url=url_i)
            time.sleep(random.random()*2)
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            html = self.browser.page_source
            yield scrapy.Request(url=response.url, headers=self.re_headers, callback=self.parse, cookies=cookies,
                                 meta={'html': html, 'i': i, 'url': url_i}, dont_filter=True)

    def parse_detail(self, response):
        # 用于获取商品的详细信息
        time.sleep(10)
        html = response.meta.get('html')
        url_i = response.meta.get("url")
        soup = BeautifulSoup(html, 'html.parser')  # html解析器
        item = TaobaoSItem()  # 创建item 对象
        item['url'] = url_i
        item['product_id'] = re.search('([?&])id=(.*?)&', url_i).group(2)
        item['shop_id'] = soup.find('input', id='dsr-userid')['value']

        item = self.get_phoneInfo(soup, item)
        #yield item   #必须返回item
        # taobaocommentspider=TaobaocommentSpider()
        # taobaocommentspider.parse_detail(response)
        #
        header = {'Sec-Fetch-Mode': 'no-cors',
                  'referer': url_i,
                  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        url_comment = 'https://rate.tmall.com/list_detail_rate.htm?currentPage=%d&itemId=%s&sellerId=%s'%(1,item['product_id'],item['shop_id'])
        # 构造url的过程，get请求的参数
        params = {'currentPage': 1,
                  'itemId': item['product_id'],
                  'sellerId': item['shop_id'],
                  'item': item,
                  }
        #response = requests.get('https://rate.tmall.com/list_detail_rate.htm', cookies=self.cookies, params=params, headers=header).text

        yield scrapy.Request(url=url_comment, headers=header, cookies=self.cookies, callback=self.parse_commentFirst,
                           meta=params, dont_filter=True)


    def get_phoneInfo(self, soup, item):
        list_columns = ['phone_name', 'phone_price', 'sell_num', 'rate_num', 'collect_num', 'shop_name',
                        'shop_type', 'shop_describe', 'shop_service', 'shop_flow', 'describe_rate', 'service_rate',
                        'flow_rate', 'describe_label', 'service_label', 'flow_label', 'shop_year', 'parameters']
        for i in list_columns:
            item[i] = None
        product_info = soup.select_one('#J_DetailMeta > div > div > div ')  # 商品详细信息   是一个list列表，列表中的元素类型是<class 'bs4.element.Tag'>
        if product_info is not None:
            phone_name = product_info.select_one("a[target='_blank']").get_text().strip()  # 名称
            item['phone_name'] = data_cleaning(phone_name)
            item['phone_price'] = product_info.select('span[class="tm-price"]')[-1].get_text().strip()  # 价格

            sell_num = product_info.select_one('ul > li.tm-ind-item.tm-ind-sellCount > div > span.tm-count')
            if sell_num is not None:
                item['sell_num'] = sell_num.get_text().strip()  # 月销售量

            rate_num = soup.select_one('#J_ItemRates > div > span.tm-count')
            if rate_num is not None:
                item['rate_num'] = rate_num.get_text().strip()  # 累计评价数
            collect_num = soup.select_one('#J_CollectCount')
            if collect_num is not None:
                collect_num = collect_num.get_text().strip()  # 收藏人数
                pattern = re.compile('[0-9]*')
                item['collect_num'] = ''.join(re.findall(pattern, collect_num))

        shop = soup.select_one('#shopExtra > div')
        if shop is not None:
            shop_name = shop.select_one("a[class='slogo-shopname'] strong")
            if shop_name is not None:
                shop_name = shop_name.get_text().strip()  # 店铺名称
                item['shop_name'] = data_cleaning(shop_name)

            shop_type = shop.select_one('span[class="flagship-icon-font"]')
            if shop_type is not None:
                shop_type = shop_type.string.strip()  # 货源、销售方式
                item['shop_type'] = data_cleaning(shop_type)
        shop_infos = soup.select_one('#shop-info')
        if shop_infos is not None:
            shop_info = shop_infos.select('div > span[class="shopdsr-score-con"]')
            item['shop_describe'] = shop_info[0].get_text().strip()  # 描述
            item['shop_service'] = shop_info[1].get_text().strip()  # 服务
            item['shop_flow'] = shop_info[2].get_text().strip()  # 物流
            shop_detial = shop_infos.select_one('div[class="extra-info "] > textarea')# 店铺 在同行业中的情况
            if shop_detial is not None:
                textarea_source = shop_detial.get_text()
                # 店铺的评分信息放在标签的text中，而text又是一个html脚本，所以这里需要再次翻译一遍
                item = self.soupTextarea(textarea_source, item)
        #产品配置信息
        item['parameters'] = self.get_parameter(soup)

        return item

    def soupTextarea(self, htmlsource, item):
        souptext = BeautifulSoup(htmlsource, 'html.parser')
        shop_rate = souptext.select_one('span[class="rateinfo"]')
        if shop_rate is not None:
            item['describe_label'], item['describe_rate'] = rateLabel(shop_rate)  # 描述 同行业情况
            item['service_label'], item['service_rate'] = rateLabel(shop_rate)  # 服务同行业情况
            item['flow_label'], item['flow_rate'] = rateLabel(shop_rate)  # 物流 同行业情况

        shop_year = souptext.select_one('span[class="tm-shop-age-num"]')
        if shop_year is not None:
            shop_year = shop_year.get_text().strip()  # 店铺开店时间
            item['shop_year'] = shop_year
        return item



    def get_parameter(self, html):
        product_parameter = html.select_one('#J_Attrs').select_one('table > tbody')
        td_list = product_parameter.find_all('td')
        parameter = {}
        for tag in td_list:
            parameter[tag.previous_sibling.string.strip()] = tag.string.strip()
        return parameter

    def parse_commentFirst(self, response):
        time.sleep(10)
        start = re.search('{', response.text).span()
        item = response.meta['item']
        response_json = json.loads(response.text[start[0]:-1])
        rateCount= response_json['rateDetail']['rateCount']
        item['total_comment'] = rateCount['total']
        item['shop'] = rateCount['shop']
        item['pic_num'] = rateCount['picNum']
        item['used_num'] = rateCount['used']
        item_id, seller_id = get_id(response.url)
        maxPage = response_json['rateDetail']['paginator']['lastPage']
        yield item
        header = {
            'Sec-Fetch-Mode': 'no-cors',
            'referer': 'https://detail.tmall.com/item.htm?spm=a230r.1.14.6.670d6fbeYKDOzW&id=598079959720&cm_id=140105335569ed55e27b&abbucket=6&sku_properties=10004:653780895;5919063:6536025',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        for p in range(maxPage):
            url_rate = 'https://rate.tmall.com/list_detail_rate.htm?currentPage=%d&itemId=%s&sellerId=%s' % (
            p + 1, item_id, seller_id)
            params = {'currentPage': p + 1,
                      'itemId': item_id,
                      'sellerId': seller_id,
                      }
            yield scrapy.Request(url=url_rate, cookies=self.cookies, headers=header, callback=self.parse_commentSecond,
                                 meta=params, dont_filter=True)
    def parse_commentSecond(self, response):
        start = re.search('{', response.text).span()
        response_json = json.loads(response.text[start[0]:-1])
        item_id, seller_id = get_id(response.url)
        comment_item = TaobaoCommentItem()
        comment_item['comment_info'] = response_json
        comment_item['item_id'] = item_id
        return comment_item
    def get_base_category(self,soup):
        item = TaobaoAllCategorysItem()
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

    def get_category(self, list):
        lists = []
        for l in list:
            lists.append(l.select_one('span.text').get_text().strip())
        return lists

    def close(self, spider, reason):
        spider.browser.close()