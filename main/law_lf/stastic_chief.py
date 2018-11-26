# encoding:utf-8
import MySQLdb
import json
import multiprocessing
import datetime
import pandas as pd
# 更新表use_stasitc
#
# def update(int_num):
#     con = MySQLdb.connect(host='192.168.12.34', user='liuf', passwd='123456', db='laws_doc', charset='utf8')
#     cursor = con.cursor()
#     sql = "select uuid, judge_chief_new from tmp_wxy"
#     cursor.execute(sql)
#     row = cursor.fetchall()
#     for n in int_num:
#         sql = "update use_stastic set judge_chief_new= '%s' where uuid='%s'" % (row[n][1], row[n][0])
#         cursor.execute(sql)
#     con.commit()
#     cursor.close()
#     con.close()
# if __name__ == '__main__':
#     pool = multiprocessing.Pool(processes=7)
#     pool.apply_async(update, (xrange(40 * 10000),))
#     pool.apply_async(update, (xrange(40 * 10000, 80 * 10000),))
#     pool.apply_async(update, (xrange(80*10000, 120*10000), ))
#     pool.apply_async(update, (xrange(120*10000, 160*10000), ))
#     pool.apply_async(update, (xrange(160*10000, 200*10000), ))
#     pool.apply_async(update, (xrange(200 * 10000, 240 * 10000),))
#     pool.apply_async(update, (xrange(240 * 10000, 250 * 10000),))
#     pool.close()
#     pool.join()

con = MySQLdb.connect(host='192.168.12.34', user='liuf', passwd='123456', db='laws_doc', charset='utf8')
cursor = con.cursor()
# sql = "select uuid,judge_chief_new from tmp_wxy"
sql = "select uuid,casedate,court_new,duration,crime_reason,defendant_new,law_office,judge_chief_new from use_stastic"
cursor.execute(sql)
row = cursor.fetchall()

def defendantlist(defendant_list):
    dd = []
    for d in defendant_list:
        if '||' in d:
            list = d.split('||')
            for a in list:
                if a:
                    dd.append(a)
        else:
            dd.append(d)
    dd_list = pd.Series(dd).value_counts()[:10]
    defendant_top={}
    for i in range(len(dd_list)):
        defendant_top[dd_list.keys()[i]]=int(dd_list[i])
    return defendant_top

def chieflist(row):
    chief_list = []
    for i in row:
        if i[7]!='' and i[7]!='None':
            if '||' in i[7]:
                alist = i[7].split('||')
                for a in alist:
                    if a:
                        chief_list.append(a+'||'+i[2])
            else:
                chief_list.append(i[7]+'||'+i[2])
    return list(set(chief_list))
chief_list=chieflist(row)

