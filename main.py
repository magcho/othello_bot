import sys
import json
import time
import requests
import logging
from bs4 import BeautifulSoup

# Othello-lib
#import Play

# Logging level
format = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=format)
logging.getLogger("requests").setLevel(logging.WARNING)

# Credential
# E_MAIL = "example@example.com"
# PASSWORD = "example1234"
E_MAIL = ""
PASSWORD = ""

# API Endpoint
HOME_URL = "http://tdu-othello.xyz/home"
LOGIN_URL = "http://tdu-othello.xyz/login"
ROOM_CREATE_URL = "http://tdu-othello.xyz/create"
LOGOUT_URL = "http://tdu-othello.xyz/logout"


def get_cookie_and_token(url, headers=False, cookies=False):
    response = requests.get(url, headers=headers, cookies=cookies)
    bs = BeautifulSoup(response.text, "html.parser")
    csrf_token = bs.find("meta", attrs={"name":"csrf-token", "content":True})
    return {
        "csrf-token":csrf_token["content"], 
        "csrf-header":response.cookies["XSRF-TOKEN"], 
        "session":response.cookies["othelloarena_session"]
    }


def do_login():
    logging.info("[*] Logging in...")
    cookie_token = get_cookie_and_token(LOGIN_URL)
    csrf_token = cookie_token["csrf-token"]
    csrf_header = cookie_token["csrf-header"]
    session = cookie_token["session"]

    cookies = {
        "XSRF-TOKEN":csrf_header, 
        "othelloarena_session":session
    }

    headers = {
        "User-Agent":"Mozilla/5.0",
        "Host":"tdu-othello.xyz",
        "Connection":"keep-alives",
        "Origin":"http://tdu-othello.xyz"
    }

    payload = {
        "_token":csrf_token, 
        "email":E_MAIL, 
        "password":PASSWORD
        
    }
    response = requests.post(LOGIN_URL, headers=headers, cookies=cookies ,data=payload, allow_redirects=False)
    if(response.status_code == requests.codes.found):
        logging.info("[*] Successfully logged in! code: {}".format(response.status_code))
    else:
        logging.critical("[*] Failed to login...")
        sys.exit(-1)

    return {
        "headers":{
            "User-Agent":"Mozilla/5.0",
            "Host":"tdu-othello.xyz",
            "Connection":"keep-alives",
            "Origin":"http://tdu-othello.xyz"
        },
        "cookies":{
            "XSRF-TOKEN":response.cookies["XSRF-TOKEN"], 
            "othelloarena_session":response.cookies["othelloarena_session"]
        }
    }


def make_room(auth_info):
    logging.info("[*] Creating room...")
    tokens = get_cookie_and_token(ROOM_CREATE_URL, auth_info["headers"], auth_info["cookies"])
    payload = {
        "_token":tokens["csrf-token"], 
        "name":"OTHELLO_BOY", 
        "size":"8",
        "play_with_mine":"0", 
        "alpha":"0", 
        "is_history":"1", 
        "create":""
    }
    response = requests.post(ROOM_CREATE_URL, headers=auth_info["headers"], cookies=auth_info["cookies"], data=payload)
    auth_info["cookies"]["XSRF-TOKEN"] = response.cookies["XSRF-TOKEN"]
    auth_info["cookies"]["othelloarena_session"] = response.cookies["othelloarena_session"]

    if(response.status_code == requests.codes.ok):
        logging.info("[*] Successfully created room! code: {}".format(response.status_code))
    else:
        logging.info("[!] You have already created room! code: {}".format(response.status_code))
        destroy_room(auth_info)


def destroy_room(auth_info):
    logging.info("[*] Destroying room...")
    response = requests.get(ROOM_CREATE_URL, headers=auth_info["headers"], cookies=auth_info["cookies"], allow_redirects=False)
    destroy_room = "{}{}".format(response.headers["Location"],"/destroy")
    response = requests.get(destroy_room, headers=auth_info["headers"], cookies=auth_info["cookies"], allow_redirects=False)

    if(response.status_code == requests.codes.found):
        logging.info("[*] Successfully destroyed room! code: {}".format(response.status_code))
        make_room(auth_info)
    else:
        logging.critical("[!] Unknown err...")
        sys.exit(-1)


def do_logout(auth_info):
    logging.info("[*] Logging out...")
    csrf_token = get_cookie_and_token(HOME_URL, auth_info["headers"], auth_info["cookies"])["csrf-token"]
    payload = {"_token":csrf_token}
    response = requests.post(LOGOUT_URL, headers=auth_info["headers"], cookies=auth_info["cookies"], data=payload)

    if(response.status_code == requests.codes.ok):
        logging.info("[*] Successfully logged out! code: {}".format(response.status_code))
    else:
        logging.critical("[!] Unknown err...")
        sys.exit(-1)



def load_own_AI():
    pass


def main():
    #while(True): # It's f**kin buggy!!!
    auth_info = do_login()
    make_room(auth_info)
    time.sleep(1) # Why are you in such a hurry?
    try:
        import Play
    except:
        logging.info("[!] GAME OVER!")

    do_logout(auth_info)


if __name__ == "__main__":
    print("===== OTHELLO_BOT =====")
    main()
