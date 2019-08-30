
#实现不同页面的元素放在一个item 中
def parse_page1(self, response):
    item = MyItem()
    item['main_url'] = response.url
    request = scrapy.Request("http://www.example.com/some_page.html",
                             callback=self.parse_page2)
    request.meta['item'] = item  # 通过meta属性将parse_page1的Item传递到parse_page2中
    return request
def parse_page2(self, response):
    item = response.meta['item']
    item['other_url'] = response.url
    return item
