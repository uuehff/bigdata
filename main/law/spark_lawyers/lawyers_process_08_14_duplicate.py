# -*- coding: utf-8 -*-

from  pyspark import SparkContext,SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *
import os
import json

if __name__ == "__main__":
    # if len(sys.argv) > 2:
    #     host = sys.argv[1]
    #     hbase_table_read = sys.argv[2]
    #     hbase_table_save = sys.argv[3]
    # else:
    # host = '192.168.12.35'
    # hbase_table_read = 'laws_doc:judgment'
    # hbase_table_save = 'laws_doc:label'
    PYSPARK_PYTHON = "C:\\Python27\\python.exe"    #多版本python情况下，需要配置这个变量指定使用哪个版本
    os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
    conf = SparkConf()
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)
    # sc.setLogLevel("ERROR")  # ALL, DEBUG, ERROR, FATAL, INFO, OFF, TRACE, WARN '(select id,uuid,plaintiff_info,defendant_info from tmp_lawyers ) tmp'
    df = sqlContext.read.jdbc(url='jdbc:mysql://cdh5-slave2:3306/laws_doc_lawyers_new', table='(select id,name,pra_number,nation,edu_origin,politics,org_name,org_identity,birth_date,first_pra_time,qua_number,qua_time from lawyer_duplicate order by pra_number ) tmp',column='id',lowerBound=1,upperBound=277365,numPartitions=1,properties={"user": "weiwc", "password": "HHly2017."})
    # df2 = sqlContext.read.jdbc(url='jdbc:mysql://cdh-slave1:3306/laws_doc2', table='(select id,plaintiff_info,defendant_info from tmp_lawyers ) tmp2',column='id',lowerBound=0,upperBound=100000,numPartitions=10,properties={"user": "root", "password": "root"})
    # df= sqlContext.read.jdbc(url='jdbc:mysql://cdh-slave1:3306/laws_doc', table='judgment_etl_lawlist',
                              # predicates=["id >= 2311362 and id <= 2311366", "id > 2311366 and id <= 2311372"],
                              # "id > 30000 and id <= 40000", "id > 40000 and id <= 50000",
                              # "id > 50000 and id <= 60000", "id > 60000 and id <= 70000",
                              # "id > 70000 and id <= 80000", "id > 80000 and id <= 90000",
                              # "id > 90000 and id <= 10000", "id > 100000 and id <= 110000",
                              # "id > 110000 and id <= 120000", "id > 120000 and id <= 130000",
                              # "id > 130000 and id <= 140000", "id > 140000 and id <= 150000",
                              # "id > 150000 and id <= 160000"],
                              # properties={"user": "root", "password": "root"})

    # def p(x):
    #     print type(x)
    #     print type(x[0]),type(x[1]),type(x[2])
    #     print x[0],x[1],x[2]
    # def p_(x):
        # print type(x)
        # print x[0],x[1]
        # for i in x[1]:
        #     print type(i),i
    def p2(x):
        # k,v = x[0],x[1]
        # print k,
        # print type(v)
        for i2 in x:
            print i2,
        print "\n"

    # id, name, pra_number, nation, edu_origin, politics, org_name, org_identity, birth_date, first_pra_time, qua_number, qua_time

    def get_results(x):

        for i in x:
            return i


    results = df.map(lambda x:x[1:]).groupBy(lambda x:x[1]).mapValues(lambda x: get_results(x)).map(lambda x:x[1])

    # print "+++++++++++++++++++++" + str(results.count())
    # results.foreach(p2)
    schema = StructType([StructField("name", StringType(), False),
                         StructField("pra_number", StringType(), True),
                         StructField("nation", StringType(), True),
                         StructField("edu_origin", StringType(), True),
                         StructField("politics", StringType(), True),
                         StructField("org_name", StringType(), True),
                         StructField("org_identity", StringType(), True),
                         StructField("birth_date", StringType(), True),
                         StructField("first_pra_time", StringType(), True),
                         StructField("qua_number", StringType(), True),
                         StructField("qua_time", StringType(), True)])

    f = sqlContext.createDataFrame(results, schema=schema)
    # , mode = "overwrite"
    # useUnicode = true & characterEncoding = utf8，指定写入mysql时的数据编码，否则会乱码。
    f.write.jdbc(url='jdbc:mysql://cdh5-slave2:3306/laws_doc_lawyers_new?useUnicode=true&characterEncoding=utf8', table='lawyer_duplicate_v2',properties={"user": "weiwc", "password": "HHly2017."})

    sc.stop()