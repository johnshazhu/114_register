import json

import api
import api_config
import handle_sms_code
import notification_util

# 需要短信验证码
NEED_SMS_CODE = 4
# 不需要短信验证
NO_SMS_CODE = 2

# 当前就诊人信息
g_patient_info = {}
# 预约下单时的信息
g_order_save_info = {}

# 医院编码-科室 map
code_department_map = {}
# 医院编码-医院名 map
code_name_map = {}
g_topic_key = None


def init_config():
    api.load_config_info()


# 'topicKey': 'KW_COVID_2019',
# 'areaId': 110112,
# 'keyword': ''
# 根据区域码、专题或搜索关键词获取医院列表
def get_hospitals_by_area_and_topic(topic_key, area_id, keyword=''):
    global g_topic_key
    g_topic_key = topic_key
    query = {
            'keywords': keyword,
            'sortType': 'COMPREHENSIVE',
            'areaId': area_id,
            'pageNo': 1,
            'pageSize': 15,
    }
    if topic_key is not None:
        query['topicKey'] = topic_key
    return api.api_call(api_config.API_114_HOSPITAL_TOPIC_LIST, query, post_data=None)


# 解析返回的医院列表，搜集医院编码-科室 map、医院编码-医院名 map
def parse_hospital_list(response):
    global code_department_map
    global code_name_map
    if api.is_success_response(response):
        data = response['data']
        if isinstance(data, dict):
            if 'list' in data:
                data_list = data['list']
                if isinstance(data_list, list):
                    for item in data_list:
                        code = None
                        if 'hosCode' in item:
                            code = item['hosCode']
                            code_name_map[code] = item['hosName']
                        elif 'code' in item:
                            code = item['code']
                            code_name_map[code] = item['name']
                        if 'depts' in item:
                            departments = item['depts']
                            if isinstance(departments, list):
                                for dep in departments:
                                    code_department_map[code] = dep
                                    break
    else:
        return False
    return True


# topic_key: 专题key，例如'KW_COVID_2019'
# hospital_code: 医院编码
# department: 门诊科室
def get_department_duty_list(topic_key, hospital_code, department):
    post_content_map = {
        'hosCode': hospital_code,
        'firstDeptCode': department['firstDeptCode'],
        'secondDeptCode': department['secondDeptCode'],
    }
    if topic_key is not None:
        post_content_map['topic_key'] = topic_key
    post_content = bytes(json.dumps(post_content_map), encoding='utf-8')
    return api.api_call(api_config.API_114_DEP_LIST, post_data=post_content)


def find_register_available_hospital(topic_key, deadline, available_map):
    dict(available_map).clear()
    for code in code_department_map:
        department = code_department_map[code]
        resp = get_department_duty_list(topic_key, code, department)
        parse_hospital_department_duty_info(code, department, resp, deadline, available_map)
    if len(dict(available_map)) > 0:
        print(available_map)


