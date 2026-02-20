from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ImageCache:
    base_dir: str

    def _path_for_key(self, key: str) -> str:
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()  # nosec
        subdir = os.path.join(self.base_dir, "images", digest[:2])
        os.makedirs(subdir, exist_ok=True)
        return os.path.join(subdir, f"{digest}.bin")

    def get(self, key: str) -> bytes | None:
        path = self._path_for_key(key)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def set(self, key: str, data: bytes) -> None:
        path = self._path_for_key(key)
        with open(path, "wb") as f:
            f.write(data)
