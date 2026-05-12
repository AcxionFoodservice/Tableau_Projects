"""Tableau Cloud REST API authentication helper."""
import os
import requests
import xml.etree.ElementTree as ET

SERVER   = os.environ.get("TABLEAU_SERVER", "https://us-east-1.online.tableau.com")
SITE     = os.environ.get("TABLEAU_SITE", "einstein")
API_VER  = "3.19"
SITE_ID  = "35367310-317e-40a8-8bd8-1b9f19988cd9"
NS       = "http://tableau.com/api"


def get_token() -> str:
    pat_name   = os.environ["TABLEAU_PAT_NAME"]
    pat_secret = os.environ["TABLEAU_PAT_SECRET"]
    resp = requests.post(
        f"{SERVER}/api/{API_VER}/auth/signin",
        headers={"Content-Type": "application/xml"},
        data=(
            f'<tsRequest>'
            f'<credentials personalAccessTokenName="{pat_name}"'
            f' personalAccessTokenSecret="{pat_secret}">'
            f'<site contentUrl="{SITE}" />'
            f'</credentials></tsRequest>'
        ),
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    err = root.find(f".//{{{NS}}}error")
    if err is not None:
        raise RuntimeError(f"Tableau auth failed: {err.get('code')} — {err.findtext(f'{{{NS}}}detail')}")
    return root.find(f".//{{{NS}}}credentials").get("token")


def get_paged(token: str, path: str, tag: str, extra: str = "") -> list:
    headers = {"x-tableau-auth": token}
    items, page = [], 1
    while True:
        url = f"{SERVER}/api/{API_VER}/sites/{SITE_ID}/{path}?pageSize=100&pageNumber={page}{extra}"
        root = ET.fromstring(requests.get(url, headers=headers).text)
        page_items = root.findall(f".//{{{NS}}}{tag}")
        items.extend(page_items)
        pag = root.find(f".//{{{NS}}}pagination")
        if pag is None or len(items) >= int(pag.get("totalAvailable", 0)):
            break
        page += 1
    return items


def get_one(token: str, path: str):
    return ET.fromstring(
        requests.get(
            f"{SERVER}/api/{API_VER}/sites/{SITE_ID}/{path}",
            headers={"x-tableau-auth": token},
        ).text
    )
