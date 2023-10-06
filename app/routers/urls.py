from fastapi import APIRouter
from fastapi.responses import FileResponse
import json
from urllib.request import urlopen
from base64 import b64decode, b64encode
from pprint import pprint

router = APIRouter()


@router.get('/', tags=['default'], name='root')
async def root_path():
    return "Hello, from home page!!!"


@router.get('/favicon.ico', response_class=FileResponse, name='favicon', tags=['favicon'])
async def favicon() -> str:
    return 'static/images/logo/favicon.ico'


@router.get("/sentry-debug/", name='sentry-debug', tags=['sentry-debug'])
async def trigger_error():
    division_by_zero = 1 / 0


@router.get('/vfs/', name='vfs-fd')
def vf():
    subscribe_url = 'https://2kk.uk/link/QlhcCp47nGXFwofW'
    return_content = urlopen(subscribe_url).read()
    print(return_content)

    share_links = b64decode(return_content).decode('utf-8').splitlines()

    strs = "\n".join(share_links)

    result = b64encode(strs.encode("utf-8"))
    return result


@router.get('/vfs-vile/', name='vfs-file', response_class=FileResponse)
def ffs():
    return 'static/fjfj'
