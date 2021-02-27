import logging
import json
import os
import string
from configparser import ConfigParser
from random import choice

import requests

logging.basicConfig(level=logging.ERROR)


class ZabbixWeb:
    def __init__(self, server, username, password):
        self.debug = False
        self.server = server
        self.username = username
        self.password = password
        self.proxies = {}
        self.verify = True
        self.cookie = None
        self.basic_auth_user = None
        self.basic_auth_pass = None
        self.tmp_dir = None

    def login(self):
        if not self.verify:
            requests.packages.urllib3.disable_warnings()

        data_api = {"name": self.username, "password": self.password, "enter": "Sign in"}
        answer = requests.post(self.server + "/", data=data_api, proxies=self.proxies, verify=self.verify,
                               auth=requests.auth.HTTPBasicAuth(self.basic_auth_user, self.basic_auth_pass))
        cookie = answer.cookies
        if len(answer.history) > 1 and answer.history[0].status_code == 302:
            logging.warning("probably the server in your config file has not full URL (for example "
                          "'{0}' instead of '{1}')".format(self.server, self.server + "/zabbix"))
        if not cookie:
            logging.error("authorization has failed, url: {0}".format(self.server + "/"))
            cookie = None

        self.cookie = cookie

    def graph_get(self, itemid, period, title, width, height, version=3):
        file_img = "{0}/{1}.png".format(self.tmp_dir, "".join(choice(string.ascii_letters) for _ in range(10)))

        title = requests.utils.quote(title)

        colors = {
            0: "00CC00",
            1: "CC0000",
            2: "0000CC",
            3: "CCCC00",
            4: "00CCCC",
            5: "CC00CC",
        }

        drawtype = 5
        if len(itemid) > 1:
            drawtype = 2

        zbx_img_url_itemids = []
        for i in range(0, len(itemid)):
            itemid_url = "&items[{0}][itemid]={1}&items[{0}][sortorder]={0}&" \
                         "items[{0}][drawtype]={3}&items[{0}][color]={2}".format(i, itemid[i], colors[i], drawtype)
            zbx_img_url_itemids.append(itemid_url)

        zbx_img_url = self.server + "/chart3.php?"
        if version < 4:
            zbx_img_url += "period={0}".format(period)
        else:
            zbx_img_url += "from=now-{0}&to=now".format(period)
        zbx_img_url += "&name={0}&width={1}&height={2}&graphtype=0&legend=1".format(title, width, height)
        zbx_img_url += "".join(zbx_img_url_itemids)

        logging.info(zbx_img_url)

        answer = requests.get(zbx_img_url, cookies=self.cookie, proxies=self.proxies, verify=self.verify,
                              auth=requests.auth.HTTPBasicAuth(self.basic_auth_user, self.basic_auth_pass))
        status_code = answer.status_code
        if status_code == 404:
            logging.error("can't get image from '{0}'".format(zbx_img_url))
            return False
        res_img = answer.content

        with open(file_img, "wb") as fd:
            fd.write(res_img)
        return file_img

    def api_test(self):
        headers = {'Content-type': 'application/json'}
        api_data = json.dumps({"jsonrpc": "2.0", "method": "user.login", "params":
                              {"user": self.username, "password": self.password}, "id": 1})
        api_url = self.server + "/api_jsonrpc.php"
        api = requests.post(api_url, data=api_data, proxies=self.proxies, headers=headers)
        return api.text


def graph_get(itemid: list,
              title: str,
              zbx_server: str,
              zbx_api_user: str,
              zbx_api_pass: str,
              zbx_tmp_dir: str) -> str:

    image_period = "14400"
    image_width = "900"
    image_height = "200"
    zbx = ZabbixWeb(server=zbx_server, username=zbx_api_user, password=zbx_api_pass)
    zbx.login()
    if not zbx.cookie:
        logging.error("Login to Zabbix web UI has failed (web url, user or password are incorrect) unable to send graphs check manually")
    zbx.tmp_dir = zbx_tmp_dir
    file_img = zbx.graph_get(itemid, image_period, title, image_width, image_height)
    return file_img


def main():
    """
    для теста
    :return:
    """

    itemid = ["9444883"]
    image_period = "14400"
    title = "test title"
    image_width = "900"
    image_height = "200"

    base_path = os.path.dirname(os.path.abspath("zbx-rc"))
    config_path = os.path.join(base_path, "zbx-rc.conf")
    cfg = ConfigParser()
    cfg.read(config_path)
    zbx_server = cfg.get("ZABBIX", "zbx_server")
    zbx_api_user = cfg.get("ZABBIX", "zbx_api_user")
    zbx_api_pass = cfg.get("ZABBIX", "zbx_api_pass")
    zbx_tmp_dir = cfg.get("ZABBIX", "zbx_tmp_dir")

    zbx = ZabbixWeb(server=zbx_server, username=zbx_api_user, password=zbx_api_pass)

    zbx.login()
    if not zbx.cookie:
        logging.error("Login to Zabbix web UI has failed (web url, user or password are incorrect) unable to send graphs check manually")

    zbx.tmp_dir = zbx_tmp_dir

    print(zbx.api_test())

    file_img = zbx.graph_get(itemid, image_period, title, image_width, image_height)

    print(file_img)


if __name__ == '__main__':
    """запускается только для теста"""
    main()
