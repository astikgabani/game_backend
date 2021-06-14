import traceback

from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from users.models import (
    UserModel,
    UserSessionModel,
    UserSessionTokenModel,
    UserRoleModel,
)
from users.schema import (
    UserSchema,
    UserLoginSchema,
    UserSessionSchema,
    UserSessionTokenSchema,
    UserRoleSchema,
)

from utils.strings_helper import gettext
from utils.user_roles import required_role

user_login_schema = UserLoginSchema()
user_register_schema = UserSchema()
user_session_schema = UserSessionSchema()
user_session_token_schema = UserSessionTokenSchema()
user_role_schema = UserRoleSchema()


class UserLogin(Resource):
    @classmethod
    def post(cls):
        """
        Verify the credentials and return tokens
        1. load the request data
        2. if user not found, return user not registered 401
        3. verify the credentials, if not authorized, return invalid creds 401
        4. check for email confirmation, if not confirmed, return email not confirm 400
        5. generate the access-token and refresh-token
        6. load the session info
        7. if new IP is found for user for specific type then automatically logout from previous sessions
        8. if more than 5 session has generated, automatically logout from previous sessions
        9. Register new token into db
        10. return newly created access-token and refresh-token.

        @return: return newly created access-token and refresh-token.
        @rtype: dict of tokens
        """
        req_data = request.get_json()
        user = user_login_schema.load(
            req_data,
            instance=UserModel.get_item(email=req_data.get("email")),
            partial=True,
        )
        if not user.id:
            return {"message": gettext("user_not_found")}, 401

        input_password = req_data.get("clear_input_password")
        if not user.verify_password(input_password):
            return {"message": gettext("user_invalid_credentials")}, 401

        # Generate tokens
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        note = None

        # Loading session info
        session_instance = UserSessionModel.get_item(
            user_id=user.id, type=req_data.get("type") or "web"
        )
        current_session = user_session_schema.load(
            req_data, instance=session_instance, partial=True
        )

        # Manage sessions
        # if new IP is found for user for specific type then automatically logout from previous sessions
        # if more than 5 session has generated, automatically logout from previous sessions
        if current_session.id and (
            current_session.ip != request.remote_addr
            or len(current_session.tokens) >= 5
        ):
            for session_token in current_session.tokens:
                session_token.deactivate()
            current_session.deactivate()
            current_session.save_to_db()
            current_session = user_session_schema.load(req_data)
            note = gettext("user_login_max_count_reached")

        current_session.user = user
        current_session.ip = request.remote_addr
        current_session.save_to_db()

        # register new token into DB
        if refresh_token not in (
            token.refresh_token for token in current_session.tokens
        ):
            session_token_dict = {
                "refresh_token": refresh_token,
                "session_id": current_session.id,
            }
            token = user_session_token_schema.load(session_token_dict)
            token.save_to_db()

        total_session_note = gettext("user_active_sessions").format(
            len(current_session.tokens)
        )
        note = note + total_session_note if note else total_session_note

        return (
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "note": note,
            },
            200,
        )


class UserRegister(Resource):
    @classmethod
    def post(cls):
        """
        Register the user
        1. load the user with request data
        2. if user already registered, return 409 conflict
        3. return the newly created user details
        4. if any exception occurred, delete user from db

        @return: the newly created user details
        @rtype: dict of newly created user details
        """
        req_data = request.get_json()
        user = user_register_schema.load(
            req_data,
            instance=UserModel.get_item(email=req_data.get("email")),
            partial=True,
        )
        if user.id:
            return {"message": gettext("user_already_registered")}, 409
        try:
            user.save_to_db()
            user.send_confirmation_email()
            return (
                {
                    "message": gettext("user_account_created"),
                    "data": user_register_schema.dump(user),
                },
                201,
            )
        except Exception as e:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": gettext("user_creation_failed")}, 500


