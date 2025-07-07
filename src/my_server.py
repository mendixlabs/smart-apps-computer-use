import json
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler


from tools import (
    TOOL_GROUPS_BY_VERSION,
    ToolCollection,
    ToolResult,
    ToolVersion,
)

from typing import Any, cast

import asyncio
import threading


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6

class AsyncRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()


class MyCustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_response_dict(self, result):
        response_dict = {
            "error_message": result.error,
            "system": result.system,
            "output": result.output,
            "base64image": result.base64_image
        }
        filtered_dict = {k: v for k, v in response_dict.items() if v not in (None, "")}
        return filtered_dict

    def send_result(self, code, result):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
                json.dumps(self.create_response_dict(result)).encode()
            )

    def do_GET(self):
        # Disable serving of static files
        self.send_error(405, "Method Not Allowed")

    def do_POST(self):
        # Implement the logic for handling POST requests from the Mendix App
        if self.path == "/computer_tool":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            # Extract the necessary fields from the JSON data
            action = data.get("action")
            text = data.get("text")
            scroll_direction = data.get("scroll_direction")
            scroll_amount = data.get("scroll_amount")
            key = data.get("key")
            duration = data.get("duration")
            coordinate = list(data.get("coordinate", [None, None])) if "coordinate" in data else None
            
            # Find the tool collection for the specified version
            tool_group = TOOL_GROUPS_BY_VERSION["computer_use_20250124"]
            tool_collection = ToolCollection(*(ToolCls() for ToolCls in tool_group.tools))
            
            # Call the tool in the tool collection with the input as provided by the Mendix App
            async_runner = AsyncRunner()
            result = async_runner.run(tool_collection.run(
                     name="computer",
                     tool_input={"action": action, "coordinate": coordinate, "text": text, "scroll_direction": scroll_direction, "scroll_amount": scroll_amount, "duration": duration, "key": key},
                 ))
           
            if result.error != "":
                self.send_result(400, result)
            else:
                self.send_result(200, result)
        else:
            self.send_error(404, "Not Found")


def run_server():
    server_address = ("::", 8081)
    httpd = HTTPServerV6(server_address, MyCustomHandler)
    print("Starting HTTP server on port 8081...")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()

# This code is a simple HTTP server that listens for POST requests on the path "/computer_tool".
# It processes the request data, runs a tool from a predefined collection, and sends back the result as a JSON response.