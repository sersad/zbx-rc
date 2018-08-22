# !!! Attention !!!
For now it's just pre-alpha version, so cannot be used.

# zbx-rc
Utility to send message from Zabbix into Rocket.Chat.
![alt](https://pp.userapi.com/c847120/v847120545/ca50d/BhNh_-7pRL4.jpg)
Zabbix Share page: None  
You can contact me with Telegram: @asand3r

Program wrote with Python 3.6.

**Latest stable versions:** None

## Dependencies
 - requests

## Feautres  
**Common:**
- [x] Send simple text message
## TODO  
- [ ] HTTPS support
- [ ] Attach images to message
- [ ] Generate AUTH section in config file

## Supported arguments  
Positional:  
0: **to**  
Recipient  
1: **subject**  
Subject for message  
2: **message**  
Message text  

Named:  
**-h|--help**  
Print help message  
**-v|--version**  
Print version number  
**-c|--config**  
Path to config file  
**--debug**  
Turn on debug output to console  
**--get-token**  
Get authentication token and user ID from Rocket.Chat API  
**-u|--username**  
Rocket.Chat username  
**-p|--password**  
Rocket.Chat password  

## Usage examples
```bash
[root@server ~]# ./zbx-rc.py '@asand3r' 'PROBLEM: Free space is low (5%)' 'Free space on disk C:\ too low - 5%'
```
