# aiogram-youbot

## Deployment
Use following commands to deploy bot on Linux/Mac OS X system:
```bash
$ cd /usr/projects
$ git clone https://github.com/hazadus/aiogram-youbot
$ virtualenv aiogram-youbot
$ cd ./aiogram-youbot
$ source bin/activate
$ pip install -r requirements.txt
```


## Running
### Server Mode
```bash
$ touch ./run_bot.sh
$ chmod a+x ./run_bot.sh
$ nano ./run_bot.sh
```
Edit `run_bot.sh`:
```bash
#!/bin/bash

# Set these env vars according to yours
# Your bot's token:
export BOT_TOKEN=TelegramBotToken
# Your telegram ID:
export BOT_ADMIN=BotAdminChatID
export BOT_LOG_FILENAME=aiogram_youbot.log

cd /usr/projects/aiogram-youbot
source bin/activate
nohup python ./aiogram-youbot &
# or with pm2:
# pm2 start ./aiogram-youbot.py --interpreter=python3 --restart-delay 6000
```
Then `chmod a+x ./run_bot.sh`.
To start the bot in production mode:
```bash
$ ./run_bot.sh
```

## References
- [How To Use subprocess to Run External Programs in Python 3](https://www.digitalocean.com/community/tutorials/how-to-use-subprocess-to-run-external-programs-in-python-3)