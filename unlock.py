"""
Standalone AES-256 Decryptor & Viewer for Encrypted Biometric Vaults
--------------------------------------------------------------------
Usage:
  python unlock.py                          -> Opens file picker to select .vault file
  python unlock.py path/to/image(b).vault   -> Opens the specified vault file
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import getpass
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import numpy as np
import cv2

import re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC_HEADER = b"FPVAULT1"

def decrypt_vault_file(vault_path, pin_string):
    """
    Decrypts an AES-256-GCM encrypted .vault biometric file.
    Returns: numpy image array (BGR)
    """
    with open(vault_path, "rb") as f:
        data = f.read()

    if not data.startswith(MAGIC_HEADER):
        raise ValueError("Invalid file format! This is not an authentic encrypted vault.")

    offset = len(MAGIC_HEADER)
    salt = data[offset : offset + 16]
    offset += 16
    nonce = data[offset : offset + 12]
    offset += 12
    ciphertext = data[offset:]

    clean_pin = re.sub(r'[^0-9a-zA-Z]', '', str(pin_string).strip())
    if not clean_pin:
        raise ValueError("PIN cannot be empty.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000
    )
    derived_key = kdf.derive(clean_pin.encode("utf-8"))
    
    aesgcm = AESGCM(derived_key)
    try:
        decrypted_png_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Decryption failed! Incorrect PIN or file has been tampered with.")

    img_array = np.frombuffer(decrypted_png_bytes, dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to parse decrypted image data.")

    return image

def main():
    print("\n" + "="*65)
    print(" [VAULT DECRYPTOR] BIOMETRIC AES-256-GCM UNLOCKER ")
    print("="*65)

    vault_path = None
    if len(sys.argv) > 1:
        vault_path = sys.argv[1].strip().strip('"').strip("'")
    else:
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            try:
                vault_path = filedialog.askopenfilename(
                    title="Select Encrypted Biometric Vault (.vault)",
                    filetypes=[("Vault files", "*.vault"), ("All files", "*.*")]
                )
            finally:
                root.destroy()
        except Exception:
            vault_path = ""

    if not vault_path or not os.path.exists(vault_path):
        if not vault_path:
            vault_path = input("Enter path to .vault file: ").strip().strip('"').strip("'")
        if not vault_path or not os.path.exists(vault_path):
            print("[ERROR] No valid .vault file selected. Exiting.")
            sys.exit(1)

    print(f"[INFO] Target Vault: {vault_path}")

    pin = ""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        try:
            res_pin = simpledialog.askstring(
                "Enter Security PIN",
                f"Enter the Secret PIN to unlock:\n{os.path.basename(vault_path)}",
                show="*"
            )
            if res_pin:
                pin = res_pin.strip()
        finally:
            root.destroy()
    except Exception:
        pass

    if not pin:
        pin = input("Enter Secret PIN: ").strip()

    if not pin:
        print("[ERROR] No PIN entered. Operation aborted.")
        sys.exit(1)

    print("[INFO] Deriving cryptographic key (600,000 PBKDF2 iterations)...")
    try:
        decrypted_img = decrypt_vault_file(vault_path, pin)
        print("[SUCCESS] Vault successfully unlocked and authenticated with AES-256-GCM!")
    except Exception as e:
        print(f"\n[AUTHENTICATION FAILED] {e}")
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            try:
                messagebox.showerror("Access Denied", str(e))
            finally:
                root.destroy()
        except Exception:
            pass
        sys.exit(1)

    base_name = os.path.splitext(vault_path)[0]
    out_extracted_path = f"{base_name}_decrypted.png"

    print(f"\n[ACTIONS]:")
    print(f" - Press [S] on preview window to export decrypted PNG -> {os.path.basename(out_extracted_path)}")
    print(f" - Press [Q] or [ESC] to exit")

    window_name = f"UNLOCKED VAULT: {os.path.basename(vault_path)}"
    
    disp_h = 600
    disp_w = int(decrypted_img.shape[1] * (disp_h / decrypted_img.shape[0]))
    disp_img = cv2.resize(decrypted_img, (disp_w, disp_h), interpolation=cv2.INTER_AREA).copy()
    
    cv2.putText(disp_img, "AES-256 Authenticated", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
    cv2.imshow(window_name, disp_img)

    while True:
        key = cv2.waitKey(100) & 0xFF
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
        if key in [ord('q'), ord('Q'), 27]:
            break
        elif key in [ord('s'), ord('S')]:
            cv2.imwrite(out_extracted_path, decrypted_img)
            print(f"[SUCCESS] Exported decrypted image to: {out_extracted_path}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
