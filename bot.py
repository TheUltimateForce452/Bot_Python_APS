import logging

from app.app_factory import build_application


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def main() -> None:
    app = build_application()
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    main()