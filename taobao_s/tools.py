import re
import random
import json
import time
from taobao_s.settings import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def data_cleaning(data):
    if ' ' in data:
        data = re.sub(' ', '', data)
    if "'" in data:
        data = re.sub("'", '', data)
    if r'\n' in data:
        data = re.sub(r'\\n', '', data)
    return data

def register():
    while True:
        browser = webdriver.FirefoxOptions()
        browser.add_argument('-headless')
        browser = webdriver.Firefox(firefox_options=browser)
        # browser = webdriver.Firefox()
        browser.get('https://login.taobao.com/member/login.jhtml')
        user = browser.find_element(By.ID, 'TPL_username_1')
        try:
            input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'forget-pwd.J_Quick2Static')))
            # for i in input:
            #     if i.is_displayed():
            #         i.click()
            input.click()
        except Exception as e:
            print(e)
        #user = browser.find_element(By.ID, 'TPL_username_1')
        password = browser.find_element(By.ID, 'TPL_password_1')
        user.send_keys(USER)
        time.sleep(random.random() * 2)
        password.send_keys(PASSWORD)
        time.sleep(random.random() * 1)
        browser.execute_script("Object.defineProperties(navigator,{webdriver:{get:() => false}})")
        action = ActionChains(browser)
        time.sleep(random.random() * 1)
        butt = browser.find_element(By.ID, 'nc_1_n1z')
        browser.switch_to.frame(browser.find_element(By.ID, '_oid_ifr_'))
        browser.switch_to.default_content()
        action.click_and_hold(butt).perform()
        action.reset_actions()
        action.move_by_offset(285, 0).perform()
        time.sleep(random.random() * 1)
        button = browser.find_element(By.ID, 'J_SubmitStatic')
        time.sleep(random.random() * 2)
        button.click()
        time.sleep(random.random() * 2)
        # browser.get('https://www.taobao.com/')
        cookie = browser.get_cookies()
        list = {}
        for cookiez in cookie:
            name = cookiez['name']
            value = cookiez['value']
            list[name] = value
        if len(list) > 10:
            break
        else:
            browser.close()
    return browser, list

def comment(url):
    browser = webdriver.FirefoxOptions()
    browser.add_argument('-headless')
    browser = webdriver.Firefox(firefox_options=browser)
    browser.get(url)
    return browser

#过滤掉部分连接
def not_item_taobao_com(href):
    return href and not re.compile('item.taobao.com').search(href)

def not_tableAtttrsSub(tag):
    return not tag.has_attr('class')

#获取评价中用户购买的手机基本信息
def skulist_find(response_json):
    rateList = response_json['rateDetail']['rateList']
    rateList_temp=[]
    for rl in rateList:
        rl_temp = {}
        keys = ['cmsSource', 'displayUserNick', 'sellerId']
        for k in keys:
            rl_temp[k] = rl[k]
        for r in rl['auctionSku'].split(';'):
            rl_temp[r.split(':')[0]] = r.split(':')[1]
        rl_temp['rateDate'] = rl['rateDate'][0:10]
        rateList_temp.append(rl_temp)
    return rateList_temp

def get_id(url):
    pattern = re.compile('itemId=(.+)&sellerId=(.+)')
    search = re.search(pattern, url)
    itemId = search.group(1)
    sellerId = search.group(2)
    return itemId, sellerId

#同行业情况比较
def rateLabel(rate):  #同行业情况比较
    if rate.select('b[class="fair"]'):
        label = '持平'
        rate = 0  # 描述 同行业情况
    elif rate.select('b[class="lower"]'):
        label = '低于'
        rate = '-' + rate.select('em')[0].get_text().strip()  # 描述 同行业情况
    else:
        label = '高于'
        rate = rate.select('em')[0].get_text().strip()  # 描述 同行业情况
    return label, rate


