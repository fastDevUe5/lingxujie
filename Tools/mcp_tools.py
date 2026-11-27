"""Ask the editor's MCP server which tools it exposes, and grep them.

Guessing tool names wastes runs: the server answers with exact unknown-tool errors but never with a
list. This speaks the protocol directly - initialize, then tools/list - and prints every tool whose
name mentions the thing being looked for.

    python Tools/mcp_tools.py camera
    python Tools/mcp_tools.py
"""

import json
import sys
import urllib.request

URL = "http://127.0.0.1:8000/mcp"


def post(payload, session=None):
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    request = urllib.request.Request(URL, data=body, headers=headers,
                                     method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read().decode("utf-8", "replace")
        sid = response.headers.get("Mcp-Session-Id")
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            line = line[5:].strip()
        if line.startswith("{"):
            try:
                return json.loads(line), sid
            except json.JSONDecodeError:
                continue
    return None, sid


def main():
    needle = (sys.argv[1] if len(sys.argv) > 1 else "").lower()

    init, session = post({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "dsh-probe", "version": "1.0"}},
    })
    if session:
        try:
            post({"jsonrpc": "2.0", "method": "notifications/initialized"},
                 session)
        except Exception:  # noqa: BLE001
            pass

    listing, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                       "params": {}}, session)
    if not listing or "result" not in listing:
        print("no tool list: %s" % (listing,))
        return 1

    tools = listing["result"].get("tools", [])
    print("tools: %d" % len(tools))
    for tool in tools:
        name = tool.get("name", "")
        description = (tool.get("description") or "").replace("\n", " ")[:90]
        if needle and needle not in name.lower() and needle not in description.lower():
            continue
        print("  %-46s %s" % (name, description))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
