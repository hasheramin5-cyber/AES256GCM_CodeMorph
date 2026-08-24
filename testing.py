"""
High-Quality Fingerprint Extractor & Square Box Formatter
--------------------------------------------------------
Input: Any high-quality fingerprint image (photo, scan, sensor capture).
Output: A clean square box with crisp black ridges (0) and pure white background (255).

Usage:
  python testing.py                   -> Opens file picker / prompt to select image
  python testing.py path/to/image.png -> Directly processes the given image
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def load_input_image(image_path=None):
    """
    Loads an image from path, opens a file dialog, or prompts the user.
    If no file is provided, generates a synthetic high-resolution sample.
    """
    if not image_path:
        if len(sys.argv) > 1:
            image_path = sys.argv[1].strip().strip('"').strip("'")
        else:
            try:
                # Try opening native file dialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                try:
                    image_path = filedialog.askopenfilename(
                        title="Select High-Quality Fingerprint Image",
                        filetypes=[
                            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp"),
                            ("All files", "*.*")
                        ]
                    )
                finally:
                    root.destroy()
            except Exception:
                image_path = ""

    if not image_path or not os.path.exists(image_path):
        if not image_path:
            image_path = input("Enter path to fingerprint image (or press Enter for sample test image): ").strip().strip('"').strip("'")
            
        if not image_path or not os.path.exists(image_path):
            print("[INFO] No input file provided. Generating a high-resolution synthetic fingerprint for testing...")
            return generate_sample_fingerprint(), "synthetic_sample.png"

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image from: {image_path}")
        
    print(f"[INFO] Successfully loaded image: {image_path} ({img.shape[1]}x{img.shape[0]} px)")
    return img, image_path

def generate_sample_fingerprint():
    """Generates a realistic high-resolution sample fingerprint for instant testing."""
    h, w = 650, 520
    img = np.full((h, w), 245, dtype=np.uint8)
    center = (260, 330)
    
    # Draw core and looping ridges
    for r in range(16, 230, 8):
        cv2.ellipse(img, center, (r, int(r * 1.35)), 25, 0, 360, 35, 3)
        cv2.ellipse(img, (center[0] + 12, center[1] - 18), (int(r * 0.85), int(r * 1.15)), 15, 0, 180, 45, 3)
        
    # Mask to natural fingerprint oval shape
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(mask, center, (190, 250), 12, 0, 360, 255, -1)
    
    # Add uneven paper lighting & slight noise
    bg = np.full((h, w), 235, dtype=np.uint8)
    fingerprint = np.where(mask == 255, img, bg)
    
    # Add gradient lighting (simulating camera / scanner lighting variations)
    x = np.linspace(-25, 25, w)
    y = np.linspace(-35, 35, h)
    xx, yy = np.meshgrid(x, y)
    gradient = (xx + yy).astype(np.int16)
    fingerprint = np.clip(fingerprint.astype(np.int16) + gradient, 0, 255).astype(np.uint8)
    
    # Add subtle texture noise
    noise = np.random.normal(0, 7, (h, w)).astype(np.int16)
    fingerprint = np.clip(fingerprint.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return cv2.cvtColor(fingerprint, cv2.COLOR_GRAY2BGR)

def enhance_and_segment_fingerprint(
    image,
    adaptive_block_size=17,
    adaptive_c=4,
    auto_invert=True
):
    """
    Processes the input image to extract sharp ridges on pure white background.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    h_img, w_img = gray.shape[:2]
    bw = max(1, min(10, h_img // 4, w_img // 4))

    border_mean = (np.mean(gray[:bw, :]) + np.mean(gray[-bw:, :]) + 
                   np.mean(gray[:, :bw]) + np.mean(gray[:, -bw:])) / 4.0
    center_mean = np.mean(gray[h_img//4: 3*h_img//4, w_img//4: 3*w_img//4])
    
    if auto_invert and border_mean < center_mean and border_mean < 80:
        gray = cv2.bitwise_not(gray)

    kernel_bg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
    bg_estimate = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel_bg)
    flat_gray = cv2.divide(gray, bg_estimate, scale=255)

    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(flat_gray)

    smoothed = cv2.bilateralFilter(enhanced, 7, 50, 50)

    blur = cv2.blur(smoothed.astype(np.float32), (15, 15))
    sq_blur = cv2.blur((smoothed.astype(np.float32)) ** 2, (15, 15))
    var = np.maximum(sq_blur - blur ** 2, 0)
    std = np.sqrt(var)
    std_norm = cv2.normalize(std, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    _, var_mask = cv2.threshold(std_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    mask_clean = cv2.morphologyEx(var_mask, cv2.MORPH_CLOSE, morph_kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, morph_kernel)

    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    roi_mask = np.zeros_like(gray)
    
    if contours:
        largest_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_cnt) > (gray.shape[0] * gray.shape[1] * 0.03):
            hull = cv2.convexHull(largest_cnt)
            cv2.drawContours(roi_mask, [hull], -1, 255, thickness=cv2.FILLED)
            bbox = cv2.boundingRect(hull)
        else:
            roi_mask[:] = 255
            bbox = (0, 0, gray.shape[1], gray.shape[0])
    else:
        roi_mask[:] = 255
        bbox = (0, 0, gray.shape[1], gray.shape[0])

    bs = adaptive_block_size if adaptive_block_size % 2 == 1 else adaptive_block_size + 1
    binary = cv2.adaptiveThreshold(
        smoothed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, bs, adaptive_c
    )

    binary_clean = cv2.medianBlur(binary, 3)
    binary_clean[roi_mask == 0] = 255

    enhanced_clean = enhanced.copy()
    enhanced_clean[roi_mask == 0] = 255

    return binary_clean, enhanced_clean, bbox

def make_clean_square_box(image_input, bbox, padding_ratio=0.12, target_size=None):
    """
    Crops the detected fingerprint and places it centered inside a clean square box.
    """
    x, y, w, h = bbox
    cx, cy = x + w // 2, y + h // 2
    
    max_dim = max(w, h)
    side = max(1, int(max_dim * (1.0 + padding_ratio)))
    half_side = side // 2

    if len(image_input.shape) == 3:
        square_box = np.full((side, side, image_input.shape[2]), 255, dtype=np.uint8)
    else:
        square_box = np.full((side, side), 255, dtype=np.uint8)

    src_x1 = cx - half_side
    src_y1 = cy - half_side
    src_x2 = src_x1 + side
    src_y2 = src_y1 + side

    img_x1 = max(0, src_x1)
    img_y1 = max(0, src_y1)
    img_x2 = min(image_input.shape[1], src_x2)
    img_y2 = min(image_input.shape[0], src_y2)

    crop_w = img_x2 - img_x1
    crop_h = img_y2 - img_y1

    pad_x1 = img_x1 - src_x1
    pad_y1 = img_y1 - src_y1
    pad_x2 = pad_x1 + crop_w
    pad_y2 = pad_y1 + crop_h

    if crop_w > 0 and crop_h > 0:
        square_box[pad_y1:pad_y2, pad_x1:pad_x2] = image_input[img_y1:img_y2, img_x1:img_x2]

    if target_size is not None:
        square_box = cv2.resize(square_box, (target_size, target_size), interpolation=cv2.INTER_AREA)

    return square_box

def process_and_save(image_path=None, target_size=None):
    """
    Main processing pipeline: loads image, enhances, crops square box, and encrypts output.
    """
    raw_img, filename = load_input_image(image_path)
    
    file_dir = os.path.dirname(os.path.abspath(filename))
    base_name, ext = os.path.splitext(os.path.basename(filename))
    
    out_ext = ext if ext.lower() in [".png", ".bmp", ".tif", ".tiff"] else ".png"
    out_filename_a = os.path.join(file_dir, f"{base_name}(a){out_ext}")
    out_filename_b = os.path.join(file_dir, f"{base_name}(b){out_ext}")
    
    print("\n" + "="*65)
    print(" FINGERPRINT EXTRACTION & CLEAN SQUARE GENERATOR ")
    print("="*65)
    print(f" Source Image : {filename}")
    
    binary_full, enhanced_clean, bbox = enhance_and_segment_fingerprint(raw_img)
    square_binary = make_clean_square_box(binary_full, bbox, padding_ratio=0.12, target_size=target_size)
    square_enhanced = make_clean_square_box(enhanced_clean, bbox, padding_ratio=0.12, target_size=target_size)
    
    cv2.imwrite(out_filename_a, square_binary)
    cv2.imwrite(out_filename_b, square_enhanced)
    
    print(f"[SUCCESS] Saved Template (a) [Binary Black/White]:")
    print(f" -> {out_filename_a}")
    print(f"[SUCCESS] Saved Template (b) [Enhanced Grayscale]:")
    print(f" -> {out_filename_b}")
    print(f" Output Dimensions : {square_binary.shape[1]}x{square_binary.shape[0]} px")
    print("="*65)
    
    from crypto_vault import secure_export_vault
    base_vault_path = os.path.join(file_dir, f"{base_name}(b)")
    pin, vault_path, html_path, pin_path = secure_export_vault(
        square_enhanced,
        base_vault_path,
        title_name=f"{base_name}(b)"
    )

    print("\n" + "="*70)
    print(" [SECURITY] AES-256-GCM ENCRYPTED BIOMETRIC VAULT ")
    print("="*70)
    print(f" Target Image   : {os.path.basename(out_filename_b)}")
    print(f" Encrypted Vault: {vault_path}")
    print(f" Web Vault      : {html_path}")
    print(f" PIN Key File   : {pin_path}")
    print("-"*70)
    print(f" [KEY] SECRET ACCESS PIN :  >>>  {pin}  <<<")
    print("-"*70)
    print(" Security Level: AES-256-GCM + 600,000 PBKDF2 Iterations")
    print("\n [HOW TO SHARE & OPEN]:")
    print(" 1. Send the file to your recipient:")
    print(f"    - Web HTML Vault:  {os.path.basename(html_path)} (Opens in ANY browser)")
    print(f"    - Or Binary Vault: {os.path.basename(vault_path)} (Open via 'python unlock.py')")
    print(f" 2. Send the PIN [{pin}] separately (via SMS, WhatsApp, Signal, etc.)")
    print("="*70 + "\n")
    
    return raw_img, square_enhanced, square_binary, out_filename_a, out_filename_b, vault_path, html_path, pin_path, pin

def main():
    raw_img, square_enhanced, square_binary, out_path_a, out_path_b, vault_path, html_path, pin_path, pin = process_and_save()

    print("\n" + "-"*65)
    print(" [FILES GENERATED IN THE SAME DIRECTORY]:")
    print(f" 1. (a) Binary Clean Square : {os.path.basename(out_path_a)}")
    print(f" 2. (b) Enhanced Grayscale  : {os.path.basename(out_path_b)}")
    print(f" 3. [VAULT] AES-256 Package : {os.path.basename(vault_path)}")
    print(f" 4. [WEB] Standalone HTML   : {os.path.basename(html_path)}")
    print(f" 5. [KEY] PIN Backup File   : {os.path.basename(pin_path)}")
    print(f"\n [KEY] UNLOCK PIN: {pin}")
    print("-"*65)
    print(" [CONTROLS]:")
    print(" - Click on the IMAGE PREVIEW WINDOW (not the terminal).")
    print(" - Press [Q] or [ESC] on your keyboard, or click [X] to exit.")
    print(" - Press [S] while focused on the image window to re-save.")
    print("-"*65 + "\n")

    disp_h = 512
    disp_w = int(raw_img.shape[1] * (disp_h / raw_img.shape[0]))
    
    orig_disp = cv2.resize(raw_img, (disp_w, disp_h))
    enh_disp = cv2.resize(square_enhanced, (disp_h, disp_h))
    if len(enh_disp.shape) == 2:
        enh_disp = cv2.cvtColor(enh_disp, cv2.COLOR_GRAY2BGR)
        
    sq_disp = cv2.resize(square_binary, (disp_h, disp_h))
    sq_disp = cv2.cvtColor(sq_disp, cv2.COLOR_GRAY2BGR)

    cv2.putText(orig_disp, "1. Original Input", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(enh_disp, "2. (b) Enhanced Square", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(sq_disp, "3. (a) Clean Binary Square", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    comparison_stack = np.hstack((orig_disp, enh_disp, sq_disp))
    window_name = "Fingerprint Processor: [Original | Enhanced | Clean Square Box]"

    cv2.imshow(window_name, comparison_stack)

    while True:
        key = cv2.waitKey(100) & 0xFF
        
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            print("[INFO] Preview window closed.")
            break
            
        if key in [ord('q'), ord('Q'), 27]:
            print("[INFO] Exiting application.")
            break
        elif key in [ord('s'), ord('S')]:
            cv2.imwrite(out_path_a, square_binary)
            cv2.imwrite(out_path_b, square_enhanced)
            print(f"[SUCCESS] Templates re-saved to disk.")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
