# PumpBot-Yobit-API-FIX-V1

/* YobitBot File */
config.readfp(open('config.txt'))
key = config.get('Yobit', 'Key')
secret = config.get('Yobit', 'Secret')
secret = bytes(secret, 'utf8')

/* config.txt File */
[Yobit]
Key =
Secret =
