import threading
import time
import difflib

import mss
import numpy as np
import cv2
import pytesseract
import pyautogui
import os
from pathlib import Path

from .ocr_processor     import OCRProcessor
from .template_matching import TemplateMatcher

class ScreenMonitorService(threading.Thread):
    """
    Continuously captures a screen region in a background thread.
    Exposes methods to find text via OCR, match image templates,
    click coordinates, and send paste hotkeys.
    """

    def __init__(self, region=None, ocr_confidence=50, template_dir=None):
        super().__init__(daemon=True)
        self.region   = region or self._detect_fullscreen_region()
        self.ocr      = OCRProcessor(confidence=ocr_confidence)
        self.matcher  = TemplateMatcher(template_dir=template_dir)
        self.running  = False
        self.latest   = None
        self._ready   = threading.Event()
        # Debug controls
        self.debug    = False
        self.debug_dir = None

    def _detect_fullscreen_region(self):
        with mss.mss() as sct:
            return sct.monitors[0]

    def run(self):
        self.running = True
        with mss.mss() as sct:
            while self.running:
                frame = np.array(sct.grab(self.region))
                # mss returns BGRA. Store as-is; downstream will convert as needed.
                self.latest = frame
                # Signal readiness after first frame
                if not self._ready.is_set():
                    self._ready.set()
                time.sleep(0.1)     

    def stop(self):
        self.running = False

    def set_debug(self, enabled: bool = True, save_dir: str | None = None):
        """
        Enable or disable debug overlay and console logs. When enabled, OCR
        candidates and annotated screenshots are saved on each find_text call.
        save_dir defaults to <project_root>/Data/ScreenDebug
        """
        self.debug = bool(enabled)
        if save_dir:
            self.debug_dir = save_dir
        else:
            # Resolve project root 3 levels up: .../Backend/AUTOMATION/screen_monitor/ -> project root
            project_root = Path(__file__).resolve().parents[3]
            self.debug_dir = str(project_root / "Data" / "ScreenDebug")
        if self.debug:
            os.makedirs(self.debug_dir, exist_ok=True)

    def capture(self):
        """
        Return the most recent frame as a BGR numpy array.
        """
        # Wait briefly for the first frame if not ready yet
        if self.latest is None:
            self._ready.wait(timeout=1.0)
        return self.latest

    def wait_until_ready(self, timeout: float = 2.0) -> bool:
        """
        Block until at least one frame has been captured or timeout occurs.
        Returns True if ready, False on timeout.
        """
        return self._ready.wait(timeout=timeout)

    def find_text(self, query: str, threshold: float = 0.75):
        """
        OCR entire frame, fuzzy-match `query` against each text box.
        Returns the center coords of the best match if above threshold.
        """
        img = self.capture()
        if img is None:
            return None

        # Ensure we pass a compatible image for OCR
        if img.ndim == 3 and img.shape[2] == 4:
            proc_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            proc_img = img

        boxes = self.ocr.ocr_image(proc_img)

        # Aggregate boxes into approximate text lines to support multi-word titles
        lines = []
        for b in sorted(boxes, key=lambda x: x['top']):
            placed = False
            for ln in lines:
                # Consider same line if vertical overlap is significant
                ln_mid = ln['top'] + ln['height'] / 2
                b_mid  = b['top'] + b['height'] / 2
                if abs(ln_mid - b_mid) <= max(10, 0.6 * max(ln['height'], b['height'])):
                    # Append word to this line
                    if b['left'] < ln['left']:
                        ln['text'] = f"{b['text']} " + ln['text']
                        ln['width'] = (ln['left'] + ln['width']) - b['left']
                        ln['left']  = b['left']
                    else:
                        ln['text'] = ln['text'] + f" {b['text']}"
                        ln['width'] = max(ln['left'] + ln['width'], b['left'] + b['width']) - ln['left']
                    ln['top']    = min(ln['top'], b['top'])
                    ln['height'] = max(ln['height'], b['height'])
                    # Track constituent words with boxes (left-ordered)
                    ln.setdefault('words', []).append({
                        'text': b['text'],
                        'left': b['left'],
                        'top': b['top'],
                        'width': b['width'],
                        'height': b['height'],
                    })
                    placed = True
                    break
            if not placed:
                lines.append({
                    'text': b['text'],
                    'left': b['left'],
                    'top': b['top'],
                    'width': b['width'],
                    'height': b['height'],
                    'words': [{
                        'text': b['text'],
                        'left': b['left'],
                        'top': b['top'],
                        'width': b['width'],
                        'height': b['height'],
                    }]
                })

        candidates = boxes + lines  # try both words and reconstructed lines
        best, best_score = None, 0.0

        q = (query or "").lower().strip()
        q_tokens = [w for w in q.split() if len(w) >= 3]
        scored = []
        for b in candidates:
            t = b['text'].lower().strip()
            score = difflib.SequenceMatcher(None, t, q).ratio()
            if q in t:
                score = max(score, 0.90)
            # Token overlap bonus for multi-word queries
            if q_tokens:
                overlap = sum(1 for w in q_tokens if w in t)
                score = max(score, overlap / max(1, len(q_tokens)))
            # Penalize extremely long lines to reduce misclick on merged UI strings
            try:
                line_width = b.get('width', 0)
                img_w = proc_img.shape[1]
                if line_width and img_w and line_width > 0.8 * img_w:
                    score *= 0.9
            except Exception:
                pass
            scored.append((score, b))
            if score > best_score:
                best_score, best = score, b

        # Slightly lower default threshold to 0.65 to accommodate OCR noise
        eff_threshold = min(threshold, 0.65)
        # Debug prints and overlay save
        if self.debug:
            top = sorted(scored, key=lambda x: x[0], reverse=True)[:10]
            print("[ScreenMonitor] OCR candidates for query:", q)
            for i, (s, b) in enumerate(top, 1):
                print(f"  {i:02d}. score={s:.3f} text='{b['text']}' box=({b['left']},{b['top']},{b['width']},{b['height']})")
            try:
                dbg_img = proc_img.copy()
                # Draw top candidates
                for (s, b) in top:
                    color = (0, 255, 255)
                    cv2.rectangle(dbg_img, (b['left'], b['top']), (b['left']+b['width'], b['top']+b['height']), color, 2)
                    cv2.putText(dbg_img, f"{s:.2f}", (b['left'], max(0, b['top']-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
                # Highlight best in green if exists
                if best is not None:
                    cv2.rectangle(dbg_img, (best['left'], best['top']), (best['left']+best['width'], best['top']+best['height']), (0,255,0), 2)
                ts = int(time.time()*1000)
                out_path = os.path.join(self.debug_dir or ".", f"ocr_debug_{ts}.png")
                cv2.imwrite(out_path, dbg_img)
                print(f"[ScreenMonitor] Saved OCR debug image to: {out_path}")
            except Exception as e:
                print(f"[ScreenMonitor] Failed to save OCR debug image: {e}")

        if best and best_score >= eff_threshold:
            # If best is a line and we have words, attempt to click the subspan covering matched tokens
            cx = best['left'] + best['width']  // 2
            cy = best['top']  + best['height'] // 2
            if best.get('words') and q_tokens:
                # Find words that appear in query tokens
                matched_words = [w for w in best['words'] if any(tok in w['text'].lower() for tok in q_tokens)]
                if matched_words:
                    min_left = min(w['left'] for w in matched_words)
                    max_right = max(w['left'] + w['width'] for w in matched_words)
                    min_top = min(w['top'] for w in matched_words)
                    max_bottom = max(w['top'] + w['height'] for w in matched_words)
                    cx = (min_left + max_right) // 2
                    cy = (min_top + max_bottom) // 2
            # Convert to absolute screen coordinates using region offset
            off_x = int(self.region.get('left', 0)) if isinstance(self.region, dict) else 0
            off_y = int(self.region.get('top', 0))  if isinstance(self.region, dict) else 0
            return {'x': cx + off_x, 'y': cy + off_y, 'text': best['text']}

        return None

    def match_template(self, name: str, threshold: float = 0.8):
        """
        Run template matching on the latest frame.
        `name` is the filename under screen_monitor/templates/.
        Returns center coords and match score.
        """
        img = self.capture()
        if img is None:
            return None

        # Convert to BGR if BGRA to match common template formats
        if img.ndim == 3 and img.shape[2] == 4:
            proc_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            proc_img = img

        result = self.matcher.match(proc_img, name, threshold=threshold)
        if result:
            off_x = int(self.region.get('left', 0)) if isinstance(self.region, dict) else 0
            off_y = int(self.region.get('top', 0))  if isinstance(self.region, dict) else 0
            result['x'] += off_x
            result['y'] += off_y
        return result

    def match_template_near(self, name: str, center_x: int, center_y: int, search_radius: int = 400, threshold: float = 0.8):
        """
        Run template matching but only within a square region around (center_x, center_y).
        This improves reliability for small UI icons like the three-dot menu on a tile.
        Returns absolute screen coords and match score if found, else None.
        """
        img = self.capture()
        if img is None:
            return None

        # Convert to BGR if BGRA to match common template formats
        if img.ndim == 3 and img.shape[2] == 4:
            proc_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            proc_img = img

        h, w = proc_img.shape[:2]
        x1 = max(0, center_x - search_radius)
        y1 = max(0, center_y - search_radius)
        x2 = min(w, center_x + search_radius)
        y2 = min(h, center_y + search_radius)

        roi = proc_img[y1:y2, x1:x2]
        if roi.size == 0:
            return None

        local = self.matcher.match(roi, name, threshold=threshold)
        if not local:
            return None

        off_x = int(self.region.get('left', 0)) if isinstance(self.region, dict) else 0
        off_y = int(self.region.get('top', 0))  if isinstance(self.region, dict) else 0

        # Translate local coords back to absolute
        local['x'] += x1 + off_x
        local['y'] += y1 + off_y
        return local

    def click_at(self, x: int, y: int):
        """
        Move mouse and click at absolute screen coordinates.
        """
        pyautogui.click(x, y)

    def paste(self):
        """
        Send Ctrl+V to current focused field.
        """
        pyautogui.hotkey('ctrl', 'v')