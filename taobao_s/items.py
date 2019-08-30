# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoSItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    phone_name = scrapy.Field()
    phone_price = scrapy.Field()
    sell_num = scrapy.Field()
    rate_num = scrapy.Field()
    collect_num = scrapy.Field()
    shop_name = scrapy.Field()
    shop_type = scrapy.Field()
    shop_describe = scrapy.Field()
    shop_service = scrapy.Field()
    shop_flow = scrapy.Field()
    describe_rate = scrapy.Field()
    service_rate = scrapy.Field()
    flow_rate = scrapy.Field()
    describe_label = scrapy.Field()
    service_label = scrapy.Field()
    flow_label = scrapy.Field()
    shop_year = scrapy.Field()
    parameters = scrapy.Field()
    product_id = scrapy.Field()
    shop_id = scrapy.Field()
    total_comment = scrapy.Field()
    pic_num = scrapy.Field()
    shop = scrapy.Field()
    used_num = scrapy.Field()

class TaobaoAllCategorysItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    trade_market_list = scrapy.Field()
    phone_type_list = scrapy.Field()
    phone_ROM_list = scrapy.Field()
    phone_RAM_list= scrapy.Field()
    network_type = scrapy.Field()
    cpu_num = scrapy.Field()
    pixel = scrapy.Field()
    os_type = scrapy.Field()

class TaobaoCommentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    comment_info = scrapy.Field()
    item_id = scrapy.Field()



