"""
AES-256-GCM Encryption Module for Biometric Fingerprints
"""

import os
import re
import secrets
import base64
import numpy as np
import cv2

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC_HEADER = b"FPVAULT1"

def generate_secure_pin():
    """Generates an 8-digit PIN formatted as XXXX-XXXX."""
    p1 = secrets.randbelow(10000)
    p2 = secrets.randbelow(10000)
    return f"{p1:04d}-{p2:04d}"

def encrypt_image_data(image_array, pin=None):
    """
    Encrypts an image array using AES-256-GCM with PBKDF2 key derivation.
    """
    if pin is None:
        pin = generate_secure_pin()

    clean_pin = re.sub(r'[^0-9a-zA-Z]', '', str(pin).strip())
    if not clean_pin:
        raise ValueError("PIN cannot be empty.")

    success, png_buffer = cv2.imencode(".png", image_array)
    if not success:
        raise ValueError("Failed to encode image to PNG format.")
    png_bytes = png_buffer.tobytes()

    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000
    )
    derived_key = kdf.derive(clean_pin.encode("utf-8"))

    aesgcm = AESGCM(derived_key)
    ciphertext = aesgcm.encrypt(nonce, png_bytes, None)

    vault_bytes = MAGIC_HEADER + salt + nonce + ciphertext
    ciphertext_b64 = base64.b64encode(ciphertext).decode("utf-8")

    return pin, vault_bytes, salt.hex(), nonce.hex(), ciphertext_b64

