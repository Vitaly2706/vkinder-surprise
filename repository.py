
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from config import db_url_object

metadata = MetaData()
Base = declarative_base()

class ViewedProfiles(Base):
    __tablename__ = 'viewed_profiles'
    user_id = sq.Column(sq.Integer, primary_key=True)
    viewed_profile_id = sq.Column(sq.Integer, primary_key=True)

class ViewedProfilesRepository:

    def __init__(self):
        engine = create_engine(db_url_object)
        Base.metadata.create_all(engine)
        self.session = Session(engine)

    def add_viewed_profile(self, user_id, viewed_profile_id):
        self.session.add(ViewedProfiles(user_id=user_id, viewed_profile_id=viewed_profile_id))
        self.session.commit()

    def was_profile_viewed(self, user_id, viewed_profile_id):
        return self.session.query(exists().where((ViewedProfiles.user_id == user_id) & (ViewedProfiles.viewed_profile_id == viewed_profile_id))).scalar()
