import os
import cv2
import numpy as np

class TemplateMatcher:
    """
    Caches small template images and runs OpenCV matchTemplate
    to find icons (e.g. YouTube’s three-dot menu).
    """

    def __init__(self, template_dir=None):
        base = os.path.dirname(__file__)
        self.template_dir = template_dir or os.path.join(base, "templates")
        self.cache = {}

    def _load(self, name):
        if name not in self.cache:
            path = os.path.join(self.template_dir, name)
            tpl  = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            self.cache[name] = tpl
        return self.cache.get(name)

    def match(self, img, name, threshold=0.8):
        tpl = self._load(name)
        if tpl is None:
            return None

        res = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            h, w = tpl.shape[:2]
            return {
                'x': int(max_loc[0] + w/2),
                'y': int(max_loc[1] + h/2),
                'score': float(max_val)
            }

        return None