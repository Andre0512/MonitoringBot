# MonitoringBot

#### Just a Telegram Bot for monitoring a few processes on my servers

## Features
* Monitoring state of python processes on various Linux systems
* Monitoring availability of devices with pings
* Monitoring state of [FHEM](https://fhem.de/) instances 
* Detecting all states fast with asynchronous running
* Reading all device data from config.yml
* Ensures that the bot runs permanently

## Installation
* Clone this Repository
* Join the project directory `cd MonitoringBot/`
* Install requierd pip packages `pip3 install requirements.txt`
* Editing _config.yml_ and add your personal data:  
```cp config.yml.default config.yml ; nano config.yml```
     * You can get a token from the Telegram [BotFather](https://t.me/BotFather)
     * Replace the placeholder with your data
* Running the MonitoringBot `python3 MonitoringBot.py`
* Install crontab for checking the bot running state every minute:  
```(cat /etc/crontab && echo "* * * * * $USER bash $PWD/startup.sh &") | sudo tee /etc/crontab```

## License
This project is under the MIT license.
If you can do anything with the project, have fun ;)
