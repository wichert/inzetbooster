import os
import httpx
from .inzetrooster import Inzetrooster


def main():
    with httpx.Client(follow_redirects=True) as client:
        ir = Inzetrooster(client, os.environ.get("ORGANIZATION", "rvliethorp"))
        ir.login(os.environ["USERNAME"], os.environ["PASSWORD"])
        ir.export_shifts()


if __name__ == "__main__":
    main()
