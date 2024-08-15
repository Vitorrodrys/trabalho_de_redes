from core import init_logging
from session_handler.listen_connections import listen_connections

init_logging()


def main():
    listen_connections()


if __name__ == "__main__":
    main()
