from dataclasses import dataclass
import uuid


@dataclass
class LinkDTO:
    name: str
    url: str
    category: str
    id: str = None

    def __post_init__(self):
        if self.id == None:
            self.id = uuid.uuid4().__str__()
        if not self.url.startswith(("https", "http")):
            self.url = "https://" + self.url
