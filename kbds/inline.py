from maxapi.types.attachments.buttons.callback_button import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def get_callback_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (4, )
    ):
    '''
    Функция генерации кнопок
    '''
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.row(CallbackButton(text=text, payload=data))
    
    return keyboard.adjust(*sizes)