# 解析科室预约情况
def parse_hospital_department_duty_info(code, department, resp, deadline, available_map):
    if api.is_success_response(resp):
        res_data = resp['data']
        if isinstance(res_data, dict) and 'calendars' in res_data:
            calendars = res_data['calendars']
            if isinstance(calendars, list):
                for day in calendars:
                    if isinstance(day, dict) and 'status' in day:
                        # print(f'{day}')
                        status = day['status']
                        date = day['dutyDate']
                        # 指定就要挂某一天的号时
                        if 'date' in api.config_dict and len(str(api.config_dict['date'])) == 10 and\
                                date != api.config_dict['date']:
                            continue

                        if date > deadline:
                            continue
                        # if status != 'NO_INVENTORY' and
                        # status != 'SOLD_OUT' and status != 'TOMORROW_OPEN':
                        if status == 'AVAILABLE':
                            available_map[code_name_map[code]] = date
                            notification_util.show_notification('可预约', f'{date} {code_name_map[code]} 可预约')
                            duty_info = get_department_day_duty_detail(date, g_topic_key, code, department)
                            duty_detail = parse_department_day_duty_info(code_name_map[code], duty_info)
                            if duty_detail is not None:
                                duty_time = '0'
                                key = duty_detail['uniqProductKey']
                                if 'period' in duty_detail:
                                    period = duty_detail['period']
                                    if isinstance(period, dict):
                                        duty_time = period['dutyTime']
                                        print(f'dict 就诊时段 {duty_time}')
                                    elif isinstance(period, list):
                                        concat_start_duty_time = ''
                                        # 根据配置的预约时段匹配
                                        config_duty_time = api.config_dict['dutyTime']
                                        # 预约时段 0900-0930
                                        if len(str(config_duty_time)) == len('0900-0930') and str(
                                                config_duty_time).__contains__('-'):
                                            start = str(config_duty_time).split('-')[0]
                                            end = str(config_duty_time).split('-')[1]
                                            # date 2023-08-05
                                            register_date = str(date).replace('-', '')
                                            # concat_start_duty_time = 202308050900
                                            concat_start_duty_time = str(config_duty_time) + str(start)
                                            # concat_end_duty_time = 20230800930
                                            concat_end_duty_time = str(config_duty_time) + str(end)
                                        for period_item in period:
                                            duty_time = period_item['dutyTime']
                                            # 202308120805-202308120835
                                            duty_time_view = period_item['dutyTimeView']
                                            current_period_start_duty_time = str(duty_time).split('-')[0]
                                            if len(concat_start_duty_time) > 0 and int(current_period_start_duty_time) >= int(concat_start_duty_time):
                                                print(f'list 就诊时段 {duty_time}, ${duty_time_view}')
                                                break
                                g_order_save_info['dutyTime'] = duty_time
                                confirm_resp = register_confirm(key, date, g_topic_key, code, department, duty_time)
                                parse_register_confirm_info(confirm_resp, code, date, department, key)
                                return True
    return False


# 获取科室当天预约信息
def get_department_day_duty_detail(date, topic_key, hospital_code, department):
    post_content_map = {
        'hosCode': hospital_code,
        'firstDeptCode': department['firstDeptCode'],
        'secondDeptCode': department['secondDeptCode'],
        'target': date,
        # 'topicKey': topic_key,
    }
    if topic_key is not None:
        post_content_map['topicKey'] = topic_key
    post_content = bytes(json.dumps(post_content_map), encoding='utf-8')
    return api.api_call(api_config.API_114_DETAIL, post_data=post_content)


# 解析科室当天预约信息
def parse_department_day_duty_info(hospital, duty_info):
    if api.is_success_response(duty_info):
        data = duty_info['data']
        if isinstance(data, list):
            for item in data:
                duty_code = None
                if 'dutyCode' in item:
                    duty_code = item['dutyCode']
                if 'detail' in item and isinstance(item['detail'], list):
                    for detail_item in item['detail']:
                        if isinstance(detail_item, dict):
                            if 'doctorName' in detail_item:
                                doctor_name = detail_item['doctorName']
                                # 指定预约挂号的医生，但这次未匹配到则查看下一个
                                if str(api.config_dict['doctorName']) > 0 and \
                                        str(api.config_dict['doctorName']) != str(doctor_name):
                                    continue

                            if 'fcode' in detail_item and 'ncode' in detail_item:
                                fcode = detail_item['fcode']
                                ncode = detail_item['ncode']
                                if fcode != ncode:
                                    if str(fcode).endswith(str(ncode)):
                                        print(f'{hospital} {duty_code} fcode endwith ncode')
                                        continue
                                    # 医生头衔 普通医生或专家
                                    doctor_title_name = detail_item['doctorTitleName']
                                    # key 上午下午不一样
                                    # unique_product_key = detail_item['uniqProductKey']
                                    if 'MORNING' == duty_code:
                                        print(f'{hospital} 上午 {doctor_title_name} 可预约')
                                    elif 'AFTERNOON' == duty_code:
                                        print(f'{hospital} 下午 {doctor_title_name} 可预约')
                                    return detail_item
    return None


# 可预约后，进行预约确认
def register_confirm(key, date, topic_key, hospital_code, department, duty_time='0'):
    post_content_map = {
        'hosCode': hospital_code,
        'firstDeptCode': department['firstDeptCode'],
        'secondDeptCode': department['secondDeptCode'],
        'target': date,
        # 'topicKey': topic_key,
        'uniqProductKey': key,
        'dutyTime': duty_time
    }
    if topic_key is not None:
        post_content_map['topicKey'] = topic_key
    post_content = bytes(json.dumps(post_content_map), encoding='utf-8')
    return api.api_call(api_config.API_114_CONFIRM, post_data=post_content)


