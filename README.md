# link-notebook
Telegram bot to save a website as PDF

## Idea

1. telegram message containing a link
2. website will be parsed into kindle readable format
3. file in kindle readable format will be sent to Kindle

## Setup

* Create `.envrc` similar to `.envrc.example`
  * Needs SendGrid API key and Telegram bot token
* Run `python3 src/notebook-bot.py`
* In Telegram, contact your bot and follow the instructions

## Commands

* `/debug` - print debug information if `LINK_NOTEBOOK_DEBUG` environment variable is set
* `/help` - print instructions again
* `/setEmail <email>` - set recipient email to `<email>`
* `/note <url>` - convert website at `<url>` to PDF and send it to recipient email

## Status

- [x] basic functionality
- [x] replace sensitive strings with env vars
- [x] README
- [ ] email validation (everyone can send emails anywhere)
- [ ] more sources (Telegram message, Slack message, HTTP webhook, ...)
- [ ] more sinks (Email, Kindle account, Telegram, Slack, ...)
- [ ] host Python app
- [ ] research Kindle compatible format (or is PDF fine?)
