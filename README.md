# Telegram Template Sender

[Русская версия](README.ru.md)

A small command-line tool built on [Telethon](https://github.com/LonamiWebs/Telethon). It lets you save message templates and send them to chats you choose (private chats, groups, channels) with a delay between rounds. It runs from your own Telegram account, not through a bot token.

## Features

- Create and store message templates (multi-line, saved in `templates.json`)
- Several messages per template: they are sent in rotation
- Chats are shown in three columns (private / groups / channels) and picked by short codes like `u0,g1,c2`
- Configurable delay and number of rounds
- Timestamped log with success/error per chat
- API keys come from environment variables, nothing is hardcoded

## Installation

```bash
git clone https://github.com/<your-user>/telegram-template-sender.git
cd telegram-template-sender
pip install -r requirements.txt
```

Get your `api_id` and `api_hash` at [my.telegram.org](https://my.telegram.org) (API development tools).

## Usage

Set the keys, then run:

```powershell
# Windows (PowerShell)
$env:TG_API_ID="123456"; $env:TG_API_HASH="your_api_hash"
python sender.py
```

```bash
# Linux / macOS / Termux
export TG_API_ID=123456 TG_API_HASH=your_api_hash
python sender.py
```

On the first run Telethon asks for your phone number and the login code, then stores the session in `session.session`.

Then in the program:

1. Choose `1` to use a saved template or `2` to create a new one. For a new template, enter the message count and the text of each message; finish every message with `STOP` on its own line.
2. Pick chats from the table, for example `u0,g1,c0`.
3. Set the delay in seconds and the number of rounds.

Message `i` of the template is sent in round `i`, wrapping around if there are more rounds than messages.

## Important

- **Never publish `*.session` files.** They give full access to your Telegram account. Add `*.session`, `*.session-journal` and `templates.json` to `.gitignore`.
- Use it responsibly. Mass or repeated messaging can violate [Telegram's Terms of Service](https://telegram.org/tos) and lead to flood limits or account restrictions. Use sensible delays and only write to chats where it is welcome.

## Requirements

- Python 3.8+
- `telethon`, `wcwidth`

## License

MIT
