import ssl

import register
import timer
import api

# 轮询间隔时间 - 默认8秒
LOOP_QUERY_DELAY = 8
DEADLINE = 'deadline'
LOOP = 'loop'


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    # 加载配置信息
    register.init_config()
    # 获取就诊信息卡
    register.get_patient_list()

    topic_key = 'KW_COVID_2019'
    area_id = 110112
    deadline = api.config_dict[DEADLINE]

    # 获取医院列表信息
    hos_list_rsp = register.get_hospitals_by_area_and_topic(topic_key, area_id)

    if register.parse_hospital_list(hos_list_rsp):
        loop = 0
        if LOOP in api.config_dict:
            loop_config = api.config_dict[LOOP]
            if str(loop_config) != '0' and len(str(loop_config)) > 0:
                loop = 1
        if loop == 1:
            # 轮询对应科室中预约状态信息
            available_map = {}
            timer = timer.RepeatingTimer(LOOP_QUERY_DELAY, register.find_register_available_hospital,
                                         args=[topic_key, deadline, available_map])
            timer.start()
