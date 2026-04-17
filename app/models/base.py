# SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy import MetaData
# Python
from typing import Any
import os


metadata = MetaData()

@as_declarative()
class Base:
    '''
    Базовый класс, от которого будут наследоваться остальные классы
    '''

    id: Any
    __name__: str
    metadata = metadata
