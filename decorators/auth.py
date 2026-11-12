from functools import wraps
from maxapi.types import MessageCreated
from maxapi.enums import TextFormat

from services.logger import log_write
from services.backend_api_connect import post_api_auth
from variables.users import oltshub_tokens


def user_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        event = next(
            (arg for arg in args if isinstance(arg, MessageCreated)),
            None
        )

        if event is None:
            event = next(
                (
                    value
                    for value in kwargs.values()
                    if isinstance(value, MessageCreated)
                ),
                None
            )

        if event is None:
            raise ValueError(
                "Декоратор user_required можно использовать "
                "только с обработчиками maxapi, принимающими MessageCreated"
            )
        
        user_id = event.message.sender.user_id
        user_name = event.message.sender.username
        first_name = event.message.sender.first_name
        last_name = event.message.sender.last_name
        # Проверяем доступ
        if user_id is None or str(user_id) not in oltshub_tokens:
            await event.message.answer(
                f"У вас нет доступа к этой команде. ❌\n"
                f"Войдите с помощью команды "
                f"<code>/login ВАШ_ЛОГИН</code>\n"
                f"Ваш ID: <code>{user_id if user_id is not None else 'неизвестен'}</code>",
                format=TextFormat.HTML
            )
            log_write(f'User: {user_id} ({first_name} {last_name} {user_name}); Action: AUTH; Message: Нет доступа. Text: {event.message.body.text}')
            return

        # Доступ разрешён
        return await f(*args, **kwargs)

    return decorated


def auth(login, max_id):
    '''
    Функция получения токена из OLTsHUB
    '''
    result = post_api_auth('/api/max/auth', {'login': login, 'max_id': max_id})
    return result