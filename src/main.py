import platform
import requests
import io
import os
from subprocess import run, PIPE
import json
from pprint import pprint


BASE_PATH = 'https://chromedriver.storage.googleapis.com'
config = {}


def load_config(location='./config.json'):
    global config
    
    #check if location exists
    if not os.path.exists(location) or not os.path.isfile(location):
        print('Unable to find config file at location [' + location + ']')
        exit(-1)

    with open(location, 'r') as configfile:
        config = json.load(configfile)


def list_available_versions():
    file_path = get_download_location()
    files = os.listdir(file_path)
    return files
    

def get_download_location():
    file_path = config['download_location']
    if file_path is None:
        file_path = ''
    
    if not os.path.exists(file_path):
        print('Download location not available, creating new directory.')
        os.makedirs(file_path)
    
    return file_path


def check_if_driver_already_exists(current_version):
    available_drivers = list_available_versions()
    return current_version in available_drivers


#check the current version of chrome on system.
def get_current_chrome_version():
    osname = platform.system()
    chrome_version_command = ["google-chrome", "--version"]
    if osname == 'Darwin':
        chrome_version_command = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]
    proc = run(chrome_version_command, encoding='utf-8', stdout=PIPE)
    version_str = proc.stdout
    if version_str is not None and "Google Chrome" in version_str:
        print("Found Google Chrome : " + str(version_str).strip())
        version_str = version_str.split(" ")[2]
    return version_str

def get_latest_driver_version_for_chrome_version():
    chrome_version = get_current_chrome_version()
    chrome_version_excluding_minor = chrome_version[0:chrome_version.rfind('.')]
    url = BASE_PATH + '/LATEST_RELEASE_' + chrome_version_excluding_minor
    resp = requests.get(url)
    driver_version = resp.text
    
    if driver_version is not None and driver_version.strip() != '':
        print("Latest chromium driver version : " + driver_version)
        
    return driver_version
    
    
def download_latest_chrome_driver():
    driver_version = get_latest_driver_version_for_chrome_version()
    if not config['download_driver']:
        print('Downloading disabled in script configuration. exiting...')
        return
    if check_if_driver_already_exists(driver_version + '.zip'):
        print('Version [' + driver_version + '] already exists, skipping download.')
        return
    
    file_location = get_download_location() +  driver_version + '.zip'
    url = BASE_PATH + '/' + driver_version
    osname = platform.system()
    
    if(osname == 'Darwin'):
        url = url + '/chromedriver_mac64.zip'
    
    print('Downloading from : [' + url + ']')
    resp = requests.get(url, stream=True)
    with open(file_location, 'wb') as f:
        f.write(resp.content)
    
    print('Download complete. File available at [' + file_location + ']')


if __name__ == '__main__':
    print('Starting script : Chrome Driver Auto Update')
    load_config()
    if config is None or len(config) == 0:
        print('Application config not set up!')
        exit(1)
    download_latest_chrome_driver()
    print('Done!')
    
