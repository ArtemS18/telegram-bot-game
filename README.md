Telegram-Bot для игры в Что? Где? Когда?

@Test_20053_bot

Логика работы:
- <img width="1754" height="1038" alt="изображение" src="https://github.com/user-attachments/assets/c357db35-5ca9-4e6f-8330-c53d3cb0db54" />
Управление:
- <img width="1885" height="946" alt="изображение" src="https://github.com/user-attachments/assets/2a619d9c-e55b-4a24-b5ac-41bd19e05ac1" />

Компоненты:
- Админака на FastApi
- Сервис для поллинга обновлений из telegram и отправки их в RabbitMq
- Сервис для получаения обновлений из RabbitMq, роутинга и всей логики работы бота.
- БД (PostgresSQL)



