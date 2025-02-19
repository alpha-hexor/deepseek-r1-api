<p align="center"><sup>An unofficial free deepseek api wrapper written in python.</sup></p>

A totally free deepseek api(with latest R1 model) written in python.

# Required Cookies
Create an account in [deepseek.com](https://www.deepseek.com/) and visit [chat.deepseek.com](https://chat.deepseek.com/) and copy the following cookies
```sh
smidV2
HMACCOUNT
Hm_lpvt_fb5acee01d9182aabb2b61eb816d24ff
intercom-session-guh50jw4
HWWAFSESTIME
Hm_lvt_fb5acee01d9182aabb2b61eb816d24ff
HWWAFSESID
.thumbcache_6b2e5483f9d858d7c661c5e276b6a6ae
Hm_lvt_1fff341d7a963a4043e858ef0e19a17c
intercom-device-id-guh50jw4
__cf_bm
ds_session_id
Hm_lpvt_1fff341d7a963a4043e858ef0e19a17c
```
and from **Local Storage** collect ``userToken`` value part

# http headers
```sh
headers={

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "X-Client-Platform": "web",
    "X-Client-Version": "1.0.0-always",
    "X-Client-Locale": "en_US",
    "X-App-Version": "20241129.1",
    "Authorization": "Bearer {userToken}", #collected from local storage
    "Origin": "https://chat.deepseek.com", 
    "Referer": "https://chat.deepseek.com/", #change to 'https://chat.deepseek.com/a/chat/s/{chatroom_id}' after chatroom creation
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0",
    "Te": "trailers",
}
```

# Install packages
```sh
pip install -r requirements.txt
```

# Usage
You can usage the terimnal wrapper this way
```py
from deepseek import DeepSeek
import json
from rich.console import Console
from rich.markdown import Markdown
console = Console()


with open("cookies.json", "r") as f:
    cookies = json.load(f)
f.close()

usertoken = "....." #collect from locla storage

deepseek_engiene:DeepSeek = DeepSeek(cookie=cookies,user_token=usertoken)
```
### Create a chatroom
```py
chatroom_id = deepseek_engiene.create_chatroom()

#you can visit the chatroom https://chat.deepseek.com/a/chat/s/{chtroom_id}
```
### Ai Response method blueprint
```py
def ai_response(self,prompt:str,file_list:list=None,r1_enabled:bool=False,web_search:bool=False)->str:

    """
    Get response from the ai
    :param prompt: The prompt to send to the ai
    :param file_list: List of files to send to the ai
    :param r1_enabled: R1 enabled
    :param web_search: Web search enabled
    :return: The response from the ai
    """
```
### Normal Ai Response
```py
markdown = Markdown(deepseek_engiene.ai_response(prompt=prompt))
console.print(markdown)
```
### Ai hallucination (R1-enabled)
```py
markdown = Markdown(deepseek_engiene.ai_response(prompt=prompt,r1_enabled=True))
console.print(markdown)
```
### Web search Enable
```py
markdown = Markdown(deepseek_engiene.ai_response(prompt=prompt,web_search=True))
console.print(markdown)
```
### File upload
```py
markdown = Markdown(deepseek_engiene.ai_response(file_list=["assets/leetcode.png","assets/leetcode2.png"],prompt="solve the problems in python and complete the function"))
```

# Example output
In the following example deepseek solves two leetcode question from screenshots
```py
markdown = Markdown(deepseek_engiene.ai_response(file_list=["assets/leetcode.png","assets/leetcode2.png"],prompt="solve the problems in python and complete the function"))
```
![create chatroom](assets/output-1.png)
![create chatroom](assets/output-2.png)
![create chatroom](assets/output-3.png)


# CodeFlow (sorta)
1. Creating a chatroom
![create chatroom](assets/account.png)

2. Util Function ``create_pow_challenge``
![create_pow_challenge](assets/challenge_pow.png)

3. Ai responses\
The api endpoint for this is ``/api/v0/chat/completion``

    **First Message**
    ![first_message](assets/first.png)

    **Second Message**
    ![second_message](assets/second.png)

    **Third message and onwards**
    ![third_message](assets/third.png)

    **File upload**
    ![file_upload](assets/file_upload.png)

    **Get file upload status**
    ![file_upload](assets/file_status.png)

    **Use the File id**\
    Use the ``file_id`` in the ``ref_file_ids`` array in the post request

# Todo
~~1. Scrape for file upload~~\
~~2. Code implementation in python.~~\
3. chat history implementation\
4. Start messaging in an already existing chatroom\
5. Better error handling

# Note
**The cloudflare __cf_bm cookie expires every thirty minutes. So if the requests aren't working then refresh the cookies**