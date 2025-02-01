import cloudscraper
from base64 import b64encode
import json
import random
from datetime import datetime
import re
import time
from os import path
import mimetypes
from functools import wraps
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()

def function_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        spinner = Spinner("dots", text=f"[blue]Thinking...[/blue]")
        start_time = time.time() 
        
        with Live(spinner, console=console, refresh_per_second=10):
            result = func(*args, **kwargs)  
        
        end_time = time.time()
        execution_time = end_time - start_time  

        console.print(f"[bold green]Answer got in {execution_time:.4f} seconds.[/bold green]")
        return result 
    return wrapper

class DeepSeek:
    def __init__(self,cookie:dict,user_token:str)->None:
        """
        initialize the class
        """
        self.main_url:str = "https://chat.deepseek.com"
        
        self.scraper = cloudscraper.create_scraper()
        
        self.cookie:dict = cookie
        
        self.headers:dict = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Client-Platform": "web",
            "X-Client-Version": "1.0.0-always",
            "X-Client-Locale": "en_US",
            "X-App-Version": "20241129.1",
            "Authorization": f"Bearer {user_token}",
            "Origin": self.main_url,
            "Referer": f"{self.main_url}/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
        }

        self.chtroom_id:str = ""
        self.message_id = 1
    

    def create_chatroom(self) -> str:
        """
        Creates a new chatroom

        :return: chatroom id
        """
        json_data = {
            'character_id': None,
        }
        max_retries = 3
        for _ in range(max_retries):
            try:
                r = self.scraper.post(
                    f"{self.main_url}/api/v0/chat_session/create",
                    headers=self.headers,
                    cookies=self.cookie,
                    json=json_data
                )
                if r.status_code == 403:
                    time.sleep(6)
                    continue
                self.chtroom_id = r.json()["data"]["biz_data"]["id"]
                self.headers['Referer'] = f'{self.main_url}/a/chat/s/{self.chtroom_id}'
                return self.chtroom_id
            except Exception as e:
                print(r.text)
                raise Exception("[X]Chatroom creation failed with error:", e)
        raise Exception("[X]Chatroom creation failed after multiple attempts. Maybe change the cookies")
        
    def create_pow_challenge(self,file_upload:bool=False)->str:
        """
        Creates a pow challenge

        :return: pow challenge data
        """
        pow_data_structure:dict={

            "algorithm":"DeepSeekHashV1",
            "challenge":"",
            "salt":"",
            "answer":random.randint(600000,700000),
            "signature":"",
            "target_path":""
        }

        if file_upload:

            json_data:dict = {
                'target_path': '/api/v0/file/upload_file'
            }
            pow_data_structure["target_path"] = "/api/v0/file/upload_file"
        else:
            json_data:dict = {
                'target_path': '/api/v0/chat/completion'
            }
            pow_data_structure["target_path"] = "/api/v0/chat/completion"

        try:
            r = self.scraper.post(
                f'{self.main_url}/api/v0/chat/create_pow_challenge',
                cookies=self.cookie,
                headers=self.headers,
                json=json_data
            )

            if r.status_code == 403:
                console.print("[red][X]Retrying pow_challenge...[/red]")
                time.sleep(7)
                #change Hm_lpvt_1fff341d7a963a4043e858ef0e19a17c cookie
                self.cookie["Hm_lpvt_1fff341d7a963a4043e858ef0e19a17c"] = str(int(datetime.now().timestamp()))

                r = self.scraper.post(
                    f'{self.main_url}/api/v0/chat/create_pow_challenge',
                    cookies=self.cookie,
                    headers=self.headers,
                    json=json_data)

            pow_data_structure["challenge"] = r.json()["data"]["biz_data"]["challenge"]["challenge"]
            pow_data_structure["salt"] = r.json()["data"]["biz_data"]["challenge"]["salt"]
            pow_data_structure["signature"] = r.json()["data"]["biz_data"]["challenge"]["signature"]
            
            b64_encoded = b64encode(json.dumps(pow_data_structure).encode()).decode()
            
            return b64_encoded
        except Exception as e:
            raise Exception("[X]Pow challenge creation failed with error:",e)
    
    @function_timer
    def ai_response(self,prompt:str,file_list:list=None,r1_enabled:bool=False,web_search:bool=False)->str:
        """
        Get response from the ai

        :param prompt: The prompt to send to the ai
        :param file_list: List of files to send to the ai
        :param r1_enabled: R1 enabled
        :param web_search: Web search enabled
        :return: The response from the ai
        """
        json_data = {}

        if file_list:
            #upload the files
            #get file ids
            #create a new json data
            file_ids = []
            for f in file_list:
                #chek if file exists or not
                if not path.exists(f):
                    raise Exception("[X]File does not exist:",f)
                
                file_name = path.basename(f)
                mime_type = mimetypes.guess_type(f)[0]
                with open(f, "rb") as file:
                    files = {
                        "file" : (
                            file_name,
                            file,
                            mime_type
                        )
                    }

                    #get the pow challenge
                    self.headers["X-Ds-Pow-Response"] = self.create_pow_challenge(file_upload=True)

                    #send the request
                    try:
                        r = self.scraper.post(
                            f'{self.main_url}/api/v0/file/upload_file',
                            headers=self.headers,
                            cookies=self.cookie,
                            files=files
                        )
                    except:
                        print("[X]File upload failed")
                        pass

                    #get the file id
                    file_ids.append(r.json()["data"]["biz_data"]["id"])
                file.close()
            
            #check for each file id
            print("Sleeping for 10 seconds for file upload process")
            time.sleep(10)

            all_files_uploaded = False
            while not all_files_uploaded:
                all_files_uploaded = True
                for file_id in file_ids:

                    #removing the pow response header
                    temp_headers = self.headers.copy()
                    temp_headers.pop("X-Ds-Pow-Response", None)

                    r = self.scraper.get(
                        f'{self.main_url}/api/v0/file/fetch_files?file_ids={file_id}',
                        cookies=self.cookie,
                        headers=temp_headers, 
                    )
                    
                    if r.json()["data"]["biz_data"]["files"][0]["status"] != "SUCCESS":
                        all_files_uploaded = False
                        print("[*]Still waiting for file upload")
                        time.sleep(2)
                        break
                    elif r.json()["data"]["biz_data"]["files"][0]["status"] == "SUCCESS":
                        print(f"[*]{file_id} uploaded successfully")

            json_data = {
                'chat_session_id': self.chtroom_id,
                'prompt': prompt,
                'ref_file_ids': file_ids,
                'thinking_enabled': r1_enabled,
                'search_enabled': False, #can't use web search with file attachment
            }

        
        else:
            #for normal prompt
            json_data = {
                'chat_session_id': self.chtroom_id,
                'prompt': prompt,
                'ref_file_ids': [],
                'thinking_enabled': r1_enabled,
                'search_enabled': web_search,
            }
        
        #calculate message id
        if self.message_id == 1:
            json_data["parent_message_id"] = None
            self.message_id += 1
        else:
            json_data["parent_message_id"] = self.message_id
            self.message_id += 3
        
        try:
            #get pow challenge data
            pow_challenge = self.create_pow_challenge()
            self.headers["X-Ds-Pow-Response"] = pow_challenge

            #send the request
            r = self.scraper.post(
                f'{self.main_url}/api/v0/chat/completion',
                cookies=self.cookie,
                headers=self.headers,
                json=json_data,
            )
        
            #cleanup the text
            response = r.text.replace('\\"', "'")
            data = "".join(re.findall(r'"content":"(.*?)"', response))
            data = data.replace(r'\n', '\n')

            return data
        except Exception as e:
            raise Exception("[X]AI response failed with error:",e)
