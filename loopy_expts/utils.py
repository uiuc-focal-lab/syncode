import os


ACTION = "\033[95m"
INFO = "\033[94m"
SUCCESS = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
END = "\033[0m"


class Logger:
    """A helper class for logging messages to std output."""

    verbose = False
    debug = False

    @staticmethod
    def log_action(action: str, msg: str):
        Logger.log(
            f"{ACTION}{BOLD}[>]{END} {INFO}{BOLD}{action}{END}:{os.linesep}{msg}"
        )

    @staticmethod
    def log_info(msg: str):
        Logger.log(f"{ACTION}{BOLD}[>]{END} {INFO}{BOLD}{msg}{END}")

    @staticmethod
    def log_debug(msg: str):
        if Logger.debug:
            Logger.log(f"{WARNING}{BOLD}[Debug]{END} {msg}")

    @staticmethod
    def log_success(msg: str):
        Logger.log(f"{SUCCESS}{BOLD}[Success]{END} {msg}")

    @staticmethod
    def log_warning(msg: str):
        Logger.log(f"{WARNING}{BOLD}[Warning]{END} {msg}")

    @staticmethod
    def log_error(msg: str):
        Logger.log(f"{FAIL}{BOLD}[Error]{END} {msg}")

    @staticmethod
    def log_model_request(model: str, messages: list[dict[str, str]]):
        if Logger.debug:
            msg = (
                "\n".join(
                    [
                        f"{BOLD}{UNDERLINE}{SUCCESS}"
                        + message["role"]
                        + f":{END} "
                        + message["content"]
                        for message in messages
                    ]
                )
                + f"\n{INFO}"
                + ("==" * 30)
                + f"{END}"
            )
            Logger.log(
                f"{INFO}{BOLD}Sending prompt to the '{model}' model:{END}\n{msg}"
            )

    @staticmethod
    def log_model_response(model: str, completions: [str]):
        if Logger.debug:
            msg = "\n".join(
                [
                    f"{BOLD}{UNDERLINE}{SUCCESS}Completion "
                    + str(i + 1)
                    + f":{END}\n"
                    + str(completion)
                    for i, completion in enumerate(completions)
                ]
            )
            Logger.log(
                f"{SUCCESS}{BOLD}Received response from the '{model}' model:{END}\n{msg}"
            )

    @staticmethod
    def log(msg: str):
        print(msg)
