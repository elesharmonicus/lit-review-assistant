from dataclasses import dataclass

@dataclass
class Paper:
    title: str
    abstract: str
    authors: list[str]
    year: int | None
    doi: str
    journal: str = ""  

    @classmethod
    def from_dict(cls, d: dict) -> "Paper":
        return cls(
            title=d.get("title", ""),
            abstract=d.get("abstract", ""),
            authors=[a.strip() for a in d.get("authors", "").split(" and ") if a.strip()],
            year=d.get("year"),
            doi=d.get("doi", ""),
            journal=d.get("journal", "")
        )