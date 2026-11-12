from telethon import TelegramClient
import asyncio
from datetime import datetime
import json
import os
from wcwidth import wcswidth

# Ключи берутся из переменных окружения (получить: https://my.telegram.org)
#   Windows (PowerShell): $env:TG_API_ID="123456"; $env:TG_API_HASH="abcdef..."
#   Linux/Termux:         export TG_API_ID=123456 TG_API_HASH=abcdef...
try:
    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]
except (KeyError, ValueError):
    raise SystemExit("Задай переменные окружения TG_API_ID и TG_API_HASH (см. комментарий в начале файла)")

client = TelegramClient("session", api_id, api_hash)

TEMPLATES_FILE = "templates.json"
COL_WIDTH = 35


def now():
    return datetime.now().strftime("%H:%M:%S")


def load_templates():
    if not os.path.exists(TEMPLATES_FILE):
        return {}
    with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_templates(data):
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def input_multiline():
    print("Введи текст (STOP на новой строке):")
    lines = []
    while True:
        line = input()
        if line == "STOP":
            break
        lines.append(line)
    return "\n".join(lines)


def format_text(text, width=COL_WIDTH):
    # Считаем реальную ширину текста в терминале (эмодзи = 2, кириллица = 1)
    vis_width = wcswidth(text)
    if vis_width < 0:
        vis_width = len(text)  # fallback

    if vis_width > width:
        # Обрезаем по визуальной ширине
        result = ""
        cur = 0
        for ch in text:
            cw = wcswidth(ch)
            if cw < 0:
                cw = 1
            if cur + cw > width - 3:
                break
            result += ch
            cur += cw
        return result + "..." + " " * max(0, width - cur - 3)
    else:
        return text + " " * (width - vis_width)


async def main():
    await client.start()

    templates = load_templates()

    print("1 - использовать шаблон")
    print("2 - создать шаблон")
    mode = input("Выбор: ")

    if mode == "1" and templates:
        print("\nШаблоны:")
        for name in templates:
            print(f"- {name}")

        name = input("Название шаблона: ")

        if name not in templates:
            print("Нет такого шаблона")
            return

        messages = templates[name]

    else:
        name = input("Название нового шаблона: ")
        msg_count = int(input("Сколько сообщений: "))

        messages = []
        for i in range(msg_count):
            print(f"\nСообщение {i+1}:")
            messages.append(input_multiline())

        templates[name] = messages
        save_templates(templates)
        print("Шаблон сохранён\n")

    print(f"\n[{now()}] Загрузка чатов...\n")

    users, groups, channels = [], [], []

    async for dialog in client.iter_dialogs():
        if dialog.is_user:
            users.append(dialog)
        elif dialog.is_group:
            groups.append(dialog)
        elif dialog.is_channel:
            channels.append(dialog)

    max_len = max(len(users), len(groups), len(channels))

    header = format_text("ЛС") + "|" + format_text("ГРУППЫ") + "|" + format_text("КАНАЛЫ")
    separator = "-" * COL_WIDTH + "+" + "-" * COL_WIDTH + "+" + "-" * COL_WIDTH

    print(header)
    print(separator)

    for i in range(max_len):
        u = f"u{i} {users[i].name}"    if i < len(users)    else ""
        g = f"g{i} {groups[i].name}"   if i < len(groups)   else ""
        c = f"c{i} {channels[i].name}" if i < len(channels) else ""

        print(format_text(u) + "|" + format_text(g) + "|" + format_text(c))

    choice = input("\nВыбор (пример u0,g1,c0): ").split(",")

    selected = []

    for item in choice:
        item = item.strip()
        try:
            if item.startswith("u"):
                selected.append(users[int(item[1:])])
            elif item.startswith("g"):
                selected.append(groups[int(item[1:])])
            elif item.startswith("c"):
                selected.append(channels[int(item[1:])])
        except:
            print(f"Ошибка: {item}")

    delay = int(input("Задержка (сек): "))
    count = int(input("Сколько раз отправить: "))

    print(f"\n[{now()}] Старт...\n")

    for i in range(count):
        msg = messages[i % len(messages)]

        for dialog in selected:
            try:
                await client.send_message(dialog.entity, msg)
                print(f"[{now()}] ✔ {dialog.name}")
            except Exception as e:
                print(f"[{now()}] ❌ {dialog.name}: {e}")

        await asyncio.sleep(delay)

    print(f"\n[{now()}] Готово")


with client:
    client.loop.run_until_complete(main())