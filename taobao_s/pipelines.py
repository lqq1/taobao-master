# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from taobao_s.tools import skulist_find
import pandas as pd
from taobao_s.items import TaobaoSItem, TaobaoCommentItem, TaobaoAllCategorysItem

class TaobaoSPipeline(object):
    def open_spider(self, spider):
        self.f = open('淘宝店铺数据.txt','w')
        self.f_type = open('phone_type.txt','w')
        self.f_comment = open('comment_info.txt','w')
    def process_item(self, item, spider):
        if isinstance(item, TaobaoSItem):
            data = {}
            data['phone_name'] = item['phone_name']
            data['phone_price'] = item['phone_price']
            data['sell_num'] = item['sell_num']
            data['rate_num'] = item['rate_num']
            data['collect_num'] = item['collect_num']
            data['shop_name'] = item['shop_name']
            data['shop_type'] = item['shop_type']
            data['shop_describe'] = item['shop_describe']
            data['shop_service'] = item['shop_service']
            data['shop_flow'] = item['shop_flow']
            data['describe_rate'] = item['describe_rate']
            data['service_rate'] = item['service_rate']
            data['flow_rate'] = item['flow_rate']
            data['describe_label'] = item['describe_label']
            data['service_label'] = item['service_label']
            data['flow_label'] = item['flow_label']
            data['shop_year'] = item['shop_year']
            data['url'] = item['url']
            data['parameters'] = item['parameters']
            data['product_id'] = item['product_id']
            data['shop_id'] = item['shop_id']
            data['total_comment'] = item['total_comment']
            data['shop'] = item['shop']
            data['pic_num'] = item['pic_num']
            data['used_num'] = item['used_num']
            self.f.write(str(data)+'\n')
        elif isinstance(item, TaobaoAllCategorysItem):
            data = {}
            data['trade_market_list'] = item['trade_market_list']
            data['phone_type_list'] = item['phone_type_list']
            data['phone_ROM_list'] = item['phone_ROM_list']
            data['phone_RAM_list'] = item['phone_RAM_list']
            data['network_type'] = item['network_type']
            data['cpu_num'] = item['cpu_num']
            data['pixel'] = item['pixel']
            data['os_type'] = item['os_type']
            self.f_type.write(str(data) + '\n')
            self.f_type.close()
        elif isinstance(item, TaobaoCommentItem):
            rateList = skulist_find(item['comment_info'])
            data = pd.DataFrame(rateList)
            data['id'] = item['item_id']
            self.f_comment.write(str(data) + '\n')
        return item
    def close_spider(self,spider):
        self.f.close()
        self.f_comment.close()



# class TaobaoAllCategorysPipeline(object):
#     def open_spider(self,spider):
#         self.f = open('phone_type.csv','w')
#     def process_item(self, item, spider):
#
#         data = {}
#         data['trade_market'] = item['trade_market']
#         data['phone_type'] = item['phone_type']
#         data['phone_ROM'] = item['phone_ROM']
#         data['phone_RAM'] = item['phone_RAM']
#         data['network_type'] = item['network_type']
#         data['cpu_num'] = item['cpu_num']
#         data['pixel'] = item['pixel']
#         data['os_type'] = item['os_type']
#         self.f.write(str(data)+'\n')
#         return item
#     def close_spider(self,spider):
#         self.f.close()
#
# class TaobaoCommentPipeline(object):
#     def open_spider(self,spider):
#         self.f = open('comment_info.csv','w')
#     def process_item(self, item, spider):
#         rateList = skulist_find(item['comment_info'])
#         data = pd.DataFrame(rateList)
#         data['id'] = item['item_id']
#         self.f.write(str(data)+'\n')
#         return item
#     def close_spider(self,spider):
#         self.f.close()



