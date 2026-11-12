from services.backend_api_connect import get_api
from services.level_color import level_color


def get_port_status(olt_id, port, token):
    '''
    Функция просмотра статуса pon порта
    '''
    result = []
    onu = ''

    URL = f'/api/oltinfo/port/{olt_id}/{port}'

    port_info = get_api(URL, token)

    if port_info['port_status']['count'] == 0:
        return result
    
    '''
    Получаем словарь с ОНУшками, делаем красивый вывод.
    Далее делаем массив, и добавляем в него элементы по 16 ОНУ,
    что бы не привысить допустимый предел по количеству символов
    для отправки в телеграм
    '''
    ports_count = 0
    for p in port_info['port_status']['onu']:
        ports_count += 1
        onu += f'''
<b>ID:</b> {p['id']} {'✅' if p['onu_status'] == 'ONLINE' else '❌'}
<b>ONU:</b> {p['onu']}
<b>Descr:</b> {p['descr']}
<b>ONU status:</b> <b>{p['onu_status']}</b> {p['down_time']}
<b>RX ONU:</b> {p['rx_onu']} {level_color(p['rx_onu'])}
<b>RX OLT:</b> {p['rx_olt']} {level_color(p['rx_olt'])}
'''
        if ports_count == 16:
            result.append(onu)
            ports_count = 0
            onu = ''

    result.append(onu)

    return result


def get_olts_list(token):
    '''
    Функция получения списка ОЛТов
    '''
    result = []
    olts = ''
    URL = f"/api/oltinfo/oltslist"
    olts_list = get_api(URL, token)
    '''
    Получаем словарь с ОЛТами, делаем красивый вывод.
    Далее делаем массив, и добавляем в него элементы по 50 ОЛТов,
    что бы не привысить допустимый предел по количеству символов
    для отправки в телеграм
    '''
    olts_count = 0
    for o in olts_list:
        olts_count += 1
        olts += f'''
<b>ID:</b> {o['id']}
<b>Имя ОЛТа:</b> {o['hostname']}
<b>IP адрес:</b> {o['ip_address']}
'''
        if olts_count == 32:
            result.append(olts)
            olts_count = 0
            olts = ''

    result.append(olts)

    return result


def get_olt_info(olt_id, token):
    '''
    Функция получения информации об ОЛТе
    '''
    result = ''
    URL = f"/api/oltinfo/{olt_id}"
    olt_info = get_api(URL, token)

    result += f'''
<b>ID:</b> {olt_info['id']}
<b>Hostname:</b> {olt_info['hostname']}
<b>IP Address:</b> {olt_info['ip_address']}
<b>Описание:</b> {olt_info['descr']}

<b>Статус ОЛТа:</b> {olt_info['olt_state']}
<b>Uptime:</b> {olt_info['olt_uptime']}
<b>Зарегистрированные ОНУ:</b> {olt_info['countonu']}
<b>Незарегистрированные ОНУ:</b>
{"\n".join(f"MAC/SN: {x['mac']} Порт: {x['oltport']}" for x in olt_info['unregonu'])}
'''
        
    return result