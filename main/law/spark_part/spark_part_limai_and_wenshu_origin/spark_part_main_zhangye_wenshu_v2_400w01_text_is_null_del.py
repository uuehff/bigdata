# -*- coding: utf-8 -*-
"""
对抓取的文书内容进行数据提取
"""
import re
from  pyspark import SparkContext,SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *
import json
import pymysql
from lxml import etree
import HTMLParser
import uuid as UUID

reg_link = re.compile(r"<a[^>]+>|</a>", flags=re.S)
reg_blank = re.compile(r'((?!\n)\s)*', flags=re.S)
# reg_part = re.compile(r'<span litigantpart></span>')  # <a type='dir' name='DSRXX'></a>, 当事人信息
# reg_process = re.compile(r'<span proceeding></span>')  # <a type='dir' name='SSJL'></a>，审理过程
# reg_argued = re.compile(r'<span argued></span>')  # <a type='dir' name='AJJBQK'></a> ，诉讼请求
# reg_fact = re.compile(r'<span fact></span>')                                         #法院查明
# reg_court = re.compile(r'<span courtconsider></span>')  # <a type='dir' name='CPYZ'></a> #法院认为
# reg_result = re.compile(r'<span result></span>')     #<a type='dir' name='PJJG'></a>    #判决结果
# doc_footer                                       #<a type='dir' name='WBWB'></a>


def format_content(content, b_value):
    """
    理脉网内容分段
    :param content:

    :return:
    """
    content_dict = dict()


    content_text = HTMLParser.HTMLParser().unescape(content)  # python2的代码
    # content_text = html.unescape(content)    #python3的代码

    # , "不公开理由":"",
    # ur"[\u4e00-\u9fa5]"
    # pri_reason_re = re.search(ur"不公开理由\":\"[\u4e00-\u9fa5]{0,200}\"",content_text)    #等价于下面的方式，使用三个引号‘’‘将字符串括起来。

    # $(function()
    # {$("#con_llcs").html("浏览：61次")});$(function()
    # {var
    # caseinfo = JSON.stringify(
    #     {"法院ID": "1213", "案件基本情况段原文": "", "附加原文": "", "审判程序": "", "案号": "（2017）皖1102执1059号之一", "不公开理由": "",
    #      "法院地市": "滁州市", "法院省份": "安徽", "文本首部段落原文": "", "法院区域": "", "文书ID": "00004255-08bc-42b2-a6a6-a84b01524e2c",
    #      "案件名称": "马忠勇、滁州市银世达棉业有限责任公司民间借贷纠纷执行实施类执行裁定书", "法院名称": "滁州市琅琊区人民法院", "裁判要旨段原文": "", "法院区县": "琅琊区", "补正文书": "2",
    #      "DocContent": "", "文书全文类型": "1", "诉讼记录段原文": "本院在执行马忠勇与滁州市银世达棉业有限责任公司民间借贷纠纷一案，因被执行人滁州市银世达棉业有限责任公司暂无财产可供执行",
    #      "判决结果段原文": "", "文本尾部原文": "", "上传日期": "\/Date(1513526400000)\/", "案件类型": "5", "诉讼参与人信息部分原文": "", "文书类型": null,
    #      "裁判日期": null, "结案方式": null, "效力层级": null});$(document).attr("title", "马忠勇、滁州市银世达棉业有限责任公司民间借贷纠纷执行实施类执行裁定书");$(
    # "#tdSource").html("马忠勇、滁州市银世达棉业有限责任公司民间借贷纠纷执行实施类执行裁定书 （2017）皖1102执1059号之一");

    #这里不再需要提取：不公开理由，后面对不能分段的数据已经做了处理，其中就包括对：不公开理由的处理

    title = re.search(ur'''attr[(（]"title","[\u4e00-\u9fa5：:;；，,() （）。0-9、\-]{3,100}"[)）];''',content_text)
    if title:
        title = title.group(0)
        if u"判决书" in title:
            content_dict['judge_type'] = u"判决"
        elif u"裁定书" in title:
            content_dict['judge_type'] = u"裁定"
        elif u"决定书" in title:
            content_dict['judge_type'] = u"决定"
        elif u"通知书" in title:
            content_dict['judge_type'] = u"通知"
        elif u"调解书" in title:
            content_dict['judge_type'] = u"调解"
        else:
            content_dict['judge_type'] = ""

    content_text = content_text.replace("<a type='dir' name='DSRXX'></a>", "0|0|0|11").replace("<a type='dir' name='SSJL'></a>", "0|0|0|22") \
        .replace("<a type='dir' name='AJJBQK'></a>", "0|0|0|33") \
        .replace("<a type='dir' name='CPYZ'></a>", "0|0|0|44").replace("<a type='dir' name='PJJG'></a>", "0|0|0|55") \
        .replace("<a type='dir' name='WBWB'></a>", "0|0|0|66")

    content_text = re.sub(reg_link, "", content_text)  # replace后再去掉<a>标签

    rl = content_text.split("0|0|0|")

    ss = remove_html(rl[0])
    content_dict['court'] = ""
    # "法院名称":"长沙市望城区人民法院"
    court_re = re.search(ur'''法院名称":"[\u4e00-\u9fa5]{3,200}"''', content_text)
    if court_re:
        content_dict['court'] = court_re.group(0).replace(ur'''法院名称":"''', "").replace(ur'''"''', "")
    else:
        for c in b_value:
            if c in ss:
                content_dict['court'] = c
                break

    for i in rl:
        if i.startswith("11"):
            content_dict['member'] = remove_html(i).replace("11", "")
        elif i.startswith("22"):
            content_dict['process'] = remove_html(i).replace("22", "")
        elif i.startswith("33"):
            content_dict['request'] = remove_html(i).replace("33", "")
        elif i.startswith("44"):
            content_dict['idea'] = remove_html(i).replace("44", "")
        elif i.startswith("55"):
            content_dict['result'] = re.split(ur"\\\"}\";", remove_html(i).replace("55", ""))[0]
        elif i.startswith("66"):
            content_dict['doc_footer'] = re.split(ur"\\\"}\";", remove_html(i).replace("66", ""))[0]

    return content_dict,content_text


