import requests

# your API secret from (Tools -> API Keys) page
apiSecret = "1ccdc141f237b2c18dfb44dc7716095c2f1ada70"

message = {
    "secret": apiSecret,
    "type": "sms",
    "mode": "devices",
    "device": "00000000-0000-0000-0aa2-9d90a03739af",
    "sim": 2,
    "phone": "+251911600710",
    "message": "Your OTP is {{otp}}"
}

r = requests.post(url = "https://hahu.io/api/send/otp", params = message)
  
# do something with response object
result = r.json()

print(result)