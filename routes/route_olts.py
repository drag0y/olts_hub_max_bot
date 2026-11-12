import os
from dotenv import load_dotenv
load_dotenv()
from maxapi import F
from maxapi.dispatcher import Router
from maxapi.filters.command import Command
from maxapi.types.updates.message_created import MessageCreated
from maxapi.types.updates.message_callback import MessageCallback
from maxapi.enums import TextFormat

from decorators.auth import user_required
from services.logger import log_write
from services.backend_api_connect import get_api
from variables.users import oltshub_tokens
from kbds.inline import get_callback_btns
from services.olt_info import get_port_status, get_olts_list, get_olt_info
from variables.messages import warning_msg


BUTTON_COL = os.getenv("BUTTON_COL")

olts_router = Router(router_id="olts_router")


@olts_router.message_created(
        (F.message.body.text.lower() == "/olts_list") | 
        (F.message.body.text.lower() == "список олтов")
    )
@user_required
async def olts_list(msg: MessageCreated):
    '''
    Показать список ОЛТов
    '''
    user_id = msg.message.sender.user_id
    olts_list = get_olts_list(oltshub_tokens[str(user_id)])

    for o in olts_list:
        await msg.message.answer(o, format=TextFormat.HTML)

    await msg.message.answer(
        'Для просмотра информации об ОЛТе, введите <code>/olt_info id</code>', 
        format=TextFormat.HTML
        )


@olts_router.message_created(Command('olt_info'))
@user_required
async def olt_info(msg: MessageCreated):
    '''
    Команда просмотра информации об ОЛТе
    '''
    user_id = msg.message.sender.user_id
    result = ''
    try:
        olt_id = msg.message.body.text.split()[-1]
        result = get_olt_info(olt_id, oltshub_tokens[str(user_id)])

        await msg.message.answer(
            text=result, 
            attachments=[
                get_callback_btns(
                    btns={
                        'Опросить ОЛТ': f'update_{olt_id}',
                        'Показать порты': f'showports_{olt_id}',
                    }
                ).as_markup()
            ],
            format=TextFormat.HTML
        )
    except:
        await msg.message.answer('Ошибка! Введите ID ОЛТа.')


@olts_router.message_callback(F.callback.payload.startswith("showports_"))
async def showports_callback(event: MessageCallback) -> None:
    '''
    Callback просмотра портов
    '''
    result = ''
    user_id = event.from_user.user_id
    oltid = event.callback.payload.split('_')[-1]
    URL = f"/api/oltinfo/{oltid}"

    olt_info = get_api(URL, oltshub_tokens[str(user_id)])

    result += f'''
<b>ID:</b> {olt_info['id']}
<b>Hostname:</b> {olt_info['hostname']}
<b>IP Address:</b> {olt_info['ip_address']}
<b>Описание:</b> {olt_info['descr']}
'''

    await event.message.answer(text=result, format=TextFormat.HTML )
    btns = {}
    count = 0
    for p in olt_info['ports']:
        count += 1
        btns.update({p.replace('EPON', 'E').replace('GPON', 'G'): f'portstatus_{oltid}_{p}'})
        if count == 16:
            await event.message.answer(
                    text='<b>Порты:</b>',
                    attachments=[get_callback_btns(btns=btns, sizes=(int(BUTTON_COL), )).as_markup()],
                    format=TextFormat.HTML            
                )
            count = 0
            btns = {}

    if len(btns) > 0:
        await event.message.answer(
            text='<b>Порты:</b>',
            attachments=[get_callback_btns(btns=btns, sizes=(int(BUTTON_COL), )).as_markup()],
            format=TextFormat.HTML
        )


