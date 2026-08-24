<div align="center">

<img src="Assets/Logo Used/AES256GCM_CodeMorph .jpeg" alt="AES256GCM_CodeMorph Logo" width=""/>

# AES256GCM_CodeMorph

<b> ``` Biometric Fingerprint Enhancement and Segmentation Using an AES-256-GCM Cryptographic Vault. ``` </b>

**AES256GCM_CodeMorph** is an end-to-end biometric processing and security suite that enhances raw fingerprint images into standardized square templates and encrypts them using **AES-256-GCM** with **PBKDF2-HMAC-SHA256 (600k rounds)** key derivation.

</div>

---

## Key Features

- **Computer Vision Pipeline (`testing.py`)**: Automatic polarity detection, CLAHE contrast enhancement, bilateral ridge filtering, texture variance ROI segmentation, and clean square box formatting.
- **Dual Outputs**: Generates a clean binary template `(a)` (black ridges on white canvas) and an enhanced grayscale template `(b)`.
- **AES-256-GCM Cryptographic Vault (`crypto_vault.py`)**: Secures biometric templates into encrypted binary `.vault` packages and self-contained zero-install `.html` web vaults.
- **Standalone Decryptor (`unlock.py`)**: GUI and CLI tool to authenticate and view encrypted vaults offline.

---

## Processing Flow

1. **Input**: Load optical sensor image, photo, scan, or generate synthetic fingerprint.
2. **Enhance & Segment**: Normalize illumination, enhance contrast, segment ROI, and crop centered square template.
3. **Export & Encrypt**: Save templates `(a)` and `(b)`, derive 256-bit key via PBKDF2-HMAC-SHA256 from an 8-digit PIN, and generate `.vault`, `.html`, and `_PIN.txt` files.
4. **Decrypt**: View offline via `unlock.py` or double-click `.html` to open in any web browser.

---

## Quick Start

### 1. Installation

```bash
git clone https://github.com/hasheramin5-cyber/AES256GCM_CodeMorph.git
cd AES256GCM_CodeMorph
pip install opencv-python numpy cryptography
```

### 2. Process & Encrypt

```bash
# Interactive GUI file picker
python testing.py

# Direct file execution
python testing.py "Assets/fp -2.png"
```

Outputs generated in the same directory: `<name>(a).png`, `<name>(b).png`, `<name>(b).vault`, `<name>(b)_secure.html`, `<name>(b)_PIN.txt`.

### 3. Decrypt & View

- **Browser (Zero-Install)**: Double-click `<name>(b)_secure.html` in any web browser and enter the PIN.
- **Python Tool**: Run `python unlock.py` (or `python unlock.py "<name>(b).vault"`).

---

## Security

Secured using **AES-256-GCM** authenticated encryption (128-bit integrity tag) combined with **PBKDF2-HMAC-SHA256 (600,000 rounds)** key derivation. Browser decryption is executed entirely offline on the client side using the WebCrypto API (`crypto.subtle`).

---

## Author

**Hasher Amin**

<a href="https://LinkedIn.com/in/hasheramin">
  <img src="assets/Logo Used/LinkedIn.png" alt="LinkedIn Logo" width="40">
</a>
<a href="https://github.com/hasheramin5-cyber">
  <img src="assets/Logo Used/GitHub Black.png" alt="GitHub Logo" width="40">
</a>
<a href="https://X.com/hasheramin_code">
  <img src="assets/Logo Used/Twitter.png" alt="X(Twitter) Logo" width="40">
</a>