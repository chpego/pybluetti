"""STOMP-over-websocket client for BLUETTI's real-time device push updates."""

import json
import logging
import threading
import time
import warnings
from collections.abc import Callable
from threading import Thread

# stomper's stompbuffer module has an invalid regex escape sequence that
# raises a SyntaxWarning on import (fixed in no released version as of
# 0.4.3); silence it here so it isn't misattributed to this package.
with warnings.catch_warnings():
    warnings.simplefilter("ignore", SyntaxWarning)
    import stomper

import websocket

from .exceptions import ApplicationRuntimeException

__LOGGER__ = logging.getLogger(__name__)


class StompClient:
    """A STOMP client connected to the BLUETTI cloud's push-update websocket."""

    def __init__(
        self,
        url: str,
        access_token: str,
        handler: Callable[[str], None] | None = None,
        on_auth_expired: Callable[[], None] | None = None,
    ) -> None:
        """
        Initialize the client.

        - url: the websocket base URL (region-specific).
        - access_token: the OAuth2 access token to authenticate the connection with.
        - handler: called with each MESSAGE frame's body.
        - on_auth_expired: called when the cloud reports the access token as
          expired (msgCode 805), so the caller can react.
        """
        self.__url = url + "/websocket"
        self.__headers = {
            "Host": self.__get_host(url),
            "Authorization": access_token,
        }
        self.listener = StompListener(self, handler)
        self.on_auth_expired = on_auth_expired
        self.websocket = None
        self.running = False

        self.heartbeat_thread = None
        self.heartbeat_interval = 10

    @staticmethod
    def __get_host(connection_url: str) -> str:
        host = connection_url.split("//")[1]
        index = host.find("/")
        host = host[0:index]

        if host.find(":") > -1:
            host = host.split(":")[0]
        return host

    def connect(self) -> None:
        """Connect to the ws server by the long term."""
        stomp_trace = False
        websocket.enableTrace(stomp_trace)

        __LOGGER__.info("Start to connect the BLUETTI WebSocket Server.")
        __LOGGER__.info("Stomp client trace enable: %s", stomp_trace)

        self.websocket = websocket.WebSocketApp(
            self.__url,
            on_message=self.listener.on_message,
            on_error=self.listener.on_error,
            on_close=self.listener.on_close,
        )
        # bind the `on_open` function
        self.websocket.on_open = self.__on_open
        self.running = True
        self.reconnect_delay = 1  # initial reconnect delay (seconds)
        self.max_reconnect_delay = 30  # max reconnect delay (seconds)
        # Run until interruption to client or server terminates connection.
        Thread(target=self._run_forever_safe, daemon=True, name="bluetti-ws").start()

    def _run_forever_safe(self) -> None:
        try:
            self.websocket.run_forever()
        except Exception:
            __LOGGER__.exception("BLUETTI WebSocket thread crashed")
            if self.running:
                self.reconnect()

    def disconnect(self) -> None:
        """Disconnect from the websocket and stop the heartbeat thread."""
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        self.websocket.close()

    def __on_open(self, ws: websocket.WebSocketApp) -> None:
        # Initial CONNECT required to initialize the server's client registries.
        connect = (
            "CONNECT\n"
            "accept-version:1.0,1.1,2.0\n"
            "Host:" + self.__headers["Host"] + "\n"
            "Authorization: " + self.__headers["Authorization"] + "\n"
            "heart-beat:10000,10000\n"
            "\n\x00\n"
        )

        __LOGGER__.info("Connect the BLUETTI WebSocket Server successfully.")
        ws.send(connect)

        # start heartbeat thread
        self._start_heartbeat()

    def _start_heartbeat(self) -> None:
        """Start heartbeat thread."""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return

        self.heartbeat_thread = threading.Thread(target=self._send_heartbeat, daemon=True)
        self.heartbeat_thread.start()

    def _send_heartbeat(self) -> None:
        """Loop send heartbeat."""
        while self.running and self.websocket and hasattr(self.websocket, "sock") and self.websocket.sock:
            try:
                if not self.websocket.sock.connected:
                    break

                self.websocket.send("\n")
                __LOGGER__.debug("Sent STOMP heartbeat")

            except Exception as e:
                __LOGGER__.error("Failed to send heartbeat: %s", e)
                break

            time.sleep(self.heartbeat_interval)

    def reconnect(self) -> None:
        """Reconnect with exponential backoff, if still running."""
        __LOGGER__.info("Websocket reconnect")
        if self.running:
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            self.connect()
        else:
            __LOGGER__.info("Websocket have stop do not reconnect")


class StompListener:
    """Handles STOMP frames received over the websocket connection."""

    def __init__(self, stompCliet: StompClient, handler: Callable[[str], None] | None = None) -> None:
        self.__handler = handler
        self.client = stompCliet

    def __callback(self, callback: Callable[[str], None] | None, *args: str) -> None:
        if callback:
            try:
                callback(*args)
            except Exception as e:
                __LOGGER__.error("error from callback %s: %s", callback, e)

    def __on_subscribe(self, ws: websocket.WebSocketApp, destination: str) -> None:
        sub = stomper.subscribe(destination, "clientUniqueId", ack="auto")
        ws.send(sub)

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """Handle an incoming STOMP frame."""
        __LOGGER__.debug("Received the BLUETTI websocket message:\n %s", message)

        if not message or message == "\n":
            __LOGGER__.debug("Received heartbeat from server")
            return

        frame = stomper.Frame()
        frame.unpack(message)

        if frame.cmd == "ERROR":
            error = frame.headers["message"].replace("\\c", ":")
            error = json.loads(error)
            if error["msgCode"] == 805:
                self.client.disconnect()
                if self.client.on_auth_expired is not None:
                    self.client.on_auth_expired()
                __LOGGER__.info("token have expired stop ws connect")
            else:
                raise ApplicationRuntimeException(msgCode=error["msgCode"], errMessage=error["message"])
        elif frame.cmd == "CONNECTED":
            heartbeat = frame.headers.get("heart-beat", "0,0")
            server_send, server_receive = map(int, heartbeat.split(","))
            __LOGGER__.info(
                "Server heartbeat configuration: send=%s, receive=%s",
                server_send, server_receive,
            )

            user_name = frame.headers.get("user-name")
            if not user_name:
                __LOGGER__.error("CONNECTED frame missing 'user-name' header, cannot subscribe")
                return
            destination = f"/ws-subscribe/user/{user_name}/notify"
            self.__on_subscribe(ws, destination)
        elif frame.cmd == "MESSAGE":
            self.__callback(self.__handler, frame.body)

    @staticmethod
    def on_error(ws: websocket.WebSocketApp, error: str) -> None:
        """Handle a websocket-level error."""
        __LOGGER__.error("The BLUETTI WebSocket raised an error: %s", error)

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        """Handle the websocket connection closing, and trigger a reconnect."""
        __LOGGER__.debug(
            "WebSocket connection closed. Status code: %s, message: %s",
            close_status_code, close_msg,
        )
        self.client.reconnect()
