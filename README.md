# Email to Telegram
- Это мой телеграм-бот для чтения электронных сообщений внутри Телеграм

## Что он умеет
На данный момент список команд такой (данные в боте могут быть актуальнее):
- /start         : Это старт,
- /help          : Список команд,
- /me            : Данные пользователя,
- /check         : Проверить новые сообщения,
- /login         : Ввести данные,
- /logout        : Удалить данные,
- /go            : Начать уведомлять о новых сообщениях,
- /stop          : Остановить уведомления.

Список рабочих команд можно получить, отправив команду **_/help_**.
Для начала работы требуется "зарегистрироваться", введя свои данные
(почтовый сервер, адрес электронной почты и пароль для внешних приложений) после команды **_/login_**.
После команды **_/logout_** данные пользователя будут удалены. 
Команда **_/me_** позволяет увидеть все нужные данные текущего пользователя.

### Для проверки сообщений существуют две функции:
- check_mail
- check_mail_permanently

**_check_mail_**

При отправке команды **_/check_** функция проверит ваш электронный почтовый ящик и
отправит в чат Телеграм информацию о непрочитанных письмах. 
При этом все непрочитанные письма отмечаются прочитнными в почтовом ящике. 
Текст уведомления в Телеграм имеет следующий вид: 
- UID (уникальный ID сообщения)
- Имя отправителя
- Адрес отправителя
- Тема сообщения
- Текст

Если тело сообщения имеет вид HTML страницы, то в пункте **_Текст_** будет написано <HTML страничка>.

Под каждым сообщением будет кнопка, нажав на которую можно удалить сообщение из электронного ящика.

**_check_mail_permanently_**

При отправке команды **_/go_** функция будет проверять ваш электронный ящик раз в некоторое время
и отправлять в чат Телеграм информацию о непрочитанных письмах. 
При этом все непрочитанные письма остаются прочитнными в почтовом ящике. 
Текст уведомления в Телеграм имеет следующий вид: 
- UID (уникальный ID сообщения)
- Имя отправителя
- Адрес отправителя
- Тема сообщения

При следующей итерации выполнения функции сообщения, уведомления о которых уже были, не будут повторяться.

## Чему я научился
- Я понял, что такое декораторы
- Научился пользоваться генераторами
- Использовал блок try - except
- Познакомился с модулями schedule и threading

## Что нужно сделать
- Привязать БД для хранения данных о пользователях
- Проверить все случаи и комбинации команд (скорее всего где-то не отработает)
- Сделать правильную проверку вводимых пользователем данных
- Сделать рабочую возможность остановить регистрацию
- В **_/start_** добавить картинки с примерами (где взять пароль, как выглядят сообщения и т.д.)
- Возможно что-то сделать с HTML страничками, но не уверен
