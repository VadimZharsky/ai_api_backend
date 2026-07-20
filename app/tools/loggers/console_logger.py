from enum import Enum
from typing import Any


class BcColors(Enum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class ConsoleLogger:
    @staticmethod
    def c_print(text: Any, color: BcColors = BcColors.ENDC) -> None:
        print(color.value + text + BcColors.ENDC.value)
