法院，省市县，字符串说明：

1、
省份、最高人民法院：使用两个字符：
其中，最高人名法院为：00

2、市、高级法院：使用三个字符串：

其中高级法院为：000
市为其他。
一个省有两个高级法院的：则为：000,001,
比如:
4765	新疆维吾尔自治区高级人民法院	新疆维吾尔自治区			高级	14	14000		
4766	新疆维吾尔自治区高级人民法院伊犁哈萨克自治州分院	新疆维吾尔自治区			高级	14	14001		

3、具体市下面的法院用三个字符串表示：

从001开始！


一个具体的法院名称的uid长度为：
最高人民法院：00
高级人民法院：2+3 = 5位
普通法院：2+3+3 = 8位


