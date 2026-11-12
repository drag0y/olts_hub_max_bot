def level_color(level: float):
    '''
    Функция для покраски уровня сигналов
    '''
    if -1.00 >= level >= -25.00:
        result = '🟢'
    elif -25.01 >= level >= -30.00:
        result = '🟡'
    elif level <= -30.01:
        result = '🔴'
    else:
        result = '⚪️'

    return result
