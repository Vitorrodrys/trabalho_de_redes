import logging

from core import init_logging, session_settings
from session_handler.listen_connections import listen_connections

init_logging()

logging.info(
    "at most package loss percentage was set as %f", session_settings.at_most_loss_percentage
)

def main():
    listen_connections()


if __name__ == "__main__":
    main()
