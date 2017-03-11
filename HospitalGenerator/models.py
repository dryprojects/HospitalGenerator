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
    next_page = Column(String(255))         #下一页的跟进链接 xpath, 为空表示不进行分页处理
    base_url = Column(String(255))          #网页绝对url,如果为分页处理，此字段为空
    extract_from = Column(String(255))      #限制解析的区域 xpath >>保留<<
    loop_css = Column(String(255))          #单次页面循环的控制节点 css
    key_words = Column(String(255))         #数据过滤关键字
    postTime_pattern = Column(String(255))  #发表日期过滤正则
    msgTitle_css = Column(String(255))      #页面标题
    msgLink_css = Column(String(255))       #不是分页处理时，内容连接的css
    postTime_css = Column(String(255))      #内容发表时间
    msgDesc_css = Column(String(255))       #内容标题
    msgFrom = Column(String(255))           #医院名称
    enable = Column(Integer)                #爬虫启用标志 1 开启 0 关闭

class Info(Base):
    __tablename__ = 'info'
    id = Column(Integer, primary_key=True)
    postTime = Column(String(20))
    msgLink = Column(String(255))
    msgTitle = Column(String(255))
    msgDesc = Column(String(255))
    msgFrom = Column(String(255))

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
            msgFrom = u'西安市第四医院',
            enable = 0
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
            msgFrom = u'第四军医大学',
            enable = 0
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
            msgFrom = u'陕西省人民医院',
            enable=0
        )
        #西安市第一医院
        xadyyy = Rules(
            name='xadyyy',
            allow_domains='xadyyy.com',
            start_urls='http://www.xadyyy.com/index.php?m=content&c=index&a=lists&catid=81&page=1',
            allow_url=r'm=content&c=index&a=lists&catid=81&page=\d{1,2}',
            next_page="",
            base_url = '',
            extract_from='',
            loop_css='.zkbk2013723',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css = 'a::attr(href)',
            postTime_css='span',
            msgDesc_css='a::text',
            msgFrom = u'西安市第一医院',
            enable=0
        )
        #西安市中医院
        xazyy = Rules(
            name='xazyy',
            allow_domains='xazyy.com',
            start_urls='http://www.xazyy.com/InfoList.aspx?pid=81',
            allow_url=r'InfoDetail.+tid=\d{1,4}&pid=81',
            next_page='//div[@id="ContentPlaceHolder1_SubContent_AspNetPager1"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,2}/\d{1,2}/\d{1,4}\s\d{1,2}:\d{1,2}:\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='#ContentPlaceHolder1_SubContent_infoinfo::text',
            msgDesc_css='.title::text',
            msgFrom = u'西安市中医院',
            enable=0
        )
        #西北妇女儿童医院
        #陕西省妇幼保健院
        nwwch = Rules(
            name='nwwch',
            allow_domains='nwwch.com',
            start_urls='http://nwwch.com/index.php?m=content&c=index&a=lists&catid=19&page=1',
            allow_url=r'm=content&c=index&a=lists&catid=19&page=\d{1,4}',
            next_page='',
            base_url='',
            extract_from='',
            loop_css='.ullist li',
            key_words=r'(\xb2\xc9\xb9\xba\xb9\xab\xb8\xe6)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'西北妇女儿童医院(陕西省妇幼保健院)',
            enable=0
        )

        #西安交通大学第一附属医院
        yfyzbb = Rules(
            name='yfyzbb',
            allow_domains='jdyfy.com',
            start_urls='http://yfyzbb.jdyfy.com/zbxx1/zbgg.htm',
            allow_url=r'info/1025/\d{1,4}\.htm',
            next_page='//div[@align="center"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='div[align="center"]::text',
            msgDesc_css='.news::text',
            msgFrom=u'西安交通大学第一附属医院',
            enable=0
        )
        #西安交通大学第二附属医院
        x2yuan = Rules(
            name='x2yuan',
            allow_domains='2yuan.org',
            start_urls='http://www.2yuan.org/Html/News/Columns/101/1.html',
            allow_url=r'Html/News/Columns/101/\d{1,3}\.html',
            next_page='',
            base_url='http://www.2yuan.org',
            extract_from='',
            loop_css='#zoom li',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='.dy_date::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'西安交通大学第二附属医院',
            enable=0
        )
        #第四军医大学唐都医院
        tdfmmu = Rules(
            name='tdfmmu',
            allow_domains='fmmu.edu.cn',
            start_urls='http://tdwww.fmmu.edu.cn/9/18(1)/list.aspx',
            allow_url=r'9/18\(\d{1,3}\)/list\.aspx',
            next_page='',
            base_url='http://tdwww.fmmu.edu.cn',
            extract_from='',
            loop_css='.Law li',
            key_words=r'(\xd5\xd0\xb1\xea|\xb2\xc9\xb9\xba)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'第四军医大学唐都医院',
            enable=0
        )
        kqfmmu = Rules(
            name='kqfmmu',
            allow_domains='fmmu.edu.cn',
            start_urls='http://kqwww.fmmu.edu.cn/info/iList.jsp?cat_id=10003&cur_page=1',
            allow_url=r'info/iList\.jsp\?cat_id=10003&cur_page=\d{1,3}',
            next_page='',
            base_url='http://kqwww.fmmu.edu.cn',
            extract_from='',
            loop_css='.list_con_box li',
            key_words=r'(\xd5\xd0\xb1\xea|\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='.time::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'第四军医大学口腔医院',
            enable=1
        )

        self.session.add(r4thofxian)
        self.session.add(fmmu)
        self.session.add(spph)
        self.session.add(xadyyy)
        self.session.add(xazyy)
        self.session.add(nwwch)
        self.session.add(yfyzbb)
        self.session.add(x2yuan)
        self.session.add(tdfmmu)
        self.session.add(kqfmmu)
        self.session.commit()

if __name__ == '__main__':
    m = HospitalModel()
