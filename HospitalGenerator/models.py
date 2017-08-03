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
#如果用runGrmp启动则去掉下面注释
#from scrapy.utils.project import get_project_settings as settings
import ConfigParser

cp = ConfigParser.SafeConfigParser()
cp.read('./settings.conf')


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
            #如果用runGrmp启动则去掉下面注释
            #dialect = 'mysql+mysqldb://'+settings()['MYSQL_USER']+':'+settings()['MYSQL_PASSWORD']+'@'+settings()['MYSQL_HOST']+'/?charset=gbk'
            dialect = 'mysql+mysqldb://'+cp.get('DB', 'MYSQL_USER')+':'+cp.get('DB', 'MYSQL_PASSWORD')+'@'+cp.get('DB', 'MYSQL_HOST')+'/?charset=gbk'

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
            postTime_pattern = r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css = 'title::text',
            postTime_css = '.artinfo::text',
            msgDesc_css = '.arttitle h1::text',
            msgFrom = u'西安市第四医院',
            enable = 1
        )#网站暂时访问不了，未备案
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
            postTime_pattern = r'(\d{4}\xc4\xea\d{2}\xd4\xc2\d{2})',
            msgTitle_css = 'title::text',
            postTime_css = '.news_fabu_title_time::text',
            msgDesc_css = '.news_title::text',
            msgFrom = u'第四军医大学',
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
            postTime_pattern=r'(\d{4}-\d{2}-\d{2})',
            msgTitle_css='title::text',
            postTime_css='.liay_con::text',
            msgDesc_css='.nir_con::text',
            msgFrom = u'陕西省人民医院',
            enable=1
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
            enable=1
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
            postTime_pattern=r'(\d{1,4}/\d{1,2}/\d{1,4})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='#ContentPlaceHolder1_SubContent_infoinfo::text',
            msgDesc_css='.title::text',
            msgFrom = u'西安市中医院',
            enable=1
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
            enable=1
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
            enable=1
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
            enable=1
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
            enable=1
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
        xaszxyy = Rules(
            name='xaszxyy',
            allow_domains='xaszxyy.com',
            start_urls='http://www.xaszxyy.com/2/15(1)/list.aspx',
            allow_url=r'2/15\(\d+\)/list.aspx',
            next_page='',
            base_url='http://www.xaszxyy.com',
            extract_from='',
            loop_css='.news_new li',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='.fr::text',
            msgDesc_css='a::text',
            msgFrom=u'西安市中心医院',
            enable=1
        )
        hzcch = Rules(
            name='hzcch',
            allow_domains='hzcch.com',
            start_urls='http://www.hzcch.com/gsgg/gsgg1.htm',
            allow_url=r'info/1064/\d+\.htm',
            next_page='//div[@align="center"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='div[align="center"]::text',
            msgDesc_css='h1::text',
            msgFrom=u'汉中市中心医院',
            enable=1
        )
        wnszxyy = Rules(
            name='wnszxyy',
            allow_domains='wnszxyy.com',
            start_urls='http://www.wnszxyy.com/subpage.asp?id=41&xid=0&page=1',
            allow_url=r'subpage\.asp\?id=41&xid=0&page=\d+',
            next_page='',
            base_url='http://www.wnszxyy.com',
            extract_from='',
            loop_css='.showcontent li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'渭南市中心医院',
            enable=1
        )
        bjzxyy = Rules(
            name='bjzxyy',
            allow_domains='bjzxyy.com',
            start_urls='http://www.bjzxyy.com/news/class/?53.html&page=1&showtj=&showhot=&author=&key=',
            allow_url=r'news/html/\?\d+\.html',
            next_page='//DIV[@class="daye_right_2_3_b"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xd5\xd0\xb1\xea|\xb2\xc9\xb9\xba|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='.daye_right_2_2::text',
            msgDesc_css='.daye_right_2_1::text',
            msgFrom=u'宝鸡市中心医院',
            enable=1
        )
        wjyy029 = Rules(
            name='wjyy029',
            allow_domains='wjyy029.com',
            start_urls='http://www.wjyy029.com/ColumnPage.aspx?categoryid=54',
            allow_url=r'ColumnPage\.aspx\?categoryid=54',
            next_page='',
            base_url='http://www.wjyy029.com',
            extract_from='',
            loop_css='.list-unstyledl li',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='a div:nth-child(2)::text',
            msgDesc_css='a div::text',
            msgFrom=u'武警陕西省总队医院',
            enable=1
        )#现在只能抓取武警医院的第一页
        zyhos = Rules(
            name='zyhos',
            allow_domains='zyhos.com',
            start_urls='http://www.zyhos.com/news/index.asp?D_CataID=I0003&pageno=1',
            allow_url=r'news/index\.asp\?D_CataID=I0003&pageno=\d+',
            next_page='',
            base_url='http://www.zyhos.com/news/',
            extract_from='',
            loop_css='.xuxian',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='td:nth-child(2)::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'陕西中医药大学第二附属医院',
            enable=1
        )
        xy120 = Rules(
            name='xy120',
            allow_domains='xy120.net',
            start_urls='http://www.xy120.net/news/notice.htm',
            allow_url=r'info/1162/\d+\.htm',
            next_page='//div[@class="page-bar"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}.*?\d{1,2}.*?\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='.view-param::text',
            msgDesc_css='.view-title::text',
            msgFrom=u'咸阳市中心医院',
            enable=1
        )
        xadwyy = Rules(
            name='xadwyy',
            allow_domains='xadwyy.com',
            start_urls='http://www.xadwyy.com/index.php?m=content&c=index&a=lists&catid=376&page=1',
            allow_url=r'index\.php\?m=content&c=index&a=lists&catid=376&page=\d+',
            next_page='',
            base_url='',
            extract_from='',
            loop_css='.content li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'西安市第五医院',
            enable=1
        )
        xa8yuan = Rules(
            name='xa8yuan',
            allow_domains='xa8yuan.com',
            start_urls='http://www.xa8yuan.com/xxgk/list.asp?classid=52&order=0&page=1',
            allow_url=r'xxgk/list\.asp\?classid=52&order=0&page=\d+',
            next_page='',
            base_url='http://www.xa8yuan.com/xxgk/',
            extract_from='',
            loop_css='#listbox li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='em::text',
            msgDesc_css='a::text',
            msgFrom=u'西安市第五医院',
            enable=1
        )#网站访问不了
        yl2y = Rules(
            name='yl2y',
            allow_domains='yl2y.com',
            start_urls='http://www.yl2y.com/dtxx/gonggao/',
            allow_url=r'dtxx/gonggao/\d+\.html',
            next_page='//div[@class="fenye"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='.dgzr_wenzhang div:nth-child(2)::text',
            msgDesc_css='.dgzr_wenzhang div:nth-child(1)::text',
            msgFrom=u'榆林市第二医院',
            enable=1
        )
        hz3201 = Rules(
            name='hz3201',
            allow_domains='hz3201.com',
            start_urls='http://www.hz3201.com/news.php?cid=35&page=1',
            allow_url=r'news\.php\?cid=35&page=\d+',
            next_page='',
            base_url='http://www.hz3201.com/',
            extract_from='',
            loop_css='.news_list2 li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='.time::text',
            msgDesc_css='a::text',
            msgFrom=u'汉中3201医院',
            enable=1
        )
        ylsdyyy = Rules(
            name='ylsdyyy',
            allow_domains='ylsdyyy.com',
            start_urls='http://www.ylsdyyy.com/index.php?m=Index&a=newsList&typeid=8&p=1',
            allow_url=r'index\.php\?m=Index&a=newsList&typeid=8&p=\d+',
            next_page='',
            base_url='http://www.ylsdyyy.com',
            extract_from='',
            loop_css='.news_nr li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'榆林市第一医院',
            enable=1
        )
        dentalxjtu = Rules(
            name='dentalxjtu',
            allow_domains='dentalxjtu.com',
            start_urls='http://www.dentalxjtu.com/news.php?hcateid=111&cateid=11119&page=1',
            allow_url=r'news\.php\?hcateid=111&cateid=11119&page=\d+',
            next_page='',
            base_url='http://www.dentalxjtu.com/',
            extract_from='',
            loop_css='.news_list li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='.n_time::text',
            msgDesc_css='a::text',
            msgFrom=u'西安交通大学口腔医院',
            enable=1
        )
        sxcahosp = Rules(
            name='sxcahosp',
            allow_domains='sxcahosp.com',
            start_urls='http://www.sxcahosp.com/newslist.aspx?sid=46',
            allow_url=r'newslist\.aspx\?sid=46',
            next_page='',
            base_url='http://www.sxcahosp.com/',
            extract_from='',
            loop_css='.newslist li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='.a::attr(href)',
            postTime_css='.time::text',
            msgDesc_css='.a::text',
            msgFrom=u'陕西省肿瘤医院',
            enable=1
        )#只能抓取第一页
        xtzxyy = Rules(
            name='xtzxyy',
            allow_domains='xtzxyy.com',
            start_urls='http://www.xtzxyy.com/cn/list.aspx?c=314&p=1',
            allow_url=r'cn/list\.aspx\?c=314&p=\d+',
            next_page='',
            base_url='http://www.xtzxyy.com/cn/',
            extract_from='',
            loop_css='#ctl00_MainContent_Controllist1_dlTW li',
            key_words=r'(\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='.time::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'西安市第九医院',
            enable=1
        )
        xahhyy = Rules(
            name='xahhyy',
            allow_domains='xahhyy.com',
            start_urls='http://www.xahhyy.com/news.aspx',
            allow_url=r'Cmsview_\d+\.aspx',
            next_page='',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}/\d{1,2}/\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='.title3::text',
            msgDesc_css='.title2::text',
            msgFrom=u'西安市红十字会医院',
            enable=1
        )
        xajwzx = Rules(
            name='xajwzx',
            allow_domains='xajwzx.com',
            start_urls='http://www.xajwzx.com/index.php?m=content&c=index&a=lists&catid=81',
            allow_url=r'index\.php\?m=content&c=index&a=lists&catid=81',
            next_page='',
            base_url='http://www.xajwzx.com',
            extract_from='',
            loop_css='.z_news_n li',
            key_words=r'(\xd5\xd0\xb1\xea)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'西安市精神卫生中心',
            enable=1
        )
        xaxkyy = Rules(
            name='xaxkyy',
            allow_domains='xaxkyy.com',
            start_urls='http://www.xaxkyy.com/2/16(1)/list.aspx',
            allow_url=r'2/16\(\d+\)/list\.aspx',
            next_page='',
            base_url='http://www.xaxkyy.com',
            extract_from='',
            loop_css='.news li',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'西安市胸科医院',
            enable=1
        )
        bjszyy = Rules(
            name='bjszyy',
            allow_domains='bjszyy.com',
            start_urls='http://www.bjszyy.com/List_1_30_1.html',
            allow_url=r'List_1_30_\d+\.html',
            next_page='',
            base_url='http://www.bjszyy.com',
            extract_from='',
            loop_css='.new li',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'宝鸡市中医院',
            enable=1
        )
        yasrmyy = Rules(
            name='yasrmyy',
            allow_domains='yasrmyy.cn',
            start_urls='http://www.yasrmyy.cn/2/13(1)/list.aspx',
            allow_url=r'2/13\(\d+\)/list\.aspx',
            next_page='',
            base_url='http://www.yasrmyy.cn',
            extract_from='',
            loop_css='.news_c li',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::text',
            msgFrom=u'延安市人民医院',
            enable=1
        )
        ylzyy = Rules(
            name='ylzyy',
            allow_domains='ylzyy.com',
            start_urls='http://www.ylzyy.com/info.aspx?classid=18',
            allow_url=r'content\.aspx\?id=\d+',
            next_page='//div[@id="page"]',
            base_url='',
            extract_from='',
            loop_css='',
            key_words=r'(YLZYY)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='',
            postTime_css='#div1::text',
            msgDesc_css='.detail_title::text',
            msgFrom=u'榆林市中医医院',
            enable=1
        )#该医院采集时间较长
        akzxyy = Rules(
            name='akzxyy',
            allow_domains='akzxyy.com',
            start_urls='http://www.akzxyy.com/news.asp?page=1&class_id=52&big_id=26',
            allow_url=r'news\.asp\?page=\d+&class_id=52&big_id=26',
            next_page='',
            base_url='http://www.akzxyy.com/',
            extract_from='',
            loop_css='table:nth-child(5) table:nth-child(5) tr',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='td:nth-child(3)::text',
            msgDesc_css='a::text',
            msgFrom=u'安康市中心医院',
            enable=1
        )
        #table:nth-child(7) td:nth-child(2) table:nth-child(3) tr
        xdjtyy = Rules(
            name='xdjtyy',
            allow_domains='xdjtyy.com',
            start_urls='http://www.xdjtyy.com/art_list_more.aspx?more_id=198',
            allow_url=r'art_list_more\.aspx\?more_id=198',
            next_page='',
            base_url='http://www.xdjtyy.com/',
            extract_from='',
            loop_css='table:nth-child(7) td:nth-child(2) table:nth-child(3) tr',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='td:nth-child(2)::text',
            msgDesc_css='a::text',
            msgFrom=u'西电集团医院',
            enable=1
        )#暂时未实现抓取
        xiyi = Rules(
            name='xiyi',
            allow_domains='xiyi.edu.cn',
            start_urls='http://www.xiyi.edu.cn/info/iList.jsp?cat_id=10198&cur_page=1',
            allow_url=r'info/iList\.jsp\?cat_id=10198&cur_page=\d+',
            next_page='',
            base_url='http://www.xiyi.edu.cn',
            extract_from='',
            loop_css='.commonList_dot2 li',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='span::text',
            msgDesc_css='a::attr(title)',
            msgFrom=u'西安医学院',
            enable=1
        )
        ccgp = Rules(
            name='ccgp',
            allow_domains='ccgp-shaanxi.gov.cn',
            start_urls='http://www.ccgp-shaanxi.gov.cn/cggg.jsp',
            allow_url=r'.*',
            next_page='',
            base_url='http://www.ccgp-shaanxi.gov.cn',
            extract_from='',
            loop_css='table tr:nth-child(2) td:nth-child(2) table:nth-child(1) tr:nth-child(2) table tr',
            key_words=r'(\xb2\xc9\xb9\xba|\xb9\xab\xb8\xe6|\xb9\xab\xca\xbe|\xd5\xd0\xb1\xea|\xe5\xe0\xd1\xa1)',
            postTime_pattern=r'(\d{1,4}-\d{1,2}-\d{1,2})',
            msgTitle_css='title::text',
            msgLink_css='a::attr(href)',
            postTime_css='td:nth-child(3)::text',
            msgDesc_css='a::text',
            msgFrom=u'陕西政府采购',
            enable=1
        )
        self.session.add(ccgp)
        self.session.add(xiyi)
        self.session.add(xdjtyy)
        self.session.add(akzxyy)
        self.session.add(ylzyy)
        self.session.add(yasrmyy)
        self.session.add(bjszyy)
        self.session.add(xaxkyy)
        self.session.add(xajwzx)
        self.session.add(xahhyy)
        self.session.add(xtzxyy)
        self.session.add(sxcahosp)
        self.session.add(dentalxjtu)
        self.session.add(ylsdyyy)
        self.session.add(hz3201)
        self.session.add(yl2y)
        self.session.add(xa8yuan)
        self.session.add(xadwyy)
        self.session.add(xy120)
        self.session.add(zyhos)
        self.session.add(wjyy029)
        self.session.add(bjzxyy)
        self.session.add(wnszxyy)
        self.session.add(hzcch)
        self.session.add(xaszxyy)
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