@olts_router.message_created(Command('ports_list'))
@user_required
async def ports_list(msg: MessageCreated) -> None:
    '''
    Команда просмотра портов
    '''
    result = ''
    user_id = msg.from_user.user_id
    oltid = msg.message.body.text.split()[-1]
    URL = f"/api/oltinfo/{oltid}"

    olt_info = get_api(URL, oltshub_tokens[str(user_id)])

    result += f'''
<b>ID:</b> {olt_info['id']}
<b>Hostname:</b> {olt_info['hostname']}
<b>IP Address:</b> {olt_info['ip_address']}
<b>Описание:</b> {olt_info['descr']}
'''

    await msg.message.answer(text=result, format=TextFormat.HTML )
    btns = {}
    count = 0
    for p in olt_info['ports']:
        count += 1
        btns.update({p.replace('EPON', 'E').replace('GPON', 'G'): f'portstatus_{oltid}_{p}'})
        if count == 16:
            await msg.message.answer(
                    text='<b>Порты:</b>',
                    attachments=[
                        get_callback_btns(
                            btns=btns, 
                            sizes=(int(BUTTON_COL), )
                        ).as_markup()
                    ],
                    format=TextFormat.HTML            
                )
            count = 0
            btns = {}

    if len(btns) > 0:
        await msg.message.answer(
            text='<b>Порты:</b>',
            attachments=[
                get_callback_btns(
                    btns=btns, 
                    sizes=(int(BUTTON_COL), )
                ).as_markup()
            ],
            format=TextFormat.HTML
        )


@olts_router.message_callback(F.callback.payload.startswith("update_"))
async def callback_olt_update(event: MessageCallback) -> None:
    '''
    Callback опроса олта
    '''
    result = ''
    user_id = event.from_user.user_id
    oltid = event.callback.payload.split('_')[-1]

    URL = f"/api/olts/oltupdate/{oltid}"

    await event.message.answer(warning_msg)

    result = get_api(URL, oltshub_tokens[str(user_id)])
    log_write(f'User: {user_id}; Action: OLT_UPDATE; Message: {result["message"]} (olt id: {oltid})')
    
    await event.message.answer(result['message'])


@olts_router.message_created(Command('olt_update'))
@user_required
async def olt_update(msg: MessageCreated) -> None:
    '''
    Команда опроса ОЛТа
    '''
    result = ''
    user_id = msg.from_user.user_id
    oltid = msg.message.body.text.split()[-1]

    URL = f"/api/olts/oltupdate/{oltid}"

    await msg.message.answer(warning_msg)

    result = get_api(URL, oltshub_tokens[str(user_id)])
    log_write(f'User: {user_id}; Action: OLT_UPDATE; Message: {result["message"]} (olt id: {oltid})')
    
    await msg.message.answer(result['message'])


@olts_router.message_callback(F.callback.payload.startswith("portstatus_"))
async def callback_port_status(event: MessageCallback) -> None:
    '''
    Callback просмотра статуса pon порта
    '''
    try:
        user_id = event.from_user.user_id
        oltid = event.callback.payload.split('_')[1]
        port = event.callback.payload.split('_')[2].replace('/', '.')

        await event.message.answer(warning_msg)

        port_info = get_port_status(oltid, port, oltshub_tokens[str(user_id)])

        if len(port_info) == 0:
                await event.message.answer('На порту нет ОНУ.')
        else:    
            for p in port_info:
                await event.message.answer(p, format=TextFormat.HTML)

    except:
        await event.message.answer('Ошибка выполнения команды!')


@olts_router.message_created(Command('port_status'))
@user_required
async def port_status(msg: MessageCreated) -> None:
    '''
    Команда просмотра статуса pon порта
    '''
    try:
        user_id = msg.from_user.user_id
        oltid = msg.message.body.text.split()[1]
        port = msg.message.body.text.split()[2].replace('/', '.')

        await msg.message.answer(warning_msg)

        port_info = get_port_status(oltid, port, oltshub_tokens[str(user_id)])

        if len(port_info) == 0:
                await msg.message.answer('На порту нет ОНУ.')
        else:    
            for p in port_info:
                await msg.message.answer(p, format=TextFormat.HTML)

    except:
        await msg.message.answer('Ошибка выполнения команды!')