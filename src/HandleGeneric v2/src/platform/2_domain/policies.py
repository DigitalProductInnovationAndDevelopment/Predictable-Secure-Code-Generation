from dataclasses import dataclass

@dataclass
class ValidationPolicy:
    fail_on_warning: bool = False