def create_standalone_html_vault(out_html_path, title_name, salt_hex, nonce_hex, ciphertext_b64):
    """
    Generates a single self-contained secure HTML file.
    Recipients can double-click this file to unlock and view the fingerprint
    in ANY browser (Chrome, Edge, Safari, Firefox, iPhone, Android)
    using the browser's hardware-accelerated WebCrypto API.
    """
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Encrypted File - {title_name}</title>
<style>
  :root {{
    --bg-page: #faf9f7;
    --bg-card: #ffffff;
    --ink: #14151a;
    --muted: #6b7280;
    --line: #e4e4e3;
    --green: #1b5e3f;
    --green-dark: #12402a;
    --green-tint: #e7f1ec;
    --red: #b3261e;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: var(--bg-page);
    color: var(--ink);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    -webkit-font-smoothing: antialiased;
  }}

  .card {{
    width: 100%;
    max-width: 400px;
    background: var(--bg-card);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(20, 21, 26, 0.04), 0 6px 20px rgba(20, 21, 26, 0.04);
    padding: 40px 36px;
    text-align: center;
  }}

  .icon-wrap {{
    display: flex;
    justify-content: center;
    margin-bottom: 18px;
  }}

  .lock-icon {{
    width: 38px;
    height: 38px;
    color: var(--ink);
    overflow: visible;
    transition: color 0.3s ease;
  }}

  .lock-icon .shackle {{
    transform-box: fill-box;
    transform-origin: 0% 100%;
    transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
  }}

  .lock-icon.unlocked {{ color: var(--green); }}
  .lock-icon.unlocked .shackle {{ transform: rotate(-32deg); }}

  .eyebrow {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 14px;
  }}

  h1 {{
    font-size: 21px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--ink);
    margin-bottom: 8px;
  }}

  .sub {{
    font-size: 14px;
    line-height: 1.55;
    color: var(--muted);
    margin-bottom: 30px;
  }}

  .field {{ text-align: left; margin-bottom: 14px; }}

  label {{
    display: block;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
  }}

  input[type="text"] {{
    width: 100%;
    padding: 13px 14px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 16px;
    letter-spacing: 0.1em;
    text-align: center;
    color: var(--ink);
    background: var(--bg-card);
    border: 1px solid var(--line);
    border-radius: 7px;
    outline: none;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }}

  input[type="text"]::placeholder {{ color: #b3b6bd; letter-spacing: normal; }}

  input[type="text"]:focus {{
    border-color: var(--green);
    box-shadow: 0 0 0 3px var(--green-tint);
  }}

  @keyframes shake {{
    10%, 90% {{ transform: translateX(-1px); }}
    20%, 80% {{ transform: translateX(2px); }}
    30%, 50%, 70% {{ transform: translateX(-4px); }}
    40%, 60% {{ transform: translateX(4px); }}
  }}

  input.shake {{ animation: shake 0.4s ease; border-color: var(--red); }}

  button {{
    width: 100%;
    margin-top: 6px;
    padding: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    background: var(--green);
    color: #ffffff;
    border: none;
    border-radius: 7px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s ease, transform 0.08s ease;
  }}

  button:hover:not(:disabled) {{ background: var(--green-dark); }}
  button:active:not(:disabled) {{ transform: scale(0.99); }}
  button:disabled {{ opacity: 0.65; cursor: not-allowed; }}

  button:focus-visible,
  .btn-outline:focus-visible {{
    outline: 2px solid var(--green);
    outline-offset: 2px;
  }}

  .spinner {{
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.35);
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }}

  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  .error {{
    min-height: 18px;
    font-size: 13px;
    color: var(--red);
    margin-top: 12px;
    text-align: center;
  }}

  .result img {{
    width: 100%;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #ffffff;
    animation: fade-in 0.35s ease;
  }}

  @keyframes fade-in {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  .btn-outline {{
    display: inline-block;
    margin-top: 16px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    color: var(--ink);
    border: 1px solid var(--ink);
    border-radius: 7px;
    text-decoration: none;
    transition: background 0.15s ease, color 0.15s ease;
  }}

  .btn-outline:hover {{ background: var(--ink); color: #ffffff; }}

  .footnote {{
    margin-top: 28px;
    font-size: 12px;
    line-height: 1.5;
    color: var(--muted);
  }}

  @media (max-width: 460px) {{
    .card {{ padding: 32px 24px; }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; transition: none !important; }}
  }}
</style>
</head>
<body>
  <main class="card">
    <div class="icon-wrap">
      <svg id="lockIcon" class="lock-icon" viewBox="0 0 48 48" aria-hidden="true">
        <rect x="12" y="22" width="24" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="2.5"/>
        <g class="shackle">
          <path d="M17 22 V15 a7 7 0 0 1 14 0 V22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </g>
        <circle cx="24" cy="31" r="1.6" fill="currentColor"/>
      </svg>
    </div>

    <p class="eyebrow" id="eyebrow">Secure file</p>
    <h1 id="title">Encrypted Biometric File</h1>
    <p class="sub" id="sub">File: <b>{title_name}</b><br>Locked with AES-256-GCM. Enter PIN to decrypt.</p>

    <div id="unlockSection">
      <div class="field">
        <label for="pinInput">Access PIN</label>
        <input type="text" id="pinInput" placeholder="XXXX-XXXX" maxlength="12" autocomplete="off" autocapitalize="off" spellcheck="false" autofocus>
      </div>

      <button type="button" id="unlockBtn">
        <span class="spinner" id="spinner" hidden></span>
        <span id="btnLabel">Unlock file</span>
      </button>

      <p class="error" id="errorMsg" role="alert"></p>
    </div>

    <div class="result" id="resultSection" hidden>
      <img id="decryptedImg" alt="Decrypted biometric image">
      <br>
      <a id="downloadLink" class="btn-outline" download="{title_name}_decrypted.png">Save image</a>
    </div>

    <p class="footnote">Decryption happens in your browser. The file is never uploaded anywhere.</p>
  </main>

  <script>
    const SALT_HEX = "{salt_hex}";
    const NONCE_HEX = "{nonce_hex}";
    const CIPHERTEXT_B64 = "{ciphertext_b64}";

    function hexToBytes(hex) {{
      const bytes = new Uint8Array(hex.length / 2);
      for (let i = 0; i < hex.length; i += 2) {{
        bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
      }}
      return bytes;
    }}

    function base64ToBytes(b64) {{
      const binStr = atob(b64);
      const bytes = new Uint8Array(binStr.length);
      for (let i = 0; i < binStr.length; i++) {{
        bytes[i] = binStr.charCodeAt(i);
      }}
      return bytes;
    }}

    const pinInput = document.getElementById('pinInput');
    const errorMsg = document.getElementById('errorMsg');
    const unlockBtn = document.getElementById('unlockBtn');
    const btnLabel = document.getElementById('btnLabel');
    const spinner = document.getElementById('spinner');
    const lockIcon = document.getElementById('lockIcon');
    const eyebrow = document.getElementById('eyebrow');
    const title = document.getElementById('title');
    const sub = document.getElementById('sub');
    const unlockSection = document.getElementById('unlockSection');
    const resultSection = document.getElementById('resultSection');
    const decryptedImg = document.getElementById('decryptedImg');
    const downloadLink = document.getElementById('downloadLink');

    pinInput.addEventListener('keyup', function (e) {{
      if (e.key === 'Enter') attemptUnlock();
    }});

    pinInput.addEventListener('input', function () {{
      errorMsg.textContent = '';
      pinInput.classList.remove('shake');
    }});

    unlockBtn.addEventListener('click', attemptUnlock);

    function setLoading(isLoading) {{
      unlockBtn.disabled = isLoading;
      spinner.hidden = !isLoading;
      btnLabel.textContent = isLoading ? 'Decrypting...' : 'Unlock file';
    }}

    function showError(msg) {{
      errorMsg.textContent = msg;
      pinInput.classList.remove('shake');
      void pinInput.offsetWidth;
      pinInput.classList.add('shake');
    }}

    async function attemptUnlock() {{
      const pinRaw = pinInput.value.trim();
      const cleanPin = pinRaw.replace(/[^0-9a-zA-Z]/g, '');

      if (!cleanPin) {{
        showError('Enter the access PIN to continue.');
        return;
      }}

      setLoading(true);

      try {{
        const enc = new TextEncoder();
        const pinData = enc.encode(cleanPin);

        const baseKey = await window.crypto.subtle.importKey(
          "raw", pinData, {{ name: "PBKDF2" }}, false, ["deriveKey"]
        );

        const saltBytes = hexToBytes(SALT_HEX);
        const aesKey = await window.crypto.subtle.deriveKey(
          {{
            name: "PBKDF2",
            salt: saltBytes,
            iterations: 600000,
            hash: "SHA-256"
          }},
          baseKey,
          {{ name: "AES-GCM", length: 256 }},
          false,
          ["decrypt"]
        );

        const nonceBytes = hexToBytes(NONCE_HEX);
        const cipherBytes = base64ToBytes(CIPHERTEXT_B64);

        const decryptedBuffer = await window.crypto.subtle.decrypt(
          {{ name: "AES-GCM", iv: nonceBytes }},
          aesKey,
          cipherBytes
        );

        const blob = new Blob([decryptedBuffer], {{ type: "image/png" }});
        const imgUrl = URL.createObjectURL(blob);

        decryptedImg.src = imgUrl;
        downloadLink.href = imgUrl;

        setLoading(false);
        unlockSection.hidden = true;
        resultSection.hidden = false;
        lockIcon.classList.add('unlocked');
        eyebrow.textContent = 'Unlocked';
        title.textContent = 'File decrypted';
        sub.textContent = 'The PIN matched. This image exists only in your browser.';
      }} catch (err) {{
        console.error(err);
        setLoading(false);
        showError('Wrong PIN, or the file was altered.');
      }}
    }}
  </script>
</body>
</html>"""
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

def secure_export_vault(image_array, base_output_path, title_name=None, custom_pin=None):
    """
    Encrypts image and exports .vault, .html, and _PIN.txt files.
    """
    pin, vault_bytes, salt_hex, nonce_hex, ciphertext_b64 = encrypt_image_data(image_array, custom_pin)
    
    vault_file_path = f"{base_output_path}.vault"
    html_file_path = f"{base_output_path}_secure.html"
    
    if title_name is None:
        title_name = os.path.basename(base_output_path)

    with open(vault_file_path, "wb") as f:
        f.write(vault_bytes)

    create_standalone_html_vault(html_file_path, title_name, salt_hex, nonce_hex, ciphertext_b64)

    pin_file_path = f"{base_output_path}_PIN.txt"
    clean_numeric_pin = re.sub(r'[^0-9a-zA-Z]', '', str(pin))
    pin_content = f"""======================================================================
 ENCRYPTED BIOMETRIC FILE ACCESS KEY
======================================================================
 Target Vault File : {os.path.basename(vault_file_path)}
 Web HTML Viewer   : {os.path.basename(html_file_path)}

 [KEY] SECRET ACCESS PIN : {pin}

 (You can type the PIN with or without dashes: {clean_numeric_pin})
======================================================================
"""
    with open(pin_file_path, "w", encoding="utf-8") as f:
        f.write(pin_content)

    return pin, vault_file_path, html_file_path, pin_file_path

