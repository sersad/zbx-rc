# zbx-rc
Utility to send message from Zabbix into Rocket.Chat.
![alt](http://gogs.mts-nn.ru/s.sadovnikov/zbx-rc-bot/raw/68e2e678f40be1ba9c35fdbf967795884fbe32d5/001.png)

![alt](http://gogs.mts-nn.ru/s.sadovnikov/zbx-rc-bot/raw/68e2e678f40be1ba9c35fdbf967795884fbe32d5/002.png)



Program run with Python > 3.4

**Latest stable versions:** 0.2

Original code: 
https://github.com/asand3r/zbx-rc/wiki/Configure-media-type-in-Zabbix

https://share.zabbix.com/cat-notifications/zabbix-to-rocket-chat 


How to add alert script in Zabbix: https://www.zabbix.com/documentation/3.4/manual/config/notifications/media/script


## How to install zbx-rc:  

### Dependencies
 - requests

### Feautres  
**Common:**
- [x] Send simple text message
- [x] HTTPS support
- [x] Update config file in place
- [x] Update message if problem resolved (id message get by triggerid/eventid)  

### TODO  
- [ ] Attach images to message
- [ ] Clear old messages 

### Supported arguments  
#### Please, read help message first, it always actual.
#### Common:  
**-h|--help**  
Print help message  
**-v|--version**  
Print version number  
**-c|--config**  
Path to config file (default: zbx-rc.conf near executable file)  
**--debug**  
Turn on debug output to console

#### Positional:  
**install**  
Prepate environment. Create config directory and config example.
>**-c|--conf-dir**  
>Path to conig directory (Default: /etc/zbx-rc)  
>**-g|--group**  
>System group, who will be own config directory (Default: zabbix)

**auth**  
Authenticate to Rocket.Chat  
>**-u|--username**  
>Rocket.Chat username  
>**-p|--password**  
>Rocket.Chat password

**send**  
Send message to Rocket.Chat  
>**to**          Recipient  
>**subject**     Subject  
>**message**     Text body  

### Usage examples
Install script to your system. In fact, it's just creates config directory with config example:
```bash
[root@server ~]# ./zbx-rc.py install
INFO: Script installed successfully. Please, correct /etc/zbx-rc/zbx-rc.conf file for your environment.
[root@server ~]# cat ./zbx-rc/zbx-rc.conf
[RCHAT]
protocol = https
server = rocketchat.mts-nn.ru
port = 443
uid = 
token = 
```

At startup, it will check if there is a database along the path 
```bash
/opt/zbx-rc/
```
and if not, it will be created. 
If an error occurs with rights, run the script with root rights. 
If it fails, create a directory '/opt/zbx-rc/' and give write permissions to the user/group the zabbix. 

Authenticate to Rocket.Chat with REST API:
```bash
[root@server ~]# ./zbx-rc.py auth -u 'asand3r' -p 'secretPa$$word'
id:     '1234567890'
token:  'c68019f8c6e613180ac296d5870e9cdb4b46f29c'
```
You can provide '--update' parameter to update your config file with received values:
```bash
[root@server ~]# ./zbx-rc.py auth -u 'asand3r' -p 'secretPa$$word' --update
```
Use 'send' parameter to send simple text message:
```bash
[root@server ~]# ./zbx-rc.py send '@asand3r' 'PROBLEM: Free space is low (5%)' 'Free space on disk C:\ too low - 5%'
```

When using the URL https://<zabbix/tr_events.php?triggerid=3349067&eventid=4026100586, the message id with triggerid eventid will be saved in the sqlite database. If a message is received with the same triggerid eventid it will be updated.