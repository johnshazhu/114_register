# base_url
API_114_BASE = 'https://www.114yygh.com/mobile'
# 专题医院列表
# ?_time=1612257618457&keywords=&topicKey=KW_COVID_2019&sortType=COMPREHENSIVE&areaId=110112&pageNo=1&pageSize=15
API_114_HOSPITAL_TOPIC_LIST = f'{API_114_BASE}/hospital/topic/list'
# ?_time=1612257818586
# {"hosCode":"792","firstDeptCode":"0","secondDeptCode":"200053142","topicKey":"KW_COVID_2019"}
# 预约挂号页面日期及可预约信息
API_114_DEP_LIST = f'{API_114_BASE}/product/list'
# ?_time=1612257818586&hosCode=792
API_114_AUTHORITY = f'{API_114_BASE}/product/authority'
# ?_time=1612257821369
# {"hosCode":"792","firstDeptCode":"0","secondDeptCode":"200053142","target":"2021-02-07","topicKey":"KW_COVID_2019"}
# 预约挂号页面当天详细信息
API_114_DETAIL = f'{API_114_BASE}/product/detail'
# ?_time=1612257823319
# {"hosCode":"792","firstDeptCode":"0","secondDeptCode":"200053142","target":"2021-02-07","uniqProductKey":"163e0b6482eb989d8ba098aa7df31fc730ae2634","dutyTime":0}
API_114_CONFIRM = f'{API_114_BASE}/product/confirm'
# ?_time=1612257818586&label=depProclamation&bizType=DEPARTMENT&hosCode=792&secondDept=200053142
# 预约挂号页面弹窗内容
API_114_COMMON_CONTENT = f'{API_114_BASE}/common/content'
# ?_time=1612257829110&mobile=xxx&smsKey=ORDER_CODE&uniqProductKey=163e0b6482eb989d8ba098aa7df31fc730ae2634
API_114_VERIFY_CODE = f'{API_114_BASE}/common/verify-code/send'
# ?_time=1612257818586&hosCode=792&firstDeptCode=0&secondDeptCode=200053142
# 预约挂号页面医院信息
API_114_DEPARTMENT_HOSPITAL_DETAIL = f'{API_114_BASE}/department/hos/detail'
# ?_time=1612257822810&code=reg_ncp_survey&hosCode=792
API_114_TERSE_SURVEY_RESULT = f'{API_114_BASE}/terse/survey/result'
# ?_time=1612257822946
API_114_USER_INFO = f'{API_114_BASE}/user/info'
# ?_time=1612257825632
# {"idCardNo":"xxx","idCardType":"IDENTITY_CARD"}
API_114_ORDER = f'{API_114_BASE}/patient/order/check'
# ?_time=1612257825892&idCardType=IDENTITY_CARD&idCardNo=xxx
API_114_CARD_LIST = f'{API_114_BASE}/patient/card/list'
# ?_time=1612257823319
API_114_PATIENT_LIST = f'{API_114_BASE}/patient/list'
# ?_time=1612257844330
# {"hosCode":"792","firstDeptCode":"","secondDeptCode":"200053142","treatmentDay":"2021-02-07",
# "uniqProductKey":"163e0b6482eb989d8ba098aa7df31fc730ae2634","cardType":"SOCIAL_SECURITY",
# "cardNo":"xxx","smsCode":"xxx","jytCardId":"","hospitalCardId":"","phone":"xxx","dutyTime":0}
API_114_ORDER_SAVE_CHECK = f'{API_114_BASE}/order/save/check'
# ?_time=1612257844660
# {"hosCode":"792","firstDeptCode":"","secondDeptCode":"200053142","treatmentDay":"2021-02-07",
# "uniqProductKey":"163e0b6482eb989d8ba098aa7df31fc730ae2634","cardType":"SOCIAL_SECURITY",
# "cardNo":"xxx","smsCode":"xxx","jytCardId":"","hospitalCardId":"","phone":"xxx","dutyTime":0,"orderFrom":"COVID"}
API_114_ORDER_SAVE = f'{API_114_BASE}/order/save'
# ?_time=1612257846239&orderNo=xxx&hosCode=792
API_114_ORDER_DETAIL = f'{API_114_BASE}/order/detail'

# hospital list
# ?_time=1612261430514&keywords=&pageNo=1&pageSize=15&sortType=COMPREHENSIVE&areaId=0
# 医院列表，支持关键词搜索
API_114_HOSPITAL_LIST = f'{API_114_BASE}/hospital/list'
# 医院详情
API_114_HOSPITAL_DETAIL = f'{API_114_BASE}/hospital/detail'
# 医院科室列表
API_114_HOSPITAL_DEPARTMENT_LIST = f'{API_114_BASE}/department/hos/list'
# ?_time=1612261600193
# {"keys":"HOS_AREA"}
API_114_AREA_ENUM = f'{API_114_BASE}/common/enum'

