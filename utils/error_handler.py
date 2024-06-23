from flask import jsonify


async def handle_429(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 429,
                "message": "too many requests",
                "data": None,
                "errors": None,
            }
        ),
        429,
    )


async def handle_404(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 404,
                "message": "endpoint not found",
                "data": None,
                "errors": None,
            }
        ),
        404,
    )


async def handle_415(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 415,
                "message": "unsupported media type",
                "data": None,
                "errors": None,
            }
        ),
        415,
    )


async def handle_400(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 400,
                "message": "bad request",
                "data": None,
                "errors": None,
            }
        ),
        400,
    )


async def handle_401(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 401,
                "message": "authorization invalid",
                "data": None,
                "errors": None,
            }
        ),
        401,
    )


async def handle_403(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 403,
                "message": "user invalid",
                "data": None,
                "errors": None,
            }
        ),
        403,
    )


async def handle_405(error):
    return (
        jsonify(
            {
                "success": False,
                "status_code": 405,
                "message": "method not allowed",
                "data": None,
                "errors": None,
            }
        ),
        405,
    )
