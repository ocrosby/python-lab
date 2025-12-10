from fastapi import Response


def set_json_response_headers(
    response: Response,
    cache_control: str = "no-cache"
) -> None:
    response.headers["Cache-Control"] = cache_control
    response.headers["Content-Type"] = "application/json"


def set_no_cache_headers(response: Response) -> None:
    set_json_response_headers(response, "no-cache")


def set_cache_headers(response: Response, max_age: int = 60) -> None:
    set_json_response_headers(response, f"max-age={max_age}, public")
