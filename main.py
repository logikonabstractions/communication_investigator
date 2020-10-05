""" the investigator:
        * takes a fast & light approach. just write lines of code that directly do something already.
        * but do organize them better (cls, methos, files) better regularly. just not constantly.

    - it initiates a communication with a server (standard http stuff).
    - it then manages the back & forth, keeps track of token/cookies etc.
    - i could make it cmdline interactive. e.g. you would have a list of http replies, arg values etc. & you could discuss, essentially, with the server

    Sample requests to obtain an activity by ID:
        http get "https://www.strava.com/api/v3/activities/{id}?include_all_efforts=" "Authorization: Bearer [[token]]"
    Replacing with our vars here:

        ID = 3427572515
        ACCESS_TOKEN =  a06efe7ae0235b961f1d5d5af6a5ed6202106302            # from /settings/api un "My API application" once logged in valid a few days

        http get f"https://www.strava.com/api/v3/activities/{ID}?include_all_efforts=" "Authorization: Bearer ACCESS_TOKEN"
"""

# no classe, no methods, just code for now

import requests     # lib that manages the back & forth
import json
from utils import *
import os
import json
from utilities.logger import get_root_logger
from utilities.dao import *
from program.validation import TokenManager


class MainProgram:
    """ the high level manager of the program """
    def __init__(self, logger=None):
        # instantiate some objcs
        self.ddao = DiskDao()
        self.sdao = StravaDao()
        self.tok_man = TokenManager(self.ddao)

        self.configs = self.ddao.get_configs()
        self.LOG = logger if logger else self.get_logger()

        self.LOG.info(f"Configs file {os.path.join(USERDATA_DIR, CONFIGS_FILE)} loaded.")
        self.LOG.debug(f"Configs file values: {self.configs}")
        self.LOG.info(f"MainProgram instantiated.")

    def check_init_logs(self):
        """ Checks if some logger has been defined. if not defines it """
        try:
            self.LOG.info(f"Logger already initialized: {self.LOG}")
        except NameError as err:
            self.get_logger()
            self.LOG.warning(f"No logger was instantiated. {self.LOG} was created.")

    @staticmethod
    def get_logger():
        """ inits the logs. should only be if for whatever reason no logger has been defined """
        logger = get_root_logger(BASE_LOGGER_NAME, filename=f'log.log')
        logger.debug(f'logger debug level msg ')
        logger.info(f'logger info level msg ')
        logger.warning(f'logger warn level msg ')
        logger.error(f'logger error level msg ')
        logger.critical(f'logger critical level msg ')
        return logger

    def run(self):
        self.LOG.info(f"MainProgram.run()... ")
        self.ping_strava()
        code = self.launch_oauth_protocol()
        tokens = self.get_tokens_reponse_from_code(code)
        print(tokens)


    def ping_strava(self):
        """ pings stravaé. Returns the who object from requests.get() """
        self.LOG.info(f"Pinging strava.... Expecting 200 OK reply.")
        headers = {}
        r = requests.get(self.sdao.home_url, headers=headers)
        self.LOG.info(f"response status code: {r.status_code}")
        self.LOG.debug(f"full response: {r.text}")
        return r

    def launch_oauth_protocol(self):
        """ makes an authorisation request to strava. format of the rqst:
            :return: a code (which can be used in a 2nd step to get the access/refresh tokens
        """

        if self.tok_man.validate_credentials():
            self.LOG.info(f"using params set in {CONFIGS_FILE} to perform oauth... ")
            code_params = {"client_id": self.client_id, "redirect_uri": 'http://127.0.0.1', "response_type": "code",
                           "approval_prompt": "auto", "scope": "activity:read_all,profile:read_all",
                           "state": "i am the state"}

            oauth_full_url = requests.Request('GET', self.sdao.oauth_code_url, params=code_params).prepare().url

            self.LOG.info(f"Please visit this URL, review the permissions requested & click Authorize if satisfied:")
            self.LOG.info(f"{oauth_full_url}")
            self.LOG.info(f"you will then be redirected to 127.0.0.1, e.g. localhost, and the URL will contain:")
            self.LOG.info(f"http:/(....)&code=b9d4b3bcd690fa1d3dfb81e4e40024363745caf7&scope(....)")
            # self.LOG.info(f"the code entered was {code}. Validating with strava... ")
            code = input("Please enter the alphanumeric code, excluding the termination symbol '&' at the end:")
            return code
        else:                   # TODO: implt. relevent actions if we fail to launc the oauth
            return False

    def get_tokens_reponse_from_code(self, code):
        """ gets you the acess/refresh tokens from strava. returns the dictionnary that contains the strava response (expiration, tokens, etc.) """
        # now we need to do a POST with the above code in params in order to receive our tokens

        if self.tok_man.validate_credentials():
            token_params = {"client_id": 47498, "client_secret": self.client_secret, "code": code,
                            "grant_type": "authorization_code"}
            token_url = self.sdao.oauth_token_url
            self.LOG.info(f"Url for token request from code: {token_url}, code:{code}")
            reponse = requests.post(token_url, params=token_params)
            self.LOG.info(f"TOKEN: {reponse}")
            resp_dict = json.loads(reponse.content)
            return resp_dict
        else:
            return False



    def get_activity_by_id(self, activity_id):
        """ assuming valid access/refresh token are set for this user in configs.json (or db or whereever),
            then fetches that activity id for that user if it exists
        """

        if self.tok_man.validate_credentials():
            pass
        else:
            return False

    @property
    def client_id(self):
        return self.configs["credentials"]["CLIENT_ID"]
    @property
    def client_secret(self):
        return self.configs["credentials"]["CLIENT_SECRET"]
    @property
    def access_token(self):
        return self.configs["credentials"]["ACCESS_TOKEN"]["access_token"]
    @property
    def refresh_token(self):
        return self.configs["credentials"]["ACCESS_TOKEN"]["refresh_token"]





if __name__ == '__main__':
    os.environ["ENV"] = "development"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_LEVEL"] = "INFO"

    program = MainProgram()
    program.run()
