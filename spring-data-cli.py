import requests, json, sys, os

username = ''
password = ''
account_id = ''
VIN = ''

if os.path.exists('config.json'):
    with open('config.json', 'r') as fp:
        _config = json.load(fp)
        username = _config['username']
        password = _config['password']
        account_id = _config['account_id']
        VIN = _config['VIN']

_config_url = 'https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_ro_RO.json'

_auth_url = '{}/accounts.login?password={}&loginID={}&ApiKey={}'
_info_url = '{}/accounts.getAccountInfo?login_token={}&ApiKey={}'
_jwt_url = '{}/accounts.getJWT?login_token={}&ApiKey={}&fields=data.personId,data.gigyaDataCenter&expiration=900'


_vehicle_battery = '{}/commerce/v1/accounts/{}/kamereon/kca/car-adapter/v2/cars/{}/battery-status?country=RO'
_vehicle_cockpit = '{}/commerce/v1/accounts/{}/kamereon/kca/car-adapter/v2/cars/{}/cockpit?country=RO'
_vehicle_hvac = '{}/commerce/v1/accounts/{}/kamereon/kca/car-adapter/v1/cars/{}/hvac-status?country=RO'
_vehicle_location = '{}/commerce/v1/accounts/{}/kamereon/kca/car-adapter/v1/cars/{}/location?country=RO'

_login_data = None
_login_session = None
_login_account = None
_login_creds = None

def get_vehicle_data(target_url):
    ret = requests.get(target_url.format(_login_data['servers']['wiredProd']['target'],
                                  account_id, VIN),
                    headers={
                        'content-type': 'application/json',
                        'apikey': 'YjkKtHmGfaceeuExUDKGxrLZGGvtVS0J',
                        'x-gigya-id_token': _login_creds['id_token']
                    })
    if ret.status_code != 200:
        print(f'[!!] status code: {ret.status_code}')
        print(f'[!!] status response: {ret.text}')
        print(f'[!!] url: {ret.url}')
        return None
    data = json.loads(ret.text)
    for k in data['data']['attributes'].keys():
        print('{}: {}'.format(k, data["data"]["attributes"][k]))

# get the latest configuration
ret = requests.get(_config_url)
if ret.status_code == 200:
    _login_data = json.loads(ret.text)

# login 
ret = requests.post(_auth_url.format(_login_data['servers']['gigyaProd']['target'], 
                                     password,
                                     username, 
                                     _login_data['servers']['gigyaProd']['apikey']),
                    headers={'content-type': 'application/x-www-form-urlencoded'})
if ret.status_code == 200:
    _login_session = json.loads(ret.text)
    if _login_session['statusCode'] != 200:
        _err = _login_account['statusReason']
        print(f'[!!] login error: {_err}')
        sys.exit(1)

# get account info
ret = requests.post(_info_url.format(_login_data['servers']['gigyaProd']['target'], 
                                     _login_session['sessionInfo']['cookieValue'], 
                                     _login_data['servers']['gigyaProd']['apikey']),
                    headers={'content-type': 'application/x-www-form-urlencoded'})
if ret.status_code == 200:
    _login_account = json.loads(ret.text)
    if _login_account['statusCode'] != 200:
        _err = _login_account['statusReason']
        print(f'[!!] get jwt error: {_err}')
        sys.exit(1)

# get JWT token
ret = requests.post(_jwt_url.format(_login_data['servers']['gigyaProd']['target'], 
                                    _login_session['sessionInfo']['cookieValue'], 
                                    _login_data['servers']['gigyaProd']['apikey']),
                    headers={'content-type': 'application/x-www-form-urlencoded'})
if ret.status_code == 200:
    _login_creds = json.loads(ret.text)
    if _login_creds['statusCode'] != 200:
        _err = _login_creds['statusReason']
        print(f'[!!] get jwt error: {_err}')
        sys.exit(1)

get_vehicle_data(_vehicle_cockpit)
get_vehicle_data(_vehicle_battery)
get_vehicle_data(_vehicle_hvac)
get_vehicle_data(_vehicle_location)