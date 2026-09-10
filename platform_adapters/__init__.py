from pathlib import Path

from .youtube import YouTubeAdapter
from .rumble import RumbleAdapter
from .bandcamp import BandcampAdapter
from .amaze import AmazeAdapter


def get_adapters(root):
    root = Path(root)

    return {
        "youtube": YouTubeAdapter(root),
        "rumble": RumbleAdapter(root),
        "bandcamp": BandcampAdapter(root),
        "amaze": AmazeAdapter(root),
    }