# 解析预约确认信息
def parse_register_confirm_info(resp, code, date, department, key):
    if api.is_success_response(resp):
        data = resp['data']
        if isinstance(data, dict):
            name = data['hospitalName']
            depart = data['departmentName']
            title = data['doctorTitleName']
            fee = data['serviceFee']
            visit_time = data['visitTime']
            doctor = data['doctorName']
            g_order_save_info['confirmToken'] = data['confirmToken']
            print(f'{visit_time} {name} {depart} {doctor} {title} {fee}')
            if 'dataItem' in data:
                data_item = data['dataItem']
                if isinstance(data_item, dict):
                    sms_code = data_item['smsCode']
                    if sms_code == NEED_SMS_CODE:
                        print('需要短信验证码')
                        sms_code_resp = get_sms_verify_code(key)
                        if api.is_success_response(sms_code_resp):
                            # 等待验证码
                            notification_util.show_notification('短信验证码', '请注意查看短信验证码并输入')
                            g_order_save_info['code'] = code
                            g_order_save_info['department'] = department
                            g_order_save_info['date'] = date
                            g_order_save_info['key'] = key
                            handle_sms_code.input_sms_code(submit_sms_code_callback)
                    else:
                        # 不需要短信验证码
                        resp = order_check()
                        if api.is_success_response(resp):
                            data = resp['data']
                            if isinstance(data, dict) and 'pass' in data:
                                result = data['pass']
                                if result or result == 'true':
                                    duty_time = '0'
                                    if 'dutyTime' in g_order_save_info:
                                        duty_time = g_order_save_info['dutyTime']
                                    check_save_order(code, department, date, key, duty_time)


# 获取就诊卡信息
def get_patient_list():
    global g_patient_info
    resp = api.api_call(api_config.API_114_PATIENT_LIST)
    if api.is_success_response(resp):
        data = resp['data']
        if isinstance(data, dict):
            count = data['count']
            if count == 0:
                print('需要添加就诊卡信息')
                return None
            patient_list = data['list']
            if isinstance(patient_list, list):
                for patient in patient_list:
                    if isinstance(patient, dict):
                        if patient['patientName'] == api.config_dict['name']:
                            card_list = patient['cardList']
                            if isinstance(card_list, list):
                                for card in card_list:
                                    card_type = card['cardTypeView']
                                    card_no = card['cardNo']
                                    print(f'{card_type} {card_no}')
                            g_patient_info = patient
                            return patient


# 获取短信验证码
def get_sms_verify_code(key):
    query = {
            'mobile': g_patient_info['phone'],
            'smsKey': 'ORDER_CODE',
            'uniqProductKey': key,
    }
    return api.api_call(api_config.API_114_VERIFY_CODE, query)


def submit_sms_code_callback():
    sms_code = handle_sms_code.get_sms_code()
    print(f'submit_sms_code_callback {sms_code}')
    print(g_order_save_info)
    handle_sms_code.destroy()
    duty_time = '0'
    if 'dutyTime' in g_order_save_info:
        duty_time = g_order_save_info['dutyTime']
    check_save_order(g_order_save_info['code'],
                     g_order_save_info['department'],
                     g_order_save_info['date'],
                     g_order_save_info['key'],
                     sms_code,
                     duty_time)
    g_order_save_info.clear()


