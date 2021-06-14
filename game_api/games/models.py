from plugins.db import db

from utils.model_helper.super_model import SuperModel


class GameModel(db.Model, SuperModel):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256))
    platform = db.Column(db.String(128))
    score = db.Column(db.Float)
    genre = db.Column(db.String(64))
    editors_choice = db.Column(db.Boolean, default=False)

    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f"{self.title}"
