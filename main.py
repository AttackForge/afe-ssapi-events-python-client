#!/usr/bin/env python3
import asyncio
import json
import os
import signal
import ssl
import sys
import uuid
import websockets

from datetime import datetime, timezone
from json.decoder import JSONDecodeError

def notification(method, params):
    print('method:', method)
    print('params:')
    print(json.dumps(params, indent=2))

    # ENTER YOUR INTEGRATION CODE HERE
    # method contains the event type e.g. vulnerability-created
    # params contains the event body e.g. JSON object with timestamp & vulnerability details

signalled = False
subscription_requests = {}

def signal_handler(signum, frame):
    global signalled
    signalled = True
    sys.exit()

async def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await connect()

async def connect():
    if 'HOSTNAME' not in os.environ:
        print('Environment variable HOSTNAME is undefined', file=sys.stderr)
        sys.exit(1)

    if 'EVENTS' not in os.environ:
        print('Environment variable EVENTS is undefined', file=sys.stderr)
        sys.exit(1)

    if 'X_SSAPI_KEY' not in os.environ:
        print('Environment variable X_SSAPI_KEY is undefined', file=sys.stderr)
        sys.exit(1)

    port = 443

    if 'PORT' in os.environ:
        port = os.environ['PORT']
    
    uri = 'wss://{}:{}/api/ss/events'.format(os.environ['HOSTNAME'], port)

    headers = { 'X-SSAPI-KEY': os.environ['X_SSAPI_KEY'] }

    # Comment out the following out if using self-signed certificates
    ssl_context = ssl.create_default_context()

    # Uncomment the following if using self-signed certificates
    #ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)

    async with websockets.connect(
        uri, ping_interval=None, ping_timeout=None, ssl=ssl_context, extra_headers=headers
    ) as websocket:

        global heartbeat_task
        heartbeat_task = asyncio.create_task(heartbeat(websocket))

        await subscribe(websocket)

        try:
            async for message in websocket:
                await process(websocket, message)
        except:
            if not signalled:
                await asyncio.sleep(1)
                await connect()

async def process(websocket, message):
    try:
        payload = json.loads(message)

        if 'jsonrpc' in payload and payload['jsonrpc'] == '2.0':
            if 'method' in payload:
                if 'id' in payload:
                    if payload['method'] == 'heartbeat':
                        await websocket.send(json.dumps({
                            'jsonrpc': '2.0',
                            'result': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                            'id': payload['id']
                        }))

                        global heartbeat_task
                        heartbeat_task.cancel()
                        heartbeat_task = asyncio.create_task(heartbeat(websocket))
                else:
                    params = None

                    if 'params' in payload:
                        params = payload['params']

                    if 'timestamp' in params:
                        store_replay_timestamp(params['timestamp'])

                    notification(payload['method'], params)

            elif 'result' in payload and 'id' in payload:
                await success(websocket, payload['result'], payload['id'])
            elif 'error' in payload and 'id' in payload:
                await failure(websocket, payload['error'], payload['id'])
            else:
                print('unsupported message format', file=sys.stderr)

    except JSONDecodeError as err:
        print('error parsing message', file=sys.stderr)
        print(err, file=sys.stderr)

async def heartbeat(websocket):
    await asyncio.sleep(30 + 1)
    await websocket.close()

def load_replay_timestamp():
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')

    try:
        with open('.replay_timestamp', 'r') as f:
            result = f.read(24)

            if len(result) == 24:
                timestamp = result
                print('Loaded replay timestamp from storage: {}'.format(timestamp))
            else:
                print('Invalid timestamp stored in ".replay_timestamp"')
    except:
        if 'FROM' in os.environ:
            print('Loaded replay timestamp from environment: {}'.format(os.environ['FROM']))
            timestamp = os.environ['FROM']

    return timestamp

def store_replay_timestamp(timestamp):
    with open('.replay_timestamp', 'w') as f:
        f.write(timestamp)

async def subscribe(websocket):
    events = list(map(lambda x: x.strip(), os.environ['EVENTS'].split(',')))
    request_id = str(uuid.uuid4())

    request = {
        'jsonrpc': '2.0',
        'method': 'subscribe',
        'params': {
            'events': events,
            'from': load_replay_timestamp()
        },
        'id': request_id
    }

    subscription_requests[request_id] = {
        'request': request,
        'timeout_task': asyncio.create_task(subscription_request_timeout(websocket, request_id))
    }

    await websocket.send(json.dumps(request))

async def success(websocket, result, id):
    print('Subscribed to the following events:', result)
    subscription_requests[id]['timeout_task'].cancel()
    del subscription_requests[id]

async def failure(websocket, error, id):
    print('Subscription request {} failed - exiting'.format(id))
    print(error)

    subscription_requests[id]['timeout_task'].cancel()
    del subscription_requests[id]

    await websocket.close()

async def subscription_request_timeout(websocket, request_id):
    await asyncio.sleep(5)
    print('Subscription request {} timed out - exiting'.format(request_id))
    del subscription_requests[request_id]
    await websocket.close()

asyncio.run(main())
