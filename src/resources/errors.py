class Interrupt(Exception):
    def __init__(self, exit_code: int = 0):
        self.exit_code = exit_code

    def __str__(self):
        return f"Interrupt with exit code {self.exit_code}"


class UnderiaError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"UnderiaError: {self.message}"
