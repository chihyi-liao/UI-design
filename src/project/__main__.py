import sys

from .cli import app


def main():
    app.entrypoint()


if __name__ == "__main__":
    sys.exit(main())
