import logging
from datetime import datetime, date
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dateutil import parser
from pathlib import Path
import json

from holiday_bot.holiday.custom_holiday import MyHolidays

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)


class RussianHolidaysBot(MyHolidays):
    def __init__(self, token: str, **kwargs):
        super().__init__(**kwargs)
        self.token = token

    def _get_my_holidays(self) -> MyHolidays:
        """Получение объекта праздников для пользователя"""
        return MyHolidays().custom_holidays

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        welcome_text = (
            f"Привет, {user.first_name}! 👋\n\n"
            "Я бот, который рассказывает о праздниках России! 🇷🇺\n\n"
            "Что я умею:\n"
            "• Показывать праздники на сегодня\n"
            "• Показывать праздники на любую дату\n"
            "• Искать праздники по месяцу\n"
            "• Добавлять свои праздники (дни рождения) 🎂\n\n"
            "Используйте команды или кнопки меню 👇"
        )

        keyboard = [
            [KeyboardButton("🎉 Сегодня"), KeyboardButton("📅 Выбрать дату")],
            [KeyboardButton("📆 Весь месяц"), KeyboardButton("➕ Добавить праздник")],
            [KeyboardButton("📋 Мои праздники"), KeyboardButton("❓ Помощь")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📋 Доступные команды:\n\n"
            "/start - начать работу с ботом\n"
            "/today - праздники сегодня\n"
            "/date [дата] - праздники на конкретную дату\n"
            "   Пример: /date 2025.12.31\n"
            "/month [месяц] - все праздники месяца\n"
            "   Пример: /month январь или /month 1\n"
            "/add_holiday - добавить свой праздник\n"
            "/my_holidays - показать мои праздники\n"
            "/delete_holiday - удалить праздник\n\n"
            "/closest - ближайший официальный праздник"
            "Или используйте кнопки ниже 👇"
        )
        await update.message.reply_text(help_text)

    async def today_holidays(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Праздники на сегодня"""
        today = date.today()
        await self._send_holidays_for_date(update, today, "сегодня")

    async def get_closest_official_holiday(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ближайший официальный праздник"""
        try:
            holidays_list = MyHolidays().get_closest_official_holiday()
            response = "📋 Ваши праздники:\n\n"
            for holidays in holidays_list:
                response += f"• {holidays}\n"
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"error: {e}")
            await update.message.reply_text("Произошла ошибка при получении праздников 😕")

    async def date_holidays(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Праздники на конкретную дату"""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите дату после команды.\n"
                "Пример: /date 31.12.2025 или /date 2025-12-31"
            )
            return

        try:
            date_str = ' '.join(context.args)
            target_date = parser.parse(date_str).date()
            await self._send_holidays_for_date(
                update, target_date, target_date.strftime("%Y-%m-%d")
            )
        except (ValueError, TypeError):
            await update.message.reply_text(
                "Неверный формат даты. Попробуйте:\n"
                "• 2025.12.31\n"
                "• 2025-12-31"
            )

    async def add_holiday_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление кастомного праздника"""
        if context.args and len(context.args) >= 2:
            # Пытаемся распарсить дату из аргументов
            try:
                date_str = context.args[0]
                name = ' '.join(context.args[1:])
                target_date = parser.parse(date_str, dayfirst=False).date()
                await self._add_custom_holiday(update, target_date, name)
            except (ValueError, TypeError):
                await update.message.reply_text(
                    "Неверный формат. Используйте:\n"
                    "/add_holiday ГГГГ.ММ.ДД Название праздника\n"
                    "Пример: /add_holiday 2024.03.15 День рождения мамы"
                )
        else:
            await update.message.reply_text(
                "📝 Чтобы добавить праздник, введите:\n"
                "/add_holiday ГГГГ.ММ.ДД Название праздника\n\n"
                "Пример:\n"
                "/add_holiday 1994-01-20 День рождения мамы\n"
                "/add_holiday 1984-05-20 День рождения папы"
            )

    async def my_holidays_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать все кастомные праздники пользователя"""
        try:
            holidays_list = self._get_my_holidays()

            if not holidays_list:
                await update.message.reply_text(
                    "У вас пока нет добавленных праздников.\n"
                    "Добавьте первый праздник с помощью команды /add_holiday"
                )
                return

            response = "📋 Ваши праздники:\n\n"
            for holiday_date, name in holidays_list.items():
                name = ", ".join(name)
                response += f"• {holiday_date.strftime('%Y.%m.%d')} - {name}\n"
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"error: {e}")
            await update.message.reply_text("Произошла ошибка при получении праздников 😕")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback-запросов"""
        query = update.callback_query
        await query.answer()

        if query.data.startswith('delete_'):
            parts = query.data.split('_')
            if len(parts) >= 4:
                holiday_date = parts[1]
                name = ' '.join(parts[2:]).replace('_', ' ')
                await self._delete_holiday(query, holiday_date, name)

    async def _add_custom_holiday(self, update: Update, holiday_date: date, name: str):
        """Добавление кастомного праздника в базу данных"""
        try:
            my_holiday = MyHolidays()
            holiday_at_the_day = my_holiday.get(holiday_date)
            if name in holiday_at_the_day:
                await update.message.reply_text(
                    f"❌ Праздник '{name}' на эту дату уже существует!"
                )
                return
            # Добавляем новый праздник
            try:
                custom_holidays_file = Path(__file__).parent / "holiday" / "custom_holiday.json"
                with open(custom_holidays_file, encoding="utf-8") as f:
                    custom_hols = json.load(f)
                    custom_hols[holiday_date.strftime('%Y-%m-%d')] = name
                with open(custom_holidays_file, "w", encoding="utf-8") as f:
                    json.dump(custom_hols, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"Get file error: {e}")
                return {}

            await update.message.reply_text(
                f"✅ Праздник добавлен!\n"
                f"📅 {holiday_date.strftime('%Y.%m.%d')} - {name}"
            )

        except Exception as e:
            logger.error(f"error: {e}")
            await update.message.reply_text("Произошла ошибка при добавлении праздника 😕")

    async def month_holidays(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Все праздники месяца"""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите месяц после команды.\n"
                "Пример: /month январь или /month 1"
            )
            return

        month_input = ' '.join(context.args).lower()
        month_dict = {
            '1': 1, 'январь': 1, 'января': 1,
            '2': 2, 'февраль': 2, 'февраля': 2,
            '3': 3, 'март': 3, 'марта': 3,
            '4': 4, 'апрель': 4, 'апреля': 4,
            '5': 5, 'май': 5, 'мая': 5,
            '6': 6, 'июнь': 6, 'июня': 6,
            '7': 7, 'июль': 7, 'июля': 7,
            '8': 8, 'август': 8, 'августа': 8,
            '9': 9, 'сентябрь': 9, 'сентября': 9,
            '10': 10, 'октябрь': 10, 'октября': 10,
            '11': 11, 'ноябрь': 11, 'ноября': 11,
            '12': 12, 'декабрь': 12, 'декабря': 12
        }

        if month_input not in month_dict:
            await update.message.reply_text(
                "Неверное название месяца. Используйте:\n"
                "• номер месяца (1-12)\n"
                "• название месяца (январь, февраль...)"
            )
            return

        month = month_dict[month_input]
        year = datetime.now().year

        month_holidays = []
        for day in range(1, 32):
            try:
                current_date = date(year, month, day)
                holidays_list = self.get(current_date)
                if holidays_list:
                    month_holidays.append((current_date, holidays_list))
            except ValueError:
                break

        if not month_holidays:
            await update.message.reply_text(
                f"В {month_input.capitalize()} нет праздников 🎯"
            )
            return

        response = f"🎊 Праздники {month_input.capitalize()} {year}:\n\n"
        for holiday_date, holiday_names in month_holidays:
            official, custom = self.get_list(holiday_date)

            if official:
                response += f"• {holiday_date.strftime('%m.%d')} - {official} 🇷🇺\n"
            if custom:
                response += f"• {holiday_date.strftime('%m.%d')} - {custom[0]} 🎂\n"

        await update.message.reply_text(response)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text.lower()

        if text in ['сегодня', '🎉 сегодня']:
            await self.today_holidays(update, context)
        elif text in ['выбрать дату', '📅 выбрать дату']:
            await update.message.reply_text(
                "Введите дату в формате ГГГГ.ММ.ДД\n"
                "Пример: 2025.12.31"
            )
        elif text in ['весь месяц', '📆 весь месяц']:
            await update.message.reply_text(
                "Введите месяц (например: '/month январь' или ' /month 1')"
            )
        elif text in ['добавить праздник', '➕ добавить праздник']:
            await self.add_holiday_command(update, context)
        elif text in ['мои праздники', '📋 мои праздники']:
            await self.my_holidays_command(update, context)
        elif text in ['помощь', '❓ помощь']:
            await self.help_command(update, context)
        else:
            # Попробуем распарсить дату из сообщения
            try:
                target_date = parser.parse(text, dayfirst=True).date()
                await self._send_holidays_for_date(
                    update, target_date, target_date.strftime("%Y.%m.%d")
                )
            except (ValueError, TypeError):
                await update.message.reply_text(
                    "Не понимаю ваше сообщение 😕\n"
                    "Используйте команды или кнопки меню. Для справки /help"
                )

    async def _send_holidays_for_date(self, update: Update, target_date: date,
                                      date_label: str):
        """Отправка праздников для указанной даты"""
        official_holidays, custom_holidays = self.get_list(target_date)

        if not official_holidays and not custom_holidays:
            response = f"На {date_label} нет праздников 🎯\n"
            response += "Но это отличный день, чтобы создать свой собственный праздник! 🎊"
            await update.message.reply_text(response)
            return

        response = f"🎉 Праздники {date_label}:\n\n"

        if official_holidays:
            response += "🇷🇺 Официальные праздники:\n"
            response += f"• {official_holidays}\n"
            response += "\n"

        if custom_holidays:
            response += "🎂 Ваши праздники:\n"
            for holiday in custom_holidays:
                response += f"• {holiday}\n"

        await update.message.reply_text(response)

    def run(self):
        """Запуск бота"""
        application = Application.builder().token(self.token).build()
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("today", self.today_holidays))
        application.add_handler(CommandHandler("date", self.date_holidays))
        application.add_handler(CommandHandler("month", self.month_holidays))
        application.add_handler(CommandHandler("add_holiday", self.add_holiday_command))
        application.add_handler(CommandHandler("my_holidays", self.my_holidays_command))
        application.add_handler(CommandHandler("closest", self.get_closest_official_holiday))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Запускаем бота
        print("Бот запущен...")
        application.run_polling()


def main():
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Пожалуйста, укажите токен вашего бота!")
        BOT_TOKEN = input("Токен вашего бота: ")

    bot = RussianHolidaysBot(BOT_TOKEN)
    bot.run()


if __name__ == "__main__":
    main()
