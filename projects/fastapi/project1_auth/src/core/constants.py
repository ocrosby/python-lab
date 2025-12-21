class HTTPStatus:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    NOT_ACCEPTABLE = 406
    CONFLICT = 409
    UNSUPPORTED_MEDIA_TYPE = 415


class ErrorMessages:
    ITEM_NOT_FOUND = "Item not found"
    UNSUPPORTED_MEDIA_TYPE = "Unsupported Media Type. Use application/json"
    NOT_ACCEPTABLE = "Not Acceptable. API only supports application/json"
    INCORRECT_CREDENTIALS = "Incorrect username or password"
    INVALID_CREDENTIALS = "Could not validate credentials"
    INACTIVE_USER = "Inactive user"


class CacheControl:
    NO_CACHE = "no-cache"
    MAX_AGE_60 = "max-age=60, public"


class AuthHeaders:
    WWW_AUTHENTICATE = "WWW-Authenticate"
    BEARER = "Bearer"


class ContentTypes:
    APPLICATION_JSON = "application/json"
    ALL = "*/*"


class TestConstants:
    DOCKER_COMPOSE_STARTUP_DELAY = 5
