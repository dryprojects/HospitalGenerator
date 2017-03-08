#!/usr/bin/env python
# -*- coding:utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from HospitalGenerator.items import HospitalgeneratorItem as HI

class DeepSpider(CrawlSpider):
    name='Deep'
    def __init__(self, rule):
        self.rule = rule

        self.name = rule.name
        self.allowed_domains = rule.allow_domains.split(',')
        self.start_urls = rule.start_urls.split(',')

        rule_list = []
        #如果是分页的网页，则采取分页处理
        if len(rule.next_page):
            rule_list.append(
                Rule(
                    LinkExtractor(restrict_xpaths=rule.next_page),
                    follow=True
                )
            )
        #网页的一般处理
        rule_list.append(
            Rule(
                LinkExtractor(allow=(rule.allow_url, ), unique=True),
                callback='parse_item',
                follow=True
            )
        )

        self.rules = rule_list

        super(DeepSpider, self).__init__()

    def parse_item(self, response):
        for sel in response.css(self.rule.loop_css):
            item = HI()
            item['title'] = response.css(self.rule.msgTitle_css)[0].extract().encode('gbk', 'ignore')
            item['desc'] = sel.css(self.rule.msgDesc_css)[0].extract().encode('gbk', 'ignore')
            item['link'] = response.url
            item['postTime'] = sel.css(self.rule.postTime_css)[0].extract().encode('gbk', 'ignore')
            yield item
