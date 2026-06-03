class InvalidDateError(Exception):

    def __init__(self, date, message="Добавлена дата - {} в неправильном формате '%Y-%m-%d'"):
        self.date = date
        self.message = message
        super().__init__(self.message.format(self.date))

    def __str__(self):
        return f'{self.message.format(self.date)}'


class HolidayLoadError(Exception):
    def __init__(self, path,
                 message="Ошибка чтения файла, проверьте корректность пути к файлу или его данные - {}"):
        self.message = message
        self.path = path

    def __str__(self):
        return f'{self.message.format(self.path)}'
