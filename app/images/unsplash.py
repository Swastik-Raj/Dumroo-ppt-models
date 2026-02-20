from __future__ import annotations

import os
import random
import re
import time
from dataclasses import dataclass

import requests
from requests import RequestException

from app.images.cache import ImageCache


@dataclass(frozen=True)
class UnsplashImageSearch:
    access_key: str
    cache: ImageCache

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Client-ID {self.access_key}"}

    def get_photo(self, photo_id: str) -> dict | None:
        """Retrieve a single photo object: GET /photos/:id."""
        photo_id = (photo_id or "").strip()
        if not photo_id:
            return None

        url = f"https://api.unsplash.com/photos/{photo_id}"
        r = requests.get(url, headers=self._headers(), timeout=20)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            return None
        return data

    def get_photo_download_url(self, photo_id: str, *, size: str = "regular") -> str | None:
        """Return a hotlinkable image URL (e.g., urls.regular) for a given photo id.

        Note: Unsplash guidelines recommend calling download_location for tracking.
        This method will attempt that call but won't fail if it can't.
        """
        data = self.get_photo(photo_id)
        if not data:
            return None

        urls = data.get("urls") or {}
        if not isinstance(urls, dict):
            urls = {}

        preferred = None
        if size in ("raw", "full", "regular", "small", "thumb"):
            preferred = urls.get(size)

        image_url = preferred or urls.get("regular") or urls.get("full")
        if not image_url:
            return None

        # Best-effort tracking call.
        links = data.get("links") or {}
        download_location = None
        if isinstance(links, dict):
            download_location = links.get("download_location")

        if download_location:
            try:
                requests.get(download_location,
                             headers=self._headers(), timeout=10)
            except Exception:
                pass

        return str(image_url)

    def download_by_id(self, photo_id: str, *, size: str = "regular") -> bytes | None:
        url = self.get_photo_download_url(photo_id, size=size)
        if not url:
            return None
        try:
            return self.download(url)
        except Exception:
            return None

    def search_image_url(self, query: str) -> str | None:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": 20,
            "orientation": "landscape",
            "content_filter": "high",
        }
        headers = self._headers()

        last_err: Exception | None = None
        data = None
        for attempt in range(3):
            try:
                r = requests.get(url, params=params,
                                 headers=headers, timeout=20)
                r.raise_for_status()
                data = r.json()
                break
            except RequestException as e:
                last_err = e
                time.sleep(0.4 * (attempt + 1))
        if data is None:
            if self._debug() and last_err is not None:
                print(
                    f"[images] search request failed err={type(last_err).__name__}: {last_err}")
            return None

        results = data.get("results") or []
        candidates: list[str] = []
        for item in results:
            urls = item.get("urls") or {}
            # Prefer reasonably sized images.
            cand = urls.get("regular") or urls.get("full")
            if cand:
                candidates.append(cand)

        if not candidates:
            return None

        # Prefer the top result for relevance.
        return candidates[0]

    def _debug(self) -> bool:
        return (os.getenv("DEBUG_IMAGES", "").strip().lower() in {"1", "true", "yes", "on"})

    def _candidate_queries(self, query: str) -> list[str]:
        q = (query or "").strip()
        if not q:
            return []

        # Keep first as-is.
        candidates: list[str] = [q]

        # Simplify: lowercase tokens, drop punctuation, trim length.
        tokens = re.findall(r"[a-zA-Z]{3,}", q.lower())
        stop = {
            "deck",
            "slide",
            "presentation",
            "overview",
            "diagram",
            "labeled",
            "high",
            "quality",
            "illustration",
            "wide",
            "photo",
        }
        tokens = [t for t in tokens if t not in stop]

        # Preserve order & uniqueness.
        uniq: list[str] = []
        seen: set[str] = set()
        for t in tokens:
            if t in seen:
                continue
            seen.add(t)
            uniq.append(t)

        def add_terms(ts: list[str]) -> None:
            qq = " ".join(ts).strip()
            if qq and qq not in candidates:
                candidates.append(qq)

        add_terms(uniq[:6])
        add_terms(uniq[:4])
        add_terms(uniq[:3])

        # Heuristic fallbacks for common business/process topics.
        token_set = set(uniq)
        if {"onboarding", "signup", "sign", "registration", "account", "verify", "verification"} & token_set:
            add_terms(["business", "onboarding"])
            add_terms(["team", "onboarding"])
            add_terms(["office", "team"])
        if {"process", "workflow", "flow", "steps", "journey"} & token_set:
            add_terms(["business", "workflow"])
            add_terms(["workflow"])
            add_terms(["business", "process"])

        # Always end with a guaranteed broad query.
        add_terms(["abstract", "background"])
        return candidates

    def download(self, url: str) -> bytes:
        cached = self.cache.get(url)
        if cached is not None:
            return cached

        # Some CDNs are picky; send a generic UA.
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                r = requests.get(
                    url,
                    timeout=30,
                    headers={"User-Agent": "ppt-generator/1.0"},
                )
                r.raise_for_status()
                data = r.content
                break
            except RequestException as e:
                last_err = e
                time.sleep(0.4 * (attempt + 1))
        else:
            raise last_err or RuntimeError("Download failed")
        self.cache.set(url, data)
        return data

    def search_and_download(self, query: str) -> bytes | None:
        for q in self._candidate_queries(query):
            try:
                url = self.search_image_url(q)
            except Exception as e:
                if self._debug():
                    print(
                        f"[images] search failed q='{q[:80]}' err={type(e).__name__}: {e}")
                continue
            if not url:
                if self._debug():
                    print(f"[images] no results q='{q[:80]}'")
                continue
            try:
                data = self.download(url)
                if self._debug():
                    print(f"[images] ok q='{q[:80]}' bytes={len(data)}")
                return data
            except Exception as e:
                if self._debug():
                    print(
                        f"[images] download failed q='{q[:80]}' err={type(e).__name__}: {e}")
                continue
        return None
