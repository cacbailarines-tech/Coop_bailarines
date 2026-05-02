import os
from py_vapid import Vapid

v = Vapid()
v.generate_keys()
private_key = v.private_pem()
public_key = v.public_pem()

print("--- CLAVES VAPID ---")
print("GUARDA ESTO EN TUS VARIABLES DE ENTORNO EN RAILWAY:")
print("\n[WEBPUSH_VAPID_PRIVATE_KEY]")
print(private_key.decode('utf-8'))
print("\n[WEBPUSH_VAPID_PUBLIC_KEY]")
# We need the urlsafe base64 of the public key for the browser, not just the PEM.
# Actually pywebpush / vapid usually expects the URLSAFE B64 public key in settings for the browser to fetch.
# Let's get the raw uncompressed point and encode it.
import base64
from cryptography.hazmat.primitives import serialization
raw_pub = v.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
pub_b64 = base64.urlsafe_b64encode(raw_pub).decode('utf-8').rstrip('=')
print(pub_b64)

# Wait, the pywebpush WebPush function expects vapid_private_key. If we pass the PEM path or the string?
# usually pywebpush accepts the PEM string or path. But it can also accept the base64 encoded private key.
# Let's just output both for safety.
raw_priv = v.private_key.private_numbers().private_value.to_bytes(32, 'big')
priv_b64 = base64.urlsafe_b64encode(raw_priv).decode('utf-8').rstrip('=')
print("\nO Alternativamente en formato Base64 (más facil para variables de entorno):")
print(f"WEBPUSH_VAPID_PRIVATE_KEY={priv_b64}")
print(f"WEBPUSH_VAPID_PUBLIC_KEY={pub_b64}")
