from utils.admin_helper.helper import SuperView

from users.models import (
    UserModel,
    UserRoleModel,
    UserSessionModel,
    UserSessionTokenModel,
)


class UserView(SuperView):

    inline_models = [
        UserRoleModel,
        UserSessionModel,
    ]
    column_exclude_list = ["password"]
    column_filters = ("email",)

    column_searchable_list = ("email", "phone_no")

    def __init__(self, model=UserModel, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)


class UserRoleView(SuperView):

    column_filters = ("role",)

    column_searchable_list = ("role",)

    def __init__(self, model=UserRoleModel, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)


class UserSessionView(SuperView):
    inline_models = [UserSessionTokenModel]

    column_filters = ("ip", "type")

    column_searchable_list = ("ip", "type")

    def __init__(self, model=UserSessionModel, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)


class UserSessionTokenView(SuperView):
    # inline_models = [UserSessionModel]

    def __init__(self, model=UserSessionTokenModel, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)
