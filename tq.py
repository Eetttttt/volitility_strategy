from tqsdk import TqApi, TqAuth, TqKq

api = TqApi(TqKq(), auth=TqAuth("ggmmh", "gmh339714"))


account = api.get_account()
print(account)
# quote = api.get_quote("SHFE.ni2206")
# print (quote.last_price, quote.volume)

# while True:
#     api.wait_update()
#     print (quote.datetime, quote.last_price)


api.close()
