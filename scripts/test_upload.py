"""Quick integration test for upload pipeline."""
import io
import json
import urllib.request
import urllib.error

from PIL import Image, ImageDraw

# Create a simple test PNG with text
img = Image.new("RGB", (400, 200), "white")
draw = ImageDraw.Draw(img)
draw.text((20, 80), "Test Evidence Image - Medical Data", fill="black")
buf = io.BytesIO()
img.save(buf, format="PNG")
png_bytes = buf.getvalue()
print(f"Created test PNG: {len(png_bytes)} bytes")

# Build multipart form data
boundary = "----TestBoundary12345"
body = b""
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="file"; filename="test_evidence.png"\r\n'
body += b"Content-Type: image/png\r\n\r\n"
body += png_bytes
body += f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://127.0.0.1:8000/v1/evidence/upload/file",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
)

try:
    r = urllib.request.urlopen(req, timeout=120)
    d = json.loads(r.read())
    print(f"Upload status: {d.get('status')}")
    print(f"Upload ID: {d.get('upload_id')}")
    print(f"File type: {d.get('file_type')}")
    evidences = d.get("evidences") or []
    print(f"Evidences returned: {len(evidences)}")
    if d.get("error"):
        print(f"Error: {d.get('error')}")
    if evidences:
        for i, ev in enumerate(evidences):
            print(f"  Evidence {i+1}: type={ev.get('evidence_type')}, confidence={ev.get('confidence')}")
            content = ev.get("content", "")
            print(f"    Content preview: {content[:100]}")
    
    # Also verify upload list
    r2 = urllib.request.urlopen("http://127.0.0.1:8000/v1/evidence/upload/list")
    d2 = json.loads(r2.read())
    print(f"\nUpload list total: {d2.get('total')}")
    
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
