import requests
from config.settings import ACCESS_TOKEN
from time import sleep

class ZenodoClient:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    def request(self, method, url, **kwargs):
        for attempt in range(3):
            r = requests.request(method, url, headers=self.headers, **kwargs)
            if r.status_code in [429, 500, 503]:
                print(f"Tentativa {attempt + 1} falhou com status {r.status_code}. Retentando em {2 ** attempt} segundos...")
                sleep(2 ** attempt)
                continue
            return r
        r.raise_for_status()