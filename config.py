import yaml
# API 密钥
symbol = 'BTCUSDT'
leverage = 100
max = 1
config = {}

def loadConfig():
    global config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    