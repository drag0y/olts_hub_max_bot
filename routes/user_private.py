from magic_filter import F
from maxapi.types.updates.message_created import MessageCreated
from maxapi.filters.command import Command, CommandStart
from maxapi.types import BotStarted
from maxapi import F
from maxapi.dispatcher import Router
from maxapi.enums import TextFormat

from decorators.auth import user_required, auth
from services.logger import log_write
from services.backend_api_connect import get_api
from services.level_color import level_color
from variables.users import oltshub_tokens
from variables.messages import start_message, help_message
from kbds.reply import start_kb


u_router = Router(router_id="u_router")


@u_router.bot_started()
async def on_start(cmd: BotStarted) -> None:
    '''
    Кнопка "Начать" при первом входе в бота
    '''
    await cmd.bot.send_message(
        chat_id=cmd.chat_id,
        text=start_message,
        format=TextFormat.HTML,
        attachments=[start_kb.as_markup()]
        )


@u_router.message_created(CommandStart())
async def on_cmd_start(cmd: MessageCreated) -> None:
    '''
    Команда /start
    '''
    await cmd.message.answer(
        text=start_message,
        format=TextFormat.HTML, 
        attachments=[start_kb.as_markup()]
    )


@u_router.message_created(
        (F.message.body.text.lower() == "/help") | 
        (F.message.body.text.lower() == "справка")
        )
async def cmd_help(cmd: MessageCreated):
    '''
    Команда /help
    '''
    await cmd.message.answer(
        help_message, 
        format=TextFormat.HTML
    )


@u_router.message_created(Command('login'))
async def user_login(cmd: MessageCreated):
    '''
    Команда /login
    '''
    try:
        user_input = cmd.message.body.text.split()
        user_id = cmd.message.sender.user_id
        
        result = auth(user_input[1], user_id)

        if result['result'] == 'error':
            log_write(f"User: {user_input[1]} ({user_id}); Action: AUTH; Message: {result['message']}")
            await cmd.message.answer(f"{result['message']}")
        else:
            oltshub_tokens.update({str(user_id): result['token']})
            log_write(f'User: {user_input[1]} ({user_id}); Action: AUTH; Message: Успешный вход в систему')
            await cmd.message.answer('Успешный вход в OLTsHUB ✅')

    except IndexError:
        await cmd.message.answer('Введите <code>/login ВАШ_ЛОГИН</code>', format=TextFormat.HTML)


@u_router.message_created()
@user_required
async def find_onu(msg):
    '''
    Поиск ОНУ
    '''
    user_input = msg.message.body.text.lower().replace(' ','') \
                                              .replace(':', '') \
                                              .replace('.', '') \
                                              .replace('hwtc', '48575443') \
                                              .replace('-', '')

    result = ''
    user_id = msg.message.sender.user_id

    if len(user_input) == 12 or len(user_input) == 16:
        URL = f"/api/onuinfo/{user_input}"
        req = get_api(URL, oltshub_tokens[str(user_id)])

        try:
            if isinstance(req, dict):
                if req['result'] == 'error':
                    await msg.message.answer(req['message'])
                else:
                    for r in req['onu']:
                        result += f'''
--- ONU Info 📊 ---
<b>ONU:</b> {r['mac/sn']}
<b>Descr:</b> {r['onudescr']}
<b>Статус:</b> {r['iface_state']} {'✅' if r['onu_state'] == 1 else '❌'}

<b>ОЛТ:</b> {r['oltname']}
<b>IP ОЛТа:</b> {r['oltip']}
<b>Порт:</b> {r['iface_name']}<b> ID:</b> {r['onuid']}

<b>ONU RX:</b> {r['level_onu_rx']} {level_color(r['level_onu_rx'])}
<b>OLT RX:</b> {r['level_olt_rx']} {level_color(r['level_olt_rx'])}

<b>Статус LAN порта:</b>
{"\n".join(f"Port: {x['port']} State: {x['status']}" for x in r['lanstate'])}

<b>MAC адреса:</b>
{"\n".join(str(x) for x in r['lan_mac'])}

<b>Uptime/Время включения:</b>
{r['uptime']}

<b>Время последнего выключения:</b>
{r['downtime']}
<b>Причина последнего выключения:</b>
{r['reason_offline']}

<b>Статус CATV порта:</b>
{r['catvstate']}
<b>Уровень сигнала CATV:</b>
{r['catvlevel']}
'''

                    await msg.message.answer(result, format=TextFormat.HTML)

        except KeyError:
            await msg.message.answer(f"У вас нет доступа или ваш токен просрочен. ❌\nВойдите с помощью команды /login ВАШ ЛОГИН")

    else:
        await msg.message.answer("Неправильный Мак или Серийник ONU!")