from flask import jsonify

STATUS_CODES = {
    200: {
        'category': 'Success',
        'message': 'OK'
    },

    201: {
        'category': 'Success',
        'message': 'Created'
    },

    204: {
        'category': 'Success',
        'message': 'No Content'
    },

    304: {
        'category': 'Redirection',
        'message': 'Not Modified'
    },

    400: {
        'category': 'Client Error',
        'message': 'Bad Request'
    },

    401: {
        'category': 'Client Error',
        'message': 'Unauthorized'
    },

    403: {
        'category': 'Client Error',
        'message': 'Forbidden'
    },

    404: {
        'category': 'Client Error',
        'message': 'Not Found'
    },

    409: {
        'category': 'Client Error',
        'message': 'Conflict'
    },

    500: {
        'category': 'Server Error',
        'message': 'Internal Server Error'
    }
}

def get_status_code(id):
    return jsonify(STATUS_CODES[id]), id if list(STATUS_CODES).count(id) > 0 else None