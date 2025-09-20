#!/usr/bin/env python3
"""
Simple webhook redirector from port 8003 to 9001
This redirects the old webhook to the new Docker container
"""
import asyncio
import aiohttp
from aiohttp import web
import json

async def redirect_webhook(request):
    """Redirect all webhook requests to the Docker container on port 9001"""
    try:
        # Get the request data
        if request.content_type == 'application/json':
            data = await request.json()
        else:
            # Handle form data (Twilio sends form data)
            data = dict(await request.post())
        
        # Forward to the Docker container
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:9001' + str(request.path_qs), 
                                  json=data if request.content_type == 'application/json' else None,
                                  data=data if request.content_type != 'application/json' else None,
                                  headers=dict(request.headers)) as resp:
                response_data = await resp.text()
                return web.Response(text=response_data, 
                                  status=resp.status,
                                  content_type=resp.content_type)
    
    except Exception as e:
        print(f"Redirect error: {e}")
        return web.Response(text=f"Redirect failed: {str(e)}", status=500)

async def health_check(request):
    return web.Response(text='Webhook redirector is running', status=200)

def create_app():
    app = web.Application()
    # Catch all routes and redirect them
    app.router.add_route('*', '/webhook', redirect_webhook)
    app.router.add_route('*', '/bot/twilio/webhook', redirect_webhook)
    app.router.add_route('GET', '/health', health_check)
    app.router.add_route('GET', '/', health_check)
    return app

if __name__ == '__main__':
    app = create_app()
    print("🔄 Starting webhook redirector on port 8003 → 9001")
    web.run_app(app, host='0.0.0.0', port=8003)