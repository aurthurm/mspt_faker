import json
import os
import requests
import random
import time
from tqdm import tqdm
from requests.auth import HTTPBasicAuth
import urllib3
from typing import List, Dict
import pandas as pd
from alive_progress import alive_bar
from datetime import datetime, timedelta

from config import *

from logger import Logger
logger = Logger(__name__, __file__)

session = requests.session()
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MSPT():
    session = session
    users = [
        {
            'first_name': f"Sniper {c}",
            'last_name': f"Sniper {c}",
            'email': f"sniper{c}@mspt.com",
            'password': "ceam2014",
        } for c in range(1, 11)
    ]

    def __init__(self):
        """"""

    def decode_response(self, response):
        return json.loads(response)
    
    def fetch(self, end_point, token=None):
        logger.log("info", f"Fetching from endpoint {end_point}")
        if not token:
            response = self.session.get(end_point)
        else:
            response = self.session.get(end_point, headers={"Authorization": f"Bearer {token}"})

        if response.status_code != 200:
            logger.log("info", f"Failed to fetch resource - status-code-{response.status_code} -- exiting")
            logger.log("info", f"Error response-text-{response.text}")
            logger.log("info", f"Error response-reason - status-code-{response.reason}")
        else:
            return self.decode_response(response.text)
    
    def send(self, end_point, data, token=None):
        logger.log("info", f"Sending Data to endpoint {end_point}")
        if not token:
            response = self.session.post(end_point, data=data)
        else:
            response = self.session.post(end_point, json=data, headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            logger.log("info", f"Failed to fetch resource - status-code-{response.status_code} -- exiting")
            logger.log("info", f"Error response-text-{response.text}")
            logger.log("info", f"Error response-reason - status-code-{response.reason}")
        else:
            return self.decode_response(response.text)

    def login(self, user):
        auth = self.send("http://localhost:8000/api/v1/login/access-token" ,data={'username': user['email'], 'password': user['password']})
        return auth['access_token'], auth['uid']

    def create_users(self):
        for user in self.users:
            user = self.send("http://localhost:8000/api/v1/users", data=user)
            logger.log("info", f"Created User: {user}")

    def create_user_instruments(self):
        instruments = [
            "eurusd", "eurjpy", "eurcad", "eurnzd", "eurgbp", "eurchf", 
            "gbpjpy", "gbpcad", "gbpnzd", "gbpchf",
            "usdcad", "usdchf", "usdjpy", "usdmxn", "usdtry",
            "nzdjpy", "nzdchf", "nzdjpy",
            "stpidx", "v75", "v100", "v50", "v100", "cr1000", "bm1000",
            "us100", "us30", "us500", "bund", "futsie", "gold", "oil",
        ]
        for user in self.users:
            choice = random.sample(instruments, random.randint(1, 10))
            token, uid = self.login(user)
            for inst in choice:
                _inst = self.send("http://localhost:8000/api/v1/mspt/instrument", data={'name': inst },  token=token)
                logger.log("info", f"{user['first_name']} Added Intrument: {_inst}")
                time.sleep(1)

    def create_user_strategies(self):
        for user in self.users:
            strategies = [{"name": f"Strategy {c}", "description": f"Strategy description {c} for {user['first_name']}", "public": random.choice([True, False]) } for c in range(random.randint(1, 20))]
            
            token, uid = self.login(user)
            for strat in strategies:
                _strat = self.send("http://localhost:8000/api/v1/mspt/strategy", data=strat,  token=token)
                logger.log("info", f"{user['first_name']} Added Strategy: {_strat}")
                time.sleep(1)


    def create_user_tplans(self):
        for user in self.users:
            t_plans = [{"name": f"Trading Plan {c}", "description": f"Trading plan description {c} for {user['first_name']}", "public": random.choice([True, False]) } for c in range(random.randint(1, 20))]
            
            token, uid = self.login(user)
            for plan in t_plans:
                _plan = self.send("http://localhost:8000/api/v1/mspt/trading-plan", data=plan,  token=token)
                logger.log("info", f"{user['first_name']} Added Trading Plan: {_plan}")
                time.sleep(1)

    def create_user_tasks(self):
        for user in self.users:
            tasks = [{"name": f"Task {c}", "description": f"Task description {c} for {user['first_name']}" } for c in range(random.randint(2, 50))]
            
            token, uid = self.login(user)
            for task in tasks:
                _task = self.send("http://localhost:8000/api/v1/mspt/task", data=task,  token=token)
                logger.log("info", f"{user['first_name']} Added Task: {_task}")
                time.sleep(1)

    def create_studies(self):
        for user in self.users:
            token, uid = self.login(user)
            insts = self.fetch("http://localhost:8000/api/v1/mspt/instrument/", token=token)
            styles = self.fetch("http://localhost:8000/api/v1/mspt/style/", token=token)

            studies = [{"name": f"Study {c}", "description": f"Study description {c} for {user['first_name']}", "public": random.choice([True, False])} for c in range(random.randint(2, 20))]
            for study in studies:
                _study = self.send("http://localhost:8000/api/v1/mspt/study", data=study,  token=token)
                if not _study:
                    continue
                logger.log("info", f"{user['first_name']} Added study: {_study}")

                attrs = [{"name": f"Attr {c}", "description": f"Attr description {c}", "study_uid": _study['uid']} for c in range(random.randint(1, 20))]
                created_atrs = []

                for attr in attrs:
                    _attr = self.send("http://localhost:8000/api/v1/mspt/attribute", data=attr,  token=token)
                    if not _attr:
                        continue
                    created_atrs.append(_attr)
                    logger.log("info", f"{user['first_name']} Study {_study['name']}  Created attr: {_attr}")

                for si in range(random.randint(1, 20)):
                    _out = random.choice([True, False])
                    if _out:
                        _pips = random.choice(range(0, 500))
                    else:
                        _pips = random.choice(range(0, 100))

                    d1 = datetime.strptime('1/1/2018', '%m/%d/%Y')
                    d2 = datetime.strptime('1/12/2020', '%m/%d/%Y')
                    random_date = d1 + timedelta(seconds=random.randint(0, int((d2 - d1).total_seconds())))

                    s_item = {
                        "study_uid": _study['uid'],
                        "description": f"Study Item {si}",
                        "instrument_uid": random.choice(insts)['uid'],
                        "position": _out,
                        "outcome": random.choice([True, False]),
                        "pips": _pips,
                        "date": str(random_date),
                        "style_uid": random.choice(styles)['uid'],
                        "rrr": random.choice(range(1, 6)),
                        "attributes": random.sample(created_atrs, random.randint(0, len(created_atrs))),
                        "public": random.choice([True, False]),
                    }

                    _st_it = self.send("http://localhost:8000/api/v1/mspt/studyitems", data=s_item,  token=token)
                    logger.log("info", f"{user['first_name']} Created _study Item: {_st_it}")
                    time.sleep(1)

    def create_user_trades(self):
        for user in self.users[:100]:
            token, user_uid = self.login(user)

            instruments = self.fetch("http://localhost:8000/api/v1/mspt/instrument/", token=token)
            styles = self.fetch("http://localhost:8000/api/v1/mspt/style/", token=token)
            strategies = self.fetch("http://localhost:8000/api/v1/mspt/strategy/", token=token)

            for trade in range(random.randint(1, 500)):
                rr = random.choice(range(1, 6))
                _out = random.choice([True, False])
                if _out:
                    _pips = random.choice(range(0, 500))
                else:
                    _pips = random.choice(range(0, 100))

                sl = random.choice(range(30, 100))
                tp = rr * sl

                d1 = datetime.strptime('1/1/2018', '%m/%d/%Y')
                d2 = datetime.strptime('1/12/2020', '%m/%d/%Y')
                random_date = d1 + timedelta(seconds=random.randint(0, int((d2 - d1).total_seconds())))

                tr_sc = {
                  "instrument_uid": random.choice(instruments)['uid'],
                  "position": random.choice([True, False]),
                  "status": False,
                  "style_uid": random.choice(styles)['uid'],
                  "pips": _pips,
                  "outcome": _out,
                  "date": str(random_date),
                  "description": "My awesome trade",
                  "strategy_uid": random.choice(strategies)['uid'],
                  "rr": rr,
                  "sl": sl,
                  "tp": tp,
                  "tp_reached": random.choice([True, False]),
                  "tp_exceeded": random.choice([True, False]),
                  "full_stop": random.choice([True, False]),
                  "entry_price": 0.000,
                  "sl_price": 0.0000,
                  "tp_price": 0.00000,
                  "scaled_in": random.choice([True, False]),
                  "scaled_out": random.choice([True, False]),
                  "correlated_position": random.choice([True, False]),
                  "owner_uid": user_uid,
                  "public": random.choice([True, False]),
                }

                _trade = self.send("http://localhost:8000/api/v1/mspt/trade", data=tr_sc,  token=token)
                logger.log("info", f"{user['first_name']} Created _trade: {_trade}")
                time.sleep(1)




if __name__ == '__main__':
    print("Sniper OSOKING ....... .....")    
    
    tool = MSPT()

    # tool.create_users()
    tool.create_user_instruments()
    tool.create_user_strategies()
    tool.create_user_tplans()
    tool.create_user_tasks()
    tool.create_studies()
    tool.create_user_trades()
