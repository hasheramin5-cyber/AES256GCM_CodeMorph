# AES256GCM_CodeMorph

> **High-Fidelity Biometric Fingerprint Enhancement, Morphological Segmentation & Military-Grade AES-256-GCM Cryptographic Vault.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Cryptography](https://img.shields.io/badge/Security-AES--256--GCM-00B4D8?style=for-the-badge&logo=target&logoColor=white)](https://cryptography.io/)
[![PBKDF2](https://img.shields.io/badge/KDF-PBKDF2--HMAC--SHA256%20(600k%20rounds)-2B9348?style=for-the-badge)](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
[![WebCrypto](https://img.shields.io/badge/Zero--Install-HTML5%20WebCrypto-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

## Overview

**AES256GCM_CodeMorph** is an end-to-end biometric processing and security suite designed to solve two core challenges:
1. **Biometric Normalization & Enhancement**: Transforming raw, noisy, unevenly-lit fingerprint images (from sensors, scanners, or smartphone cameras) into standardized, centered square templates with crisp black ridges on a pure white background.
2. **Zero-Knowledge Authenticated Biometric Vaulting**: Securing sensitive biometric templates using **AES-256-GCM (Galois/Counter Mode)** authenticated encryption combined with **600,000 iterations of PBKDF2-HMAC-SHA256**, exporting both native binary containers (`.vault`) and standalone, zero-install WebCrypto HTML files (`.html`) decryptable offline in any modern web browser.

---

## Key Features

### 1. Advanced Computer Vision Pipeline (`testing.py`)
- **Dynamic Illumination Normalization**: Eliminates flashlight hot-spots, uneven shadows, and paper lighting gradients using morphological background estimation.
- **Smart Sensor Auto-Inversion**: Automatically detects inverted sensor captures (light ridges on dark backgrounds) and normalizes polarity.
- **CLAHE Contrast Enhancement**: Enhances fine ridge clarity using Contrast Limited Adaptive Histogram Equalization.
- **Bilateral Edge-Preserving Denoising**: Smooths surface noise while preserving critical minutiae, ridge endings, and bifurcations.
- **Texture Variance ROI Segmentation**: Isolates the fingerprint Region of Interest (ROI) via local statistical variance, eliminating background artifacts and borders.
- **Clean Square Box Extraction**: Automatically crops the detected fingerprint convex hull and centers it on a pure white ($255$) padded square canvas.
- **Dual Template Generation**:
  - `(a)` **Clean Binary Square**: High-contrast, binarized black ridges ($0$) on pure white ($255$).
  - `(b)` **Enhanced Grayscale Square**: High-fidelity CLAHE-enhanced grayscale template.
- **Built-in Synthetic Fingerprint Generator**: Generates realistic high-resolution synthetic fingerprint patterns for testing without requiring external datasets.

### 2. Military-Grade Cryptographic Vault (`crypto_vault.py`)
- **Authenticated Encryption (AEAD)**: Uses **AES-256-GCM** with a 12-byte cryptographically secure random nonce (`secrets.token_bytes(12)`) and a 128-bit integrity authentication tag.
- **OWASP-Standard Key Derivation**: Derives 256-bit encryption keys from user PINs using **PBKDF2-HMAC-SHA256 with 600,000 rounds** and a 16-byte random cryptographic salt.
- **High-Entropy PIN Generator**: Generates 8-digit randomized PIN keys formatted as `XXXX-XXXX`.
- **Zero-Knowledge Standalone HTML Vault**: Generates self-contained, responsive HTML files that decrypt client-side using the hardware-accelerated **WebCrypto API** (`crypto.subtle`) without internet access or server dependencies.
- **Tamper Resistance**: Any alteration or bit-flip in the ciphertext immediately fails GCM tag authentication, preventing unauthorized tampering.

### 3. Standalone Decryptor & Viewer (`unlock.py`)
- **Native GUI & CLI Support**: Features interactive Tkinter file dialogs and PIN prompts, with fallback to terminal input and command-line arguments.
- **Instant Preview & Export**: Displays authenticated decrypted biometric templates in an OpenCV viewer with direct one-key export (`[S]` key).

---

## Architecture and Pipeline

```text
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                            INPUT FINGERPRINT                              │
 │            (Optical Sensor / Smartphone Photo / Flatbed Scan)            │
 └─────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                   IMAGE ENHANCEMENT & NORMALIZATION                       │
 │  1. Polarity Detection (Auto-Invert Light-on-Dark)                        │
 │  2. Background Illumination Flattening (Morphological Division)           │
 │  3. CLAHE Local Contrast Enhancement + Bilateral Ridge Filtering          │
 │  4. Texture Variance ROI Masking & Convex Hull Extraction                 │
 │  5. Centered Square-Box Canvas Generation with Pure White Padded Bounds   │
 └───────────────────┬───────────────────────────────────┬───────────────────┘
                     │                                   │
                     ▼                                   ▼
        ┌─────────────────────────┐         ┌─────────────────────────┐
        │  TEMPLATE (a): BINARY   │         │ TEMPLATE (b): ENHANCED  │
        │ Clean Black Ridges (0)  │         │ CLAHE Grayscale Matrix  │
        │ Pure White Canvas (255) │         └────────────┬────────────┘
        └─────────────────────────┘                      │
                                                         ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                      AES-256-GCM CRYPTO ENGINE                            │
 │  1. Secrets Module generates 8-digit PIN [XXXX-XXXX]                      │
 │  2. PBKDF2-HMAC-SHA256 Key Derivation (600,000 Iterations + 16-byte Salt) │
 │  3. AES-256-GCM Authenticated Encryption (12-byte Nonce + 128-bit Tag)    │
 └───────────────────┬───────────────────────────────────┬───────────────────┘
                     │                                   │
                     ▼                                   ▼
        ┌─────────────────────────┐         ┌─────────────────────────┐
        │   BINARY VAULT (.vault) │         │  WEB VAULT (.html)      │
        │ Magic Header: FPVAULT1  │         │ Self-Contained WebCrypto│
        │ Salt + Nonce + Cipher   │         │ Zero-Install Universal  │
        └────────────┬────────────┘         │ Decryption in Browser   │
                     │                      └─────────────────────────┘
                     ▼
        ┌─────────────────────────┐
        │   UNLOCKER (unlock.py)  │
        │ GUI / CLI Decryptor &   │
        │ Authenticated Viewer    │
        └─────────────────────────┘
```

---

## Repository Structure

```text
AES256GCM_CodeMorph/
├── Assets/
│   └── fp -2.png           # Sample fingerprint image asset for testing
├── crypto_vault.py         # Core AES-256-GCM encryption & HTML generator module
├── testing.py              # Main enhancement, segmentation & processing pipeline
├── unlock.py               # GUI & CLI decryptor / viewer for .vault files
├── .gitignore              # Git ignore configuration
└── README.md               # Project documentation
```

---

## Output Files Specification

When you process an image (e.g., `sample.png`), the pipeline automatically generates 5 synchronized artifacts in the same folder:

| File Pattern | Type | Description |
| :--- | :--- | :--- |
| `<name>(a).png` | **Image** | Clean square binary template ($0 = \text{black ridges}, 255 = \text{white background}$). |
| `<name>(b).png` | **Image** | Clean square CLAHE-enhanced grayscale template. |
| `<name>(b).vault` | **Binary Container** | Encrypted binary vault package (`FPVAULT1` header + Salt + Nonce + AES-GCM Ciphertext). |
| `<name>(b)_secure.html` | **Web App** | Self-contained, responsive HTML5 viewer with WebCrypto client-side decryption. |
| `<name>(b)_PIN.txt` | **Key Record** | Generated secret access PIN record for reference and secure sharing. |

---

## Quick Start

### 1. Prerequisites & Installation

Ensure you have **Python 3.8+** installed. Clone the repository and install dependencies:

```bash
# Clone repository
git clone https://github.com/hasheramin5-cyber/AES256GCM_CodeMorph.git
cd AES256GCM_CodeMorph

# Install required dependencies
pip install opencv-python numpy cryptography
```

> **Note**: `tkinter` is included with standard Python installations on Windows and macOS. On Linux (Ubuntu/Debian), install it via `sudo apt install python3-tk`.

---

### 2. Process & Encrypt Fingerprint Images

#### Option A: Interactive Mode (GUI File Picker)
Run the script without arguments to open a native file picker:
```bash
python testing.py
```
*(If no file is selected, the script will automatically generate and process a high-resolution synthetic fingerprint).*

#### Option B: Direct Path Execution (CLI)
Pass the target image directly:
```bash
python testing.py "Assets/fp -2.png"
```

#### Controls in the Preview Window:
- **`[Q]`** or **`[ESC]`** or clicking **`[X]`**: Close preview and exit.
- **`[S]`**: Re-save templates to disk.

---

### 3. Decrypt & View Encrypted Vaults

You have two versatile options to unlock and view the encrypted biometric template:

#### Method 1: Universal Web Decryption (Zero Installation)
1. Double-click the generated `<name>(b)_secure.html` file in any web browser (Chrome, Edge, Safari, Firefox, iOS, Android).
2. Enter the secret access PIN.
3. Decrypt and view the biometric template instantly (with an option to download the decrypted PNG).
4. *Zero internet connection needed — all computation executes locally on your device using WebCrypto.*

#### Method 2: Python GUI/CLI Decryptor
Run the native decryptor tool:
```bash
# Interactive GUI mode (Opens file picker)
python unlock.py

# Direct CLI mode
python unlock.py "Assets/fp -2(b).vault"
```

#### Controls in the Unlocked Window:
- **`[S]`**: Export decrypted biometric PNG image (`<name>_decrypted.png`).
- **`[Q]`** or **`[ESC]`**: Exit viewer.

---

## Security & Cryptographic Specifications

| Parameter | Specification | Details |
| :--- | :--- | :--- |
| **Cipher Algorithm** | `AES-256-GCM` | Authenticated Encryption with Associated Data (AEAD). |
| **Key Size** | `256 bits` (32 bytes) | Maximum AES key strength against quantum & brute-force attacks. |
| **Key Derivation Function** | `PBKDF2-HMAC-SHA256` | High-work-factor defense against GPU/ASIC dictionary attacks. |
| **KDF Iteration Count** | `600,000 rounds` | Complies with current **OWASP Password Storage Recommendations**. |
| **Salt Length** | `128 bits` (16 bytes) | Cryptographically secure random salt generated via OS entropy pool. |
| **Nonce / IV Length** | `96 bits` (12 bytes) | Unique, non-repeating initialization vector per encryption operation. |
| **Integrity Tag** | `128 bits` (16 bytes) | Galois authentication tag guaranteeing ciphertext authenticity. |
| **Magic Byte Identifier** | `b"FPVAULT1"` | 8-byte file format verification header. |
| **Web Crypto Standard** | `SubtleCrypto` | Hardware-accelerated browser-native cryptographic implementation. |

---

## Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](../../issues) if you want to contribute.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## Author

**Hasher Amin**
- GitHub: [@hasheramin5-cyber](https://github.com/hasheramin5-cyber)

If you find this project useful, please consider starring the repository. 