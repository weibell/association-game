import requests
import json
from flask import jsonify

# TODO: enter URL for Game API
GAME_API = "http://..."


def webhook(request):
    """
    Called through HTTP request initiated by Dialogflow. Forwards user input to the Game API which returns questions
    to prompt the user with.

    The purpose of introducing an additional webhook in between the game API and Dialogflow is to reduce the overall
    complexity by adding another level of abstraction. Only a few parameters sent by Dialogflow are important to us,
    so we will filter and work with them accordingly.

    Note that this webhook must return within five seconds, else Dialogflow will ignore the response.

    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    query_result = get_request_value(request, 'queryResult')

    game_response = send_payload({
        'session_id': get_request_value(request, 'session'),
        'action': query_result['action'] if 'action' in query_result else None,
        'intent': query_result['intent']['displayName'],
        'parameters': query_result['parameters'],
        'raw_input': query_result['queryText'],
    })

    return jsonify(handle_api_response(game_response))


def handle_api_response(response):
    """
    Handle response by Game API and convert to Dialogflow API format.

    Request and response format of Dialogflow V2 API:
    https://dialogflow.com/docs/fulfillment/how-it-works
    """
    output = get_dict_value(response, 'output')
    end_conversation = get_dict_value(response, 'end_conversation')

    payload = {
        'fulfillmentText': output
    }

    if end_conversation:
        payload['followupEventInput'] = {
            'name': 'exit',
            'languageCode': 'de'
        }

    return payload


def get_request_value(req, key):
    """
    Return the value of the request object's JSON dictionary.
    """
    request_json = req.get_json()
    if req.args and key in req.args:
        return req.args.get(key)
    elif request_json and key in request_json:
        return request_json[key]
    else:
        return None


def get_dict_value(dict_, key):
    """
    Return the value for key in the (JSON) dictionary.
    """
    return dict_[key] if key in dict_ else None


def send_payload(payload):
    """
    Transmit the payload to the Game API and return its response.

    Request and response format of Dialogflow V2 API:
    https://dialogflow.com/docs/fulfillment/how-it-works
    """
    r = requests.post(GAME_API, data=json.dumps(payload))
    return r.json()
