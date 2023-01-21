import requests
import pandas as pd
import configparser

#  we will use configparser to work with our configuration ini file for requests and data location

config = configparser.ConfigParser()
config.read('conf.ini')

