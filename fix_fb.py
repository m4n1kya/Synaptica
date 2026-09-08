import base64
import json

with open('backend/firebase-adminsdk.json', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

with open('backend/firestore_store.py', 'r') as f:
    content = f.read()

replacement = f"""    elif True:
        import base64
        cert_dict = json.loads(base64.b64decode("{b64}").decode("utf-8"))
        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
    elif os.environ.get("FIREBASE_SERVICE_ACCOUNT"):"""

new_content = content.replace('    elif os.environ.get("FIREBASE_SERVICE_ACCOUNT"):', replacement)

with open('backend/firestore_store.py', 'w') as f:
    f.write(new_content)
