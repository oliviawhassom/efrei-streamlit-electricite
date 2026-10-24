import os
import sys

# so the script works when launched from anywhere
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.io import download_file

if __name__ == "__main__":
    force = "--force" in sys.argv
    path = download_file(force=force)
    print("dataset is in", path, "(%.1f MB)" % (os.path.getsize(path) / 1e6))
