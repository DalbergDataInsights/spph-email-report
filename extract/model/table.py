from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
import json

Base = declarative_base()


class Config(Base):

    __tablename__ = "config"

    indicator = Column(Integer, primary_key=True, autoincrement=True)
    function = Column(String, nullable=False)
    group = Column(String, nullable=False)
    view = Column(String, nullable=False)
    denominator = Column(String, nullable=False)

    def serialize(self):
        return {
            "config_indicator": self.indicator,
            "config_function": self.function,
            "config_group": self.group,
            "config_view": self.view,
            "config_denominator": self.denominator,
        }


class FetchDate(Base):

    __tablename__ = "fetch_date"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)

    def serialize(self):
        return self.date
