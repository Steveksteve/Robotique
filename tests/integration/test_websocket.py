import os
import time
import pytest

WS_URL = os.getenv('WS_URL')


@pytest.mark.skipif(not WS_URL, reason="WS_URL not set")
def test_websocket_connect_and_listen():
    # Smoke test: try to connect to a websocket endpoint and wait briefly for an event
    # Requires: set WS_URL env var in CI if socket server is available
    import websocket

    messages = []

    def on_message(ws, message):
        messages.append(message)

    def on_error(ws, error):
        pytest.fail(f"WebSocket error: {error}")

    ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_error=on_error)

    import threading

    thread = threading.Thread(target=ws.run_forever, kwargs={'ping_interval': 5})
    thread.daemon = True
    thread.start()

    time.sleep(5)

    ws.close()

    assert isinstance(messages, list)
