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
1. Clone this Repository  
```git clone git@github.com:Andre0512/MonitoringBot.git && cd MonitoringBot/```
2. Create virtual environment (optional)  
```python3 -m venv venv && soure ./venv/bin/activate```
3. Install requierd pip packages  
```pip install -r requirements.txt```
4. Editing _config.yml_ and add your personal data:  
```cp config.yml.default config.yml ; nano config.yml```
     * You can get a token from the Telegram [BotFather](https://t.me/BotFather)
     * Replace the placeholder with your data
5. Running the MonitoringBot `./MonitoringBot.py`
6. Install crontab for checking the bot running state every minute:  
```(cat /etc/crontab && echo "* * * * * $USER bash $PWD/startup.sh &") | sudo tee /etc/crontab```

## License
This project is under the MIT license.
If you can do anything with the project, have fun ;)
