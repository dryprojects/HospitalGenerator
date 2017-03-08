#!/usr/bin/env python
# -*- coding:utf-8 -*-

###############################################
#   数据模型定义
#   作者: Jennei
#   日期: 2017/03/07
#   邮箱: jennei@hotmail.com
###############################################
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

from scrapy.utils.project import get_project_settings as settings

Base = declarative_base()

class Rules(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))               #爬虫名字
    allow_domains = Column(String(255))     #允许爬取的域名
    start_urls = Column(String(255))        #爬取的起始链接
    allow_url = Column(String(255))         #允许爬取的链接匹配模式
    next_page = Column(String(255))         #下一页的跟进链接 xpath
    extract_from = Column(String(255))      #限制解析的区域 xpath >>保留<<
    loop_css = Column(String(255))          #单次页面循环的控制节点 css
    key_words = Column(String(255))         #数据过滤关键字
    postTime_pattern = Column(String(255))  #发表日期过滤正则
    msgTitle_css = Column(String(255))      #页面标题
    postTime_css = Column(String(255))      #内容发表时间
    msgDesc_css = Column(String(255))       #内容标题
    enable = Column(Integer)                #爬虫启用标志 1 开启 0 关闭

class Info(Base):
    __tablename__ = 'info'
    id = Column(Integer, primary_key=True)
    postTime = Column(String(20))
    msgLink = Column(String(255))
    msgTitle = Column(String(255))
    msgDesc = Column(String(255))

class Model(object):
    def __init__(self, dialect = None, encoding='gbk', echo=False):
        """
        根据所给的数据库方言，初始化相应连接
        :param dialect:数据库连接字符串
        """
        if dialect is None:
            dialect = 'mysql+mysqldb://'+settings()['MYSQL_USER']+':'+settings()['MYSQL_PASSWORD']+'@'+settings()['MYSQL_HOST']+'/?charset=gbk'

        self.engine = create_engine(dialect, encoding=encoding, echo=echo)
        DB_Session = sessionmaker(bind=self.engine)
        self.session = DB_Session()
        self.session.execute('create database if NOT EXISTS bids DEFAULT CHARACTER SET gbk COLLATE gbk_chinese_ci;')
        self.session.execute('use bids;')
        self.session.execute('drop table if EXISTS rules;')
        self.session.execute('drop table if EXISTS info;')
        self.session.commit()
        Rules.metadata.create_all(self.engine)
        Info.metadata.create_all(self.engine)

class HospitalModel(Model):
    def __init__(self):
        super(HospitalModel, self).__init__()
        #定义各个爬虫的规则，并添加到数据库当中
        #西安市第四医院
        r4thofxian = Rules(
            name = 'grmp',
            allow_domains = 'grmg.com.cn',
            start_urls = 'http://www.grmg.com.cn/news/changjianwenti/yiyuangonggao/',
            allow_url = r'yiyuangonggao/\d+',
            next_page = "//div[@class='pages']",
            extract_from = '',
            loop_css = '.pageC',
            key_words = r'(\xd5\xd0\xb1\xea)',
            postTime_pattern = r'(\d{1,4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})',
            msgTitle_css = 'title::text',
            postTime_css = '.artinfo::text',
            msgDesc_css = '.arttitle h1::text',
            enable = 1
        )
        #第四军医大学
        fmmu = Rules(
            name = 'fmmu',
            allow_domains = 'fmmu.edu.cn',
            start_urls = 'https://tongzhi.fmmu.edu.cn/gsxx.htm',
            allow_url = r'info/\d+/\d+\.htm',
            next_page = "//div[@style='float:left']",
            extract_from = '',
            loop_css = '.content',
            key_words = r'(\xd5\xd0\xb1\xea|\xd2\xbd\xd4\xba|\xb2\xc9\xb9\xba)',
            postTime_pattern = r'(\d{1,4}.+\d{1,2}.+\d{1,2}.+\s*\d{1,2}:\d{1,2})',
            msgTitle_css = 'title::text',
            postTime_css = '.news_fabu_title_time::text',
            msgDesc_css = '.news_title::text',
            enable = 1
        )
        #陕西省人民医院
        spph = Rules(
            name='spph',
            allow_domains='spph-sx.com',
            start_urls='http://www.spph-sx.com/xwzx/tzgg.htm',
            allow_url=r'info/\d+/\d+\.htm',
            next_page="//div[@align='center']",
            extract_from='',
            loop_css='.wen_contt',
            key_words=r'(\xd5\xd0\xc6\xb8|\xd2\xe9\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})',
            msgTitle_css='title::text',
            postTime_css='.liay_con::text',
            msgDesc_css='.nir_con::text',
            enable=1
        )

        self.session.add(r4thofxian)
        self.session.add(fmmu)
        self.session.add(spph)
        self.session.commit()

if __name__ == '__main__':
    m = HospitalModel()
