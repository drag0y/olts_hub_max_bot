from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types.attachments.buttons import MessageButton

start_kb = InlineKeyboardBuilder()

start_kb.add(
    MessageButton(text='Справка'),
    MessageButton(text='Список ОЛТов')
)

start_kb.adjust(2)