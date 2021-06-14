from utils.admin_helper.helper import SuperView

from .models import GameModel


class GameView(SuperView):

    column_searchable_list = ("title",)

    def __init__(self, model=GameModel, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)
