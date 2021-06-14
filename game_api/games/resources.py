from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from .models import GameModel
from .schema import GameSchema
from utils.pagination import paginate

from utils.strings_helper import gettext

game_schema = GameSchema()


class GameListResource(Resource):
    @classmethod
    @jwt_required()
    @paginate("games", schema=game_schema)
    def get(cls):
        """
        Get the list of games
        1. return the all active games along with the applied filters.
        (Paginate all this games.)

        @return:
        @rtype:
        """
        qs = GameModel.get_active()
        filter_options = ["platform", "genre"]
        for arg, value in request.args.items():
            if arg == "order_by":
                try:
                    qs = qs.order_by(
                        getattr(
                            getattr(GameModel, value), request.args.get("order", "asc")
                        )()
                    )
                except AttributeError:
                    pass
            elif arg in filter_options:
                qs = qs.filter(arg == value)
        if "editors_choice" in request.args:
            if request.args["editors_choice"].lower() in [
                "true",
                "1",
                "t",
                "y",
                "yes",
                "yeah",
                "yup",
                "certainly",
                "uh-huh",
            ]:
                qs = qs.filter_by(editors_choice=True)
            else:
                qs = qs.filter_by(editors_choice=False)
        title = request.args.get("title")
        if title:
            qs = qs.filter(GameModel.title.like(f"%{title}%"))
        return qs


class GameResource(Resource):
    @classmethod
    @jwt_required()
    def get(cls, id):
        """
        return the specified game detail.

        @return:
        @rtype:
        """
        game = GameModel.get_item(id=id)
        return {"game": game_schema.dump(game)}, 200

    @classmethod
    @jwt_required()
    def put(cls, id):
        """
        Update the provided fields of the game.

        @return:
        @rtype:
        """
        req_data = request.get_json()
        game = game_schema.load(req_data, instance=GameModel.get_item(id=id))
        if not game.id:
            return {"message": gettext("game_not_exist")}, 404
        game.save_to_db()
        return (
            {"game": game_schema.dump(game)},
            200,
        )

    @classmethod
    @jwt_required()
    def delete(cls, id):
        """
        Delete the game based on the provided id.

        @return:
        @rtype:
        """
        req_data = request.get_json()
        game = game_schema.load(req_data, instance=GameModel.get_item(id=id))
        if not game:
            return {"message": gettext("game_not_exist")}, 404
        game.delete_from_db()
        return (
            {"game": game_schema.dump(game)},
            200,
        )


class GameCreateResource(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        """
        Create the game based on the provided details.

        @return:
        @rtype:
        """
        req_data = request.get_json()
        game = game_schema.load(
            req_data, instance=GameModel.get_item(title=request.args.get("title"))
        )
        if game.id:
            return {"message": gettext("game_already_exist")}, 409
        game.save_to_db()
        return (
            {"game": game_schema.dump(game)},
            200,
        )
