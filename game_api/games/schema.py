from marshmallow import RAISE

from plugins.ma import ma

from .models import GameModel


class GameSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GameModel
        include_fk = True
        unknown = RAISE
        load_instance = True