# 保存订单确认
def check_save_order(code, department, date, key, sms_code='', duty_time='0'):
    if len(g_patient_info) == 0 or g_patient_info['cardList'] is None or len(g_patient_info['cardList']) == 0:
        print('无就诊卡相关信息')
        return False
    card = g_patient_info['cardList'][0]
    post_content_map = {
        'hosCode': code,
        'firstDeptCode': department['firstDeptCode'],
        'secondDeptCode': department['secondDeptCode'],
        'treatmentDay': date,
        'uniqProductKey': key,
        'cardType': card['cardType'],
        'cardNo': card['cardNo'],
        'smsCode': sms_code,
        'jytCardId': '',
        'hospitalCardId': '',
        'phone': g_patient_info['phone'],
        'dutyTime': duty_time
    }
    post_content = bytes(json.dumps(post_content_map), encoding='utf-8')
    resp = api.api_call(api_config.API_114_ORDER_SAVE_CHECK, post_data=post_content)
    if api.is_success_response(resp):
        data = resp['data']
        if isinstance(data, dict):
            if 'state' in data:
                state = data['state']
                if state == 'OK' or state == 'NEED_CONFIRM':
                    save_order(code, department, date, key, sms_code, duty_time)
                    return True
                elif state == 'TOAST':
                    msg = data['msg']
                    if '请重新选择就诊时段' == msg:
                        print('需要重新选择就诊时段')
                        resp = get_department_day_duty_detail(date, g_topic_key, code, department)
                        duty_detail = parse_department_day_duty_info(code_name_map[code], resp)
                        if 'period' in duty_detail:
                            period = duty_detail['period']
                            if isinstance(period, dict):
                                # 没有具体的预约时段
                                period_duty_time = period['dutyTime']
                                duty_time_view = period['dutyTimeView']
                                print(f'新的就诊时段 {period_duty_time}, {duty_time_view}')
                                check_save_order(code, department, date, key, period_duty_time)
                            elif isinstance(period, list):
                                concat_start_duty_time = ''
                                # 根据配置的预约时段匹配
                                config_duty_time = api.config_dict['dutyTime']
                                # 预约时段 0900-0930
                                if len(str(config_duty_time)) == len('0900-0930') and str(
                                        config_duty_time).__contains__('-'):
                                    start = str(config_duty_time).split('-')[0]
                                    end = str(config_duty_time).split('-')[1]
                                    # date 2023-08-05
                                    register_date = str(date).replace('-', '')
                                    # concat_start_duty_time = 202308050900
                                    concat_start_duty_time = str(config_duty_time) + str(start)
                                    # concat_end_duty_time = 20230800930
                                    concat_end_duty_time = str(config_duty_time) + str(end)
                                for period_item in period:
                                    period_duty_time = period_item['dutyTime']
                                    duty_time_view = period_item['dutyTimeView']
                                    current_period_start_duty_time = str(period_duty_time).split('-')[0]
                                    if len(concat_start_duty_time) > 0:
                                        if int(current_period_start_duty_time) >= int(concat_start_duty_time):
                                            print(f'新的就诊时段 {period_duty_time}, {duty_time_view}')
                                            check_save_order(code, department, date, key, period_duty_time)
                                            break
                                    else:
                                        print(f'新的就诊时段 {period_duty_time}, {duty_time_view}')
                                        check_save_order(code, department, date, key, period_duty_time)
                                        break


# 保存订单
def save_order(code, department, date, key, sms_code='', duty_time='0'):
    card = g_patient_info['cardList'][0]
    post_content_map = {
        'hosCode': code,
        'firstDeptCode': department['firstDeptCode'],
        'secondDeptCode': department['secondDeptCode'],
        'treatmentDay': date,
        'uniqProductKey': key,
        'cardType': card['cardType'],
        'cardNo': card['cardNo'],
        'smsCode': sms_code,
        'jytCardId': '',
        'hospitalCardId': '',
        'phone': g_patient_info['phone'],
        'dutyTime': duty_time,
        'orderFrom': 'HOSP',
        'confirmToken': g_order_save_info['confirmToken']
    }
    if g_topic_key is not None and len(str(g_topic_key).split('-')) > 1:
        post_content_map['orderFrom'] = str(g_topic_key).split('-')[1]

    post_content = bytes(json.dumps(post_content_map), encoding='utf-8')
    resp = api.api_call(api_config.API_114_ORDER_SAVE, post_data=post_content)
    if api.is_success_response(resp):
        data = resp['data']
        if isinstance(data, dict) and 'orderNo' in data:
            order_no = data['orderNo']
            print(f'预约成功，订单号 {order_no}')
            order_detail(code, order_no)
    else:
        msg = resp['msg']
        notification_util.show_notification('预约失败', msg)
        print(f'提交预约单失败 : {msg}')


# 预约单检查
def order_check():
    post_content_map = {
        'idCardNo': g_patient_info['idCardNo'],
        'idCardType': g_patient_info['idCardType'],
    }
    post_content = bytes(json.dumps(post_content_map), encoding='utf-8')
    return api.api_call(api_config.API_114_ORDER, post_data=post_content)


# 订单详情
def order_detail(code, order_no):
    query = {
            'orderNo': order_no,
            'hosCode': code,
    }
    resp = api.api_call(api_config.API_114_ORDER_DETAIL, query)
    if api.is_success_response(resp):
        print(resp)
