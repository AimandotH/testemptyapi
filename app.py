# Import necessary libraries
from flask import Flask, request, jsonify
import time
import logging

# Initialize the Flask application
app = Flask(__name__)

# Configure logging to see requests in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the endpoint that will "not return anything" (i.e., cause a timeout)
@app.route('/no-response', methods=['GET', 'POST'])
def no_response_endpoint():
    """
    This endpoint is designed to simulate a server that does not respond.
    It will intentionally sleep for a very long time (e.g., 600 seconds = 10 minutes),
    which should exceed most client-side timeouts, causing the client to
    experience a connection timeout error.

    From the client's perspective, this API will appear to "not return anything"
    because no HTTP response (status code, headers, or body) will be sent
    before the client's connection times out.
    """
    logging.info(f"Received {request.method} request to /no-response")
    if request.method == 'POST':
        # Log any incoming JSON or form data for POST requests
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")

    # Intentionally sleep for a very long time.
    # This will cause the client's connection to time out.
    # A typical client timeout might be 30 seconds, 60 seconds, etc.
    # 600 seconds (10 minutes) ensures it exceeds most defaults.
    time.sleep(600)

    # IMPORTANT: The code below this line will generally NOT be reached
    # because the client will have timed out and closed the connection
    # before the sleep finishes. If it somehow is reached (e.g., a very
    # long client timeout or direct server interaction), it would send
    # a 200 OK, but that's not the primary intent.
    logging.warning("This line should ideally not be reached if client times out.")
    return jsonify({"message": "This response should not be seen by the client due to timeout."}), 200

@app.route('/malformed-response', methods=['GET', 'POST'])
def malformed_response_endpoint():
    """
    This endpoint is designed to simulate an API that returns a response
    that is syntactically malformed (e.g., invalid JSON).
    This can cause client-side parsers to throw errors, leading to a "crash"
    or unhandled exception in the webhook application if not properly handled.
    """
    logging.info(f"Received {request.method} request to /malformed-response")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")

    # Return a string that looks like incomplete or invalid JSON
    # For example, missing a closing brace or having extra commas
    malformed_json_string = '{"status": "error", "message": "This is malformed JSON, missing a closing brace or invalid syntax", "data": [1, 2,'
    
    # You could also return plain text when JSON is expected
    # return "This is plain text, not JSON!", 200, {'Content-Type': 'text/plain'}

    # Return the malformed string with a 200 OK status, but with JSON content type
    # This will force the client to try and parse it as JSON and fail.
    return malformed_json_string, 200, {'Content-Type': 'application/json'}

@app.route('/empty-json-response', methods=['GET', 'POST'])
def empty_json_response_endpoint():
    """
    This endpoint is designed to simulate an API that returns a successful
    HTTP 200 OK status but with an empty JSON object as the response body.
    This can trigger "empty response" or "no output" errors in client
    applications that expect a specific, non-empty data structure.
    """
    logging.info(f"Received {request.method} request to /empty-json-response")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")

    # Return an empty JSON object with a 200 OK status
    return jsonify({}), 200


# Run the Flask application
if __name__ == '__main__':
    # You can run this on a specific host and port.
    # For local testing, '0.0.0.0' makes it accessible from your network,
    # and 5000 is the default Flask port.
    # If deploying, ensure it's accessible from your third-party app.
    app.run(host='0.0.0.0', port=5000, debug=False) # Set debug=False for production use