for c in chief_list:
    c_list = c.split('||')
    chief_num=0
    # 律师
    defendant_list = []
    # top10案由
    reason_list = []
    # top10律所
    office = []
    # 近十年处理的案件数
    new10_dict = {}
    t_year_num1=0;t_year_num2=0;t_year_num3=0;t_year_num4=0;t_year_num5=0;t_year_num6=0;t_year_num7=0;t_year_num8=0;t_year_num9=0;t_year_num10=0
    # 诉讼时长
    duration_r = {}
    duration_num1=0;duration_num2=0;duration_num3=0;duration_num4=0;duration_num5=0;duration_num6=0;duration_num7=0;duration_num8=0;duration_num9=0;duration_num10=0;duration_num11=0;
    for i in row:
        if c_list[0] in i[7] and c_list[1] == i[2]:
            chief_num += 1
            if i[5] != '' and i[5] != 'None':
                defendant_list.append(i[5])
            if i[1] != '' and i[1] != 'None':
                t = datetime.datetime.strptime(i[1], "%Y-%m-%d")
                t_year = int(t.year)
                if t_year == 2017:
                    t_year_num1 += 1
                elif t_year == 2016:
                    t_year_num2 += 1
                elif t_year == 2015:
                    t_year_num3 += 1
                elif t_year == 2014:
                    t_year_num4 += 1
                elif t_year == 2013:
                    t_year_num5 += 1
                elif t_year == 2012:
                    t_year_num6 += 1
                elif t_year == 2011:
                    t_year_num7 += 1
                elif t_year == 2010:
                    t_year_num8 += 1
                elif t_year == 2009:
                    t_year_num9 += 1
                elif t_year == 2008:
                    t_year_num10 += 1
            if i[3] != '' and i[3] != 'None':
                duration_int = int(i[3])
                if duration_int <= 10:
                    duration_num1 += 1
                elif duration_int > 10 and duration_int <= 20:
                    duration_num2 += 1
                elif duration_int > 20 and duration_int <= 30:
                    duration_num3 += 1
                elif duration_int > 30 and duration_int <= 40:
                    duration_num4 += 1
                elif duration_int > 40 and duration_int <= 50:
                    duration_num5 += 1
                elif duration_int > 50 and duration_int <= 60:
                    duration_num6 += 1
                elif duration_int > 60 and duration_int <= 70:
                    duration_num7 += 1
                elif duration_int > 70 and duration_int <= 80:
                    duration_num8 += 1
                elif duration_int > 80 and duration_int <= 90:
                    duration_num9 += 1
                elif duration_int > 90 and duration_int <= 120:
                    duration_num10 += 1
                elif duration_int > 120:
                    duration_num11 += 1
            if i[4] != '' and i[4] != 'None':
                reason_list.append(i[4])
            if i[6] != '' and i[6] != 'None':
                office.append(i[6])
 # top10律所
    office_list = pd.Series(office).value_counts()[:10]
    office_top = {}
    for i in range(len(office_list)):
        office_top[office_list.keys()[i]] = int(office_list[i])
# top10案由
    reason_top = defendantlist(reason_list)
# top10律师
    defendant_all_dict = defendantlist(defendant_list)
# 近10年案件数
    new10_dict[u'2017年'] = t_year_num1
    new10_dict[u'2016年'] = t_year_num2
    new10_dict[u'2015年'] = t_year_num3
    new10_dict[u'2014年'] = t_year_num4
    new10_dict[u'2013年'] = t_year_num5
    new10_dict[u'2012年'] = t_year_num6
    new10_dict[u'2011年'] = t_year_num7
    new10_dict[u'2010年'] = t_year_num8
    new10_dict[u'2009年'] = t_year_num9
    new10_dict[u'2008年'] = t_year_num10
# 诉讼时长
    duration_r[u'10天以下'] = duration_num1
    duration_r[u'10-20天'] = duration_num2
    duration_r[u'20-30天'] = duration_num3
    duration_r[u'30-40天'] = duration_num4
    duration_r[u'40-50天'] = duration_num5
    duration_r[u'50-60天'] = duration_num6
    duration_r[u'60-70天'] = duration_num7
    duration_r[u'70-80天'] = duration_num8
    duration_r[u'80-90天'] = duration_num9
    duration_r[u'90-120天'] = duration_num10
    duration_r[u'120天以上'] = duration_num11

    new10_dict = json.dumps(new10_dict, ensure_ascii=False)
    duration_r = json.dumps(duration_r, ensure_ascii=False)
    defendant_all_dict = json.dumps(defendant_all_dict, ensure_ascii=False)
    reason_top = json.dumps(reason_top, ensure_ascii=False)
    office_top = json.dumps(office_top, ensure_ascii=False)
    value = [c_list[0], chief_num,c_list[1],new10_dict, duration_r, reason_top, office_top, defendant_all_dict]
    # print c_list[0],chief_num,c_list[1],new10_dict, duration_r, reason_top, office_top, defendant_all_dict
  # 插入数据
    insert_sql = "insert into scene_chief(chief_new,chief_num,court,new10_dict,duration_dict,reason_top,office_top,defendant_top) values (%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(insert_sql, value)
con.commit()

