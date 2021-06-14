from users.resources import (
    UserLogin,
    UserRegister,
    UserRoles,
    UserFreshLogin,
    UserTokenRefresh,
    UserRoleAssign,
)
from games.resources import GameResource, GameCreateResource, GameListResource


def add_resources(api):

    # User
    api.add_resource(UserLogin, "/login")
    api.add_resource(UserRegister, "/register")
    api.add_resource(UserRoles, "/user-roles")
    api.add_resource(UserRoleAssign, "/user-roles-assign")
    api.add_resource(UserFreshLogin, "/fresh-login")
    api.add_resource(UserTokenRefresh, "/user-token-refresh")

    # Game
    api.add_resource(GameListResource, "/games")
    api.add_resource(GameResource, "/game/<int:id>")
    api.add_resource(GameCreateResource, "/game")
