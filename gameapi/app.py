from datetime import datetime

from flask import Flask, request

import gameapi.gameplay as gameplay
from gameapi.contexts import InputContext, SessionContext, OutputContext
import gameapi.db as db

app = Flask(__name__)


@app.route("/api", methods=['GET', 'POST'])
def webhook():
    # initialize input, output and session contexts
    input_context = InputContext(request)
    session_context = SessionContext(input_context.get('session_id'))
    output_context = OutputContext()

    # debug output
    # print("\n--- BEGIN ---")
    # print("Raw request data: " + str(request.get_data()))
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # print(input_context)
    # print(session_context)
    print()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Raw input: {input_context.get('raw_input')}")
    print()

    db.log(input_context, session_context)

    # handle debug mode
    if input_context.get('action') == 'debug':
        debug_mode = input_context.check_option_debug()

        # force-restart session
        if debug_mode == 'alpha':
            session_context.restart_session()
            output_context.say("Okay, ich setze das Spiel zurück.")

        # skip to association
        elif debug_mode == 'beta':
            session_context.set('state', 'ASSOCIATIONS')
            session_context.set('substate', 0)
            output_context.say("Okay, ich springe zum zweiten Spielabschnitt")

    # main game logic
    gameplay.next_interaction(output_context, session_context, input_context)

    # debug output
    # print(session_context)
    # print(output_context)
    # print("---- END -----\n")

    # respond to user
    return output_context.jsonify()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
