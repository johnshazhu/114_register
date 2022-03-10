# 114_register
北京114微信公众号上挂号用

data目录下新建一config.property文件，内容大概如下
```
cookie=114公众号中使用的cookie，可以通过抓包方式获取
name=就诊人姓名
keyword=医院关键词
department=科室关键词
autoDelay=轮询间隔秒数（默认10秒）
loop=是否自动查询（0否 其他是）
deadline=期望最晚挂号时间（格式yyyy-MM-dd，如2000-01-01）
date=要挂号的指定日期（格式yyyy-MM-dd，如2000-01-01）
```

使用前提：北京114公众号中添加了相关就诊人信息及就诊卡（医保卡）信息
配置好以上信息后，执行hospital.py
