import fastapi
from talkingheads import ChatGPTClient

chathead = ChatGPTClient(headless=False, incognito=False, sso=True, username="username", password="password", use_subprocess=False)

response = chathead.interact("Hello, how are you today")

print(response)