class UserTokenRefresh(Resource):
    """
    Refresh token endpoint. This will generate a new access token from
    the refresh token, but will mark that access token as non-fresh,
    as we do not actually verify a password in this endpoint.
    """

    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        """
        Create a new access-token from refresh-token
        1. extract refresh-token from header
        2. load the session from db
        3. load the token from db
        4. if token found, create access-token and return it.
        5. else return not found 404

        @return: newly created access-token
        @rtype: 200
        """
        current_user = get_jwt_identity()
        auth_header = request.headers.get("Authorization")
        user_token = auth_header.split()[1]
        session = UserSessionModel.get_item(user_id=current_user)
        data = {"refresh_token": user_token, "session": session}

        token = user_session_token_schema.load(
            data, instance=UserSessionTokenModel.get_item(**data), partial=True,
        )
        if token.id:
            return (
                {
                    "access_token": create_access_token(
                        identity=current_user, fresh=False
                    )
                },
                200,
            )
        return {"message": gettext("user_session_expired")}, 440


class UserFreshLogin(Resource):
    """
    Fresh login endpoint. This is designed to be used if we need to
    make a fresh token for a user (by verifying they have the
    correct username and password). Unlike the standard login endpoint,
    this will only return a new access token, so that we don't keep
    generating new refresh tokens, which entirely defeats their point.
    """

    @classmethod
    def post(cls):
        """
        Generate new fresh access-token from creds
        1. load the user details with request data
        2. if user not found, return 404 not found
        3. verify the creds, if creds not verified, return invalid credentials, 401
        4. generate and return new fresh access-token

        @return: new fresh access-token
        @rtype: dict of access-token
        """
        req_data = request.get_json()
        user = user_login_schema.load(
            req_data,
            instance=UserModel.get_item(email=req_data.get("email")),
            partial=True,
        )
        if not user.id:
            return {"message": gettext("user_not_found")}, 401

        input_password = req_data.get("clear_input_password")
        if not user.verify_password(input_password):
            return {"message": gettext("user_invalid_credentials")}, 401
        return (
            {"access_token": create_access_token(identity=user.id, fresh=True)},
            200,
        )


class UserRoles(Resource):
    @jwt_required
    @required_role(["admin"])
    def get(self):
        """
        Get all the roles
        1. fetch all the roles from the db
        2. if roles not found, return 404 not found
        3. return list of all roles

        @return: all the roles
        @rtype: dict of roles list
        """
        roles = UserRoleModel.get_items()
        if not roles:
            return {"message": gettext("user_role_not_found")}, 404
        return {"roles": [role.role for role in roles]}, 200

    @jwt_required
    # @required_role(["admin"])
    def post(self):
        """
        Create the role
        1. load the role with request data from the db
        2. if role found, return 409 conflict
        3. save to db and return newly created role details

        @return: newly created role details
        @rtype: dict of role details
        """
        req_data = request.get_json()
        user_role = user_role_schema.load(
            req_data, instance=UserRoleModel.get_item(role=req_data.get("role"))
        )
        if user_role.get("id"):
            return {"message": gettext("user_role_already_created")}, 409
        user_role.save_to_db()
        return (
            {
                "message": gettext("user_role_created"),
                "data": user_role_schema.dump(user_role),
            },
            200,
        )


class UserRoleAssign(Resource):
    @jwt_required
    # @required_role(["admin"])
    def post(self):
        """
        Assign the specific roles to user
        1. load the user role with request data from the db
        2. if role found, return 409 conflict
        3. loop through all the user emails. load the user from db and add user into the user_role's object.
        4. save the user roles and return success, already assigned and user not found list

        @return: success, already assigned and user not found list
        @rtype: dict of success, already assigned and user not found list
        """
        req_data = request.get_json()
        user_role = user_role_schema.load(
            req_data, instance=UserRoleModel.get_item(role=req_data.get("role"))
        )
        if not user_role.get("id"):
            return {"message": gettext("user_role_not_found")}, 409
        user_not_found_list = []
        already_assigned = []
        for user_email in req_data.get("users"):
            user = UserModel.get_item(email=user_email)
            if user:
                if user in user_role.users:
                    already_assigned.append(user.get("email"))
                else:
                    user_role.users.append(user)
            else:
                user_not_found_list.append(user.get("email"))
        user_role.save_to_db()
        return (
            {
                "Success": [
                    user_email
                    for user_email in req_data.get("users")
                    if user_email not in user_not_found_list
                    and user_email not in already_assigned
                ],
                "Already Assigned": already_assigned,
                "User not found": user_not_found_list,
            },
            200,
        )
