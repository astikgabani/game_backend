from users.admin import (
    UserView,
    UserRoleView,
    UserSessionView,
    UserSessionTokenView,
)
from games.admin import GameView

USER_CATEGORY = "User"
GAME_CATEGORY = "Game"


def add_admin_views(admin):
    admin.add_view(UserView(name="User", category=USER_CATEGORY))
    admin.add_view(UserRoleView(name="User Roles", category=USER_CATEGORY))
    admin.add_view(UserSessionView(name="User Session", category=USER_CATEGORY))
    admin.add_view(
        UserSessionTokenView(name="User Session Tokens", category=USER_CATEGORY)
    )

    admin.add_view(GameView(name="Game View", category=GAME_CATEGORY))
