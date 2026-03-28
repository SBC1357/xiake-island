"""Quick test for custom rule mode review endpoint."""
import urllib.request
import json

data = json.dumps({
    "content": "这是一段测试文本内容，赋能范式底层逻辑，需要检查是否符合自定义规则。",
    "rule_mode": "custom",
    "custom_rules": ["避免使用网络流行语"],
}).encode()

req = urllib.request.Request(
    "http://127.0.0.1:8001/v1/review/independent/text",
    data=data,
    headers={"Content-Type": "application/json"},
)

try:
    r = urllib.request.urlopen(req)
    resp = json.loads(r.read())
    print("status:", r.status)
    print("review_id:", resp.get("review_id"))
    print("passed:", resp.get("passed"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.reason)
    print(e.read().decode())
