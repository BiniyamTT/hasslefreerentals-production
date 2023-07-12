import requests

# your API secret from (Tools -> API Keys) page
apiSecret = "1ccdc141f237b2c18dfb44dc7716095c2f1ada70"

# otp from a user supplied input or data
otpCode = "339863"

r = requests.get(url = "https://hahu.io/api/get/otp", params = {
    "secret": apiSecret,
    "otp": otpCode
})
  
# do something with response object
result = r.json()
print(result)