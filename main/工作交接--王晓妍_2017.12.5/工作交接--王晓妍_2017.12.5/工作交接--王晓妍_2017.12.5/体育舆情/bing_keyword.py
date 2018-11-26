# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 18:55:30 2017

@author: Administrator
"""

# 体育舆情发掘关键词 + 词云
import MySQLdb
conn = MySQLdb.connect(host='192.168.12.34',user='wxy',passwd='123456',db='spider',charset='utf8')
cursor = conn.cursor()
cursor.execute("select new_content,name,comments_num from tmp_weibo where sub_id=6")
bo_result = cursor.fetchall()

cursor.execute("select tie_content,tieba_name,reply_num from tmp_tieba where sub_id=6") 
ba_result=cursor.fetchall()

cursor.execute('select web_title,web_name,web_comment_num from tmp_news where sub_id=6')
new_result=cursor.fetchall()

cursor.execute("select content,name,comments_num from tmp_wechat where sub_id=6")
chat_result=cursor.fetchall()

content=[]
for r in bo_result:
    if r[0]!=None:
        content.append(r[0])
for r in ba_result:
    if r[0]!=None:
        content.append(r[0])
for r in new_result:
    if r[0]!=None:
        content.append(r[0])
for r in chat_result:
    if r[0]!=None:
        content.append(r[0])
      

import jieba
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud,ImageColorGenerator
from PIL import Image
content=list(set(content)) 
stopword=[line.strip().decode('utf8') for line in open('D:\\study\\dictionary\\stopword.txt').readlines()]
def wordCount(file): 
    bow=[]
    for i in content:
        n=set(jieba.cut(i,cut_all=False))-set(stopword)
        bow.append(list(n))
    
    word_l=[]
    for i in range(len(bow)):
        #fout.write(str(bow[i]))#显示的是unicode
        if len(bow[i])!=0:
            for j in range(len(bow[i])):
                word_l.append(bow[i][j])
    wordCount={}
    for word in word_l:
        if word in wordCount.keys():
            wordCount[word]=wordCount[word]+1
        else:
            wordCount[word]=1
    return [(k,wordCount[k]) for k in wordCount.keys()]
#print wordCount(path)            

def generateCloud(filename,imagename,cloudname,fontname):  
   alice = np.array(Image.open(imagename))            # 读取背景图片  
   wc = WordCloud(background_color="white", # 背景颜色max_words=2000,# 词云显示的最大词数  
               mask=alice,            # 设置背景图片  
               stopwords=stopword,      # 停止词  
               font_path=fontname,       # 兼容中文字体  
               max_font_size=150)        # 字体最大值  
       
        #txtFreq例子为[('词a', 100),('词b', 90),('词c', 80)]  
   txtFreq = wordCount(filename)  
   wc.generate_from_frequencies(txtFreq)  
        # 生成图片  
   img_color = ImageColorGenerator(np.array(Image.open(imagename)))#颜色与原图片一样
   plt.imshow(wc.recolor(color_func=img_color))  
   plt.axis("off")  
        # 绘制词云  
   plt.figure()  
        # 保存词云  
   wc.to_file(cloudname)  

if __name__ == '__main__':  
      # 获取当前文件路径  
    fontname = 'D://tool//simhei.ttf'    # 中文字体路径  
    filename = content   # txt文件路径  
    imagename = 'E:\\record\\service2\\timg1.jpg' # 背景图片路径  
    cloudname = 'E:\\record\\service2\\comment.png'  # 标签云路径  
    generateCloud(filename,imagename, cloudname,fontname)