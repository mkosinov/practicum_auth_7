from dataclasses import dataclass, field
from datetime import datetime
import uuid


# эталонные датаклассы (DC) под схему в Postgres
@dataclass
class TimeStampCreatedDC:
    created: str = field(default=datetime.now)


@dataclass
class TimeStampModifiedDC:
    modified: str = field(default=datetime.now)


@dataclass(kw_only=True)
class GenreDC(TimeStampCreatedDC, TimeStampModifiedDC):
    name: str
    description: str = field(default='')
    id: uuid.UUID = field(default_factory=uuid.UUID)

    def __post_init__(self):
        if self.description is None:
            self.description = ''


@dataclass(kw_only=True)
class PersonDC(TimeStampCreatedDC, TimeStampModifiedDC):
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.UUID)


@dataclass(kw_only=True)
class FilmWorkDC(TimeStampCreatedDC, TimeStampModifiedDC):
    title: str
    description: str = field(default='')
    creation_date: str = field(default='')
    rating: float = field(default=0.0)
    type: str = field(default='mv')
    id: uuid.UUID = field(default_factory=uuid.UUID)
    file_path: str = field(default='')

    def __post_init__(self):
        if self.description is None:
            self.description = ''
        if self.rating is None:
            self.rating = 0


@dataclass(kw_only=True)
class GenreFilmWorkDC(TimeStampCreatedDC):
    id: uuid.UUID = field(default_factory=uuid.UUID)
    genre_id: uuid.UUID = field(default_factory=uuid.UUID)
    film_work_id: uuid.UUID = field(default_factory=uuid.UUID)


@dataclass(kw_only=True)
class PersonFilmWorkDC(TimeStampCreatedDC):
    role: str
    id: uuid.UUID = field(default_factory=uuid.UUID)
    person_id: uuid.UUID = field(default_factory=uuid.UUID)
    film_work_id: uuid.UUID = field(default_factory=uuid.UUID)
