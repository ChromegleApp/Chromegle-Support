import json
from typing import List

from aiohttp.abc import Request
from aiohttp.web_response import Response, json_response
from aiohttp.web_routedef import RouteTableDef, RouteDef

routes = RouteTableDef()


@routes.get("/")
async def home(request: Request):
    bot = request.app['bot']['cache']
    r: List[RouteDef] = list(routes)

    url: str = str(request.url)

    text = (
        f"<!DOCTYPE html>\n"
        f"<html>\n"
        f"<body>"
        f"<h1>Welcome to {bot.user}'s API</h1>\n"
        f"<h3>Path List:</h3>" +
        '<br>'.join([f'<a href="{url[:len(url) - 1] + i.path}">{i.path}</a>' for i in r[1:]]) +
        "</body>"
        "</html"
    )

    return Response(text=text, content_type='html')


@routes.get("/streaming")
async def streaming(request: Request):
    bot = request.app['bot']['cache']
    return json_response(bot.streaming, status=200, content_type='application/json')