def remove_html(html_data):
    """
    移除HTML标签
    :param html_data:
    :return:
    """
    html_item = re.sub(reg_blank, "", html_data)
    if html_item:
        item_list = etree.HTML(html_item).xpath('//text()')
        html_text = "\n".join(item_list).strip()
    else:
        html_text = ''
    return html_text


def doc_items(items, b_value):
    id = items[0]
    uuid = items[1]
    doc_content = items[2]
    is_crawl = items[3]


    if not doc_content or not doc_content.startswith('$(fun'):
        # return None
        return u"123qwe-1" + uuid

    content_text,doc_text = format_content(doc_content, b_value)

    if not content_text:
        # return None
        return u"123qwe-2" + uuid
    party_info = content_text.get('member', '')
    trial_process = content_text.get('process', '')
    trial_request = content_text.get('request', '')
    court_find = content_text.get('fact', '')
    court_idea = content_text.get('idea', '')
    judge_result = content_text.get('result', '')
    doc_footer = content_text.get('doc_footer', '')
    court = content_text.get('court', '')

    # pri_reason = content_text.get('pri_reason',"")
    #
    # if party_info == "" and trial_process == "" and trial_request == "" and court_find == "" and court_idea == "" and judge_result == "":  # 没有当事人、判决结果的文书，没有意义！
    #     court_idea = pri_reason    #如果长文本字段都没有，则将未公开理由放到当事人信息里！！

    party_info = party_info.replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")
    court_find = pymysql.escape_string(court_find).replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")
    trial_process = pymysql.escape_string(trial_process).replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")
    trial_request = pymysql.escape_string(trial_request).replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")
    court_idea = pymysql.escape_string(court_idea).replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")
    judge_result = pymysql.escape_string(judge_result).replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")
    doc_footer = pymysql.escape_string(doc_footer).replace("\\n","\n").replace(r'''\\r''', "").replace("\\r", "")


    uuid_ = unicode(UUID.uuid3(UUID.NAMESPACE_DNS2, uuid.encode("utf8"))).replace("-","")  # 基于平台的命名空间 + uuid确定新的uuid_,uuid_是一个对象，需要转化为字符串

    court_idea_all = party_info + trial_process + trial_request + court_find + court_idea + judge_result + doc_footer
    # 无标签下的数据处理,放入court_idea字段
    if court_idea_all == "":
        # doc_text = remove_html(doc_text)
        pri_reason_re = re.search(ur'''不公开理由":"[\u4e00-\u9fa5]{3,200}"''', doc_text)
        if pri_reason_re:
            court_idea = pri_reason_re.group(0).replace(ur'''不公开理由":"''', "").replace(ur'''"''', "")
        else:
            return u"123qwe-3" + uuid
            # return None

    elif is_crawl == "2":  #处理新更新的数据
        pass
    else :           #已经处理过的带标签的数据
        return "is_handled"

    # 对最终的不正常的court_idea做处理，包含有标签和无标签两种情况得到的court_idea。
    c_r = re.compile(ur"[^\u4e00-\u9fa5]")  # 去除court_idea开头不为汉字的。
    if re.match(c_r, court_idea.strip()):
        if court_idea_all == "":  # 无标签的数据，court_idea为空的。
            # return None
            return u"123qwe-4" + uuid
        elif court_idea_all.replace(court_idea, "") == "":  # 有标签的数据，除了court_idea之外全为空的。
            # return None
            return u"123qwe-5" + uuid
        else:  # 有标签的数据，除了court_idea之外,其他字段还有值的。
            court_idea = ""

    judge_type = content_text.get('judge_type', '')

    if judge_type.startswith(u"决定") or judge_type.startswith(u"通知") or judge_type.startswith(u"调解") or judge_type == "":
        court_idea = party_info + "\n\n" + trial_process + "\n\n" + trial_request + "\n\n" + court_find + "\n\n" + court_idea + "\n\n" + judge_result + "\n\n" + doc_footer
        court_idea = court_idea.replace("\n\n\n\n\n\n", "\n\n").replace("\n\n\n\n", "\n\n")


    court_idea.replace("\\n", "\n").replace(r'''\\r''', "").replace("\\r", "")

    # items_dict = dict(party_info=party_info, trial_process=trial_process, trial_request=trial_request,
    #                   court_find=court_find, court_idea=court_idea, judge_result=judge_result, is_format=1,doc_footer=doc_footer)
    # for j in items_dict.keys():
    #     print(j,":::::::",items_dict[j])
    # print type(party_info)
    return (id, uuid, party_info, trial_process, trial_request, court_find, court_idea, judge_result, doc_footer, court,uuid_,judge_type)


