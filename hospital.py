import ssl

import api
import api_config
import register

KEYWORD = 'keyword'
DEPARTMENT = 'department'
deadline = None
hospital_code_name_map = {}
department_name_code_map = {}


# 获取医院列表
def get_hospital_list(keywords):
    query = {
            'keywords': keywords,
            'sortType': 'COMPREHENSIVE',
            'areaId': 0,
            'pageNo': 1,
            'pageSize': 15,
    }
    return api.api_call(api_config.API_114_HOSPITAL_LIST, query)


# 获取医院详情
def get_hospital_detail(hos_code):
    query = {
            'hosCode': hos_code,
    }
    return api.api_call(api_config.API_114_HOSPITAL_DETAIL, query)


# 获取医院科室列表
def get_hospital_department_list(hos_code):
    global department_name_code_map
    target_department = api.config_dict[DEPARTMENT]
    query = {
            'hosCode': hos_code,
    }
    rsp = api.api_call(api_config.API_114_HOSPITAL_DEPARTMENT_LIST, query)
    if api.is_success_response(rsp):
        rsp_data = rsp['data']
        if isinstance(rsp_data, dict) and 'list' in rsp_data:
            depart_list = rsp_data['list']
            if isinstance(depart_list, list):
                for department_info in depart_list:
                    if isinstance(department_info, dict):
                        department_code = department_info['code']
                        department_name_code_map[department_code] = department_info
    if len(department_name_code_map) > 0:
        for key in department_name_code_map:
            info = department_name_code_map[key]
            dep_name = info['name']
            dep_1_code = info['code']
            dep_2_code = ''
            sub_list = info['subList']
            if isinstance(sub_list, list):
                if len(sub_list) == 1:
                    dep_2_code = sub_list[0]['code']
                for sub in sub_list:
                    sub_name = sub['name']
                    sub_dep_1_code = sub['dept1Code']
                    sub_dep_2_code = sub['code']
                    print(f'{sub_name} {sub_dep_1_code} {sub_dep_2_code}')
            print(f'{dep_name} {dep_1_code} {dep_2_code}')

            if len(str(target_department)) > 0 and str(dep_name).__contains__(target_department):
                department_code_info = {'firstDeptCode': dep_1_code, 'secondDeptCode': dep_2_code}
                duty_resp = register.get_department_duty_list(None, hos_code, department_code_info)
                available_map = {}
                register.parse_hospital_department_duty_info(code, department_code_info, duty_resp, deadline, available_map)
                break


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context

    api.load_config_info()
    deadline = api.config_dict['deadline']
    # 检查是否配置指定医院
    keyword = ''
    if KEYWORD in api.config_dict:
        keyword = api.config_dict[KEYWORD]
        if len(str(keyword)) > 0:
            resp = get_hospital_list(keyword)
            if api.is_success_response(resp):
                data = resp['data']
                if isinstance(data, dict) and 'list' in data:
                    hos_list = data['list']
                    if isinstance(hos_list, list):
                        for hospital in hos_list:
                            name = hospital['name']
                            code = hospital['code']
                            hospital_code_name_map[code] = name
                            print(hospital)
                            get_hospital_department_list(code)