if __name__ == "__main__":

    # PYSPARK_PYTHON = "C:\\Python27\\python.exe"    #多版本python情况下，需要配置这个变量指定使用哪个版本
    # os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
    conf = SparkConf()
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)
    # sc.setLogLevel("ERROR")  # ALL, DEBUG, ERROR, FATAL, INFO, OFF, TRACE, WARN '(select id,uuid,plaintiff_info,defendant_info from tmp_lawyers ) tmp'
    # df = sqlContext.read.jdbc(url='jdbc:mysql://192.168.10.22:3306/laws_doc', table='(select id,uuid,doc_content from adjudication_civil where id  >= 1010 and id <= 1041 and doc_from = "limai" ) tmp',column='id',lowerBound=1,upperBound=1800000,numPartitions=1,properties={"user": "tzp", "password": "123456"})
    df = sqlContext.read.jdbc(url='jdbc:mysql://192.168.74.113:3306/wenshu_gov', table='(select id,uuid,doc_content,is_crawl from judgment ) tmp',column='id',lowerBound=1,upperBound=8450135,numPartitions=99,properties={"user": "root", "password": "hhly419"})

    df2 = sqlContext.read.jdbc(url='jdbc:mysql://cdh5-slave2:3306/laws_doc',
                               table='(select id,name from court where name is not null ) tmp', column='id',
                               lowerBound=1, upperBound=5000, numPartitions=1,
                               properties={"user": "weiwc", "password": "HHly2017."})

    def filter_(x):
        if x is not None:
            if isinstance(x,tuple):
            # if  x != "is_handled" and not x.startswith("123qwe-") :
                return True
        return False

    def filter_2(x):
        if x is None :
            return True
        if not isinstance(x,tuple) :
            if x.startswith("123qwe-"):
                return True
        return False


    court_value = sc.broadcast(df2.map(lambda x: x[1]).collect()).value

    lawyer_k_v = df.map(lambda x:doc_items(x,court_value)).cache()
    lawyer_k_v_1 = lawyer_k_v.filter(lambda x:filter_(x))
    lawyer_k_v_null = lawyer_k_v.filter(lambda x:filter_2(x))


    # (id, uuid, party_info, trial_process, trial_request, court_find, court_idea, judge_result, doc_footer)
    schema = StructType([StructField("id", IntegerType(), False)
                            ,StructField("uuid", StringType(), False)
                            ,StructField("party_info", StringType(), True)
                            ,StructField("trial_process", StringType(), True)
                            ,StructField("trial_request", StringType(), True)
                            ,StructField("court_find", StringType(), True)
                            ,StructField("court_idea", StringType(), True)
                            ,StructField("judge_result", StringType(), True)
                            ,StructField("doc_footer", StringType(), True)
                            ,StructField("court", StringType(), True)
                            ,StructField("uuid_", StringType(), True)
                            ,StructField("judge_type", StringType(), True)
                         ])

    schema2 = StructType([StructField("uuid", StringType(), False)])

    f1 = sqlContext.createDataFrame(lawyer_k_v_1, schema=schema)


    f2 = sqlContext.createDataFrame(lawyer_k_v_null, schema=schema2)
    # f.show()
    # , mode = "overwrite"
    # useUnicode = true & characterEncoding = utf8，指定写入mysql时的数据编码，否则会乱码。
    # f.write.jdbc(url='jdbc:mysql://cdh-slave1:3306/laws_doc_zhangye_update1?useUnicode=true&characterEncoding=utf8', table='judgment_zhangye_etl01',properties={"user": "root", "password": "root"},mode="overwrite")
    f1.write.jdbc(url='jdbc:mysql://cdh5-slave2:3306/laws_doc_zhangye_v2?useUnicode=true&characterEncoding=utf8', table='judgment_zhangye_400w_v3_01',properties={"user": "weiwc", "password": "HHly2017."})
    f2.write.jdbc(url='jdbc:mysql://cdh5-slave2:3306/laws_doc_zhangye_v2?useUnicode=true&characterEncoding=utf8', table='judgment_zhangye_400w_v3_01_null',properties={"user": "weiwc", "password": "HHly2017."})
    sc.stop()
