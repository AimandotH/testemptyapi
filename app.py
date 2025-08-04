# Import necessary libraries
from flask import Flask, request, jsonify, Response
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
    # This will force the client to try to parse it as JSON and fail.
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

@app.route('/non-json-with-json-header', methods=['GET', 'POST'])
def non_json_with_json_header_endpoint():
    """
    This endpoint returns a plain text string but with a 'Content-Type: application/json' header.
    This is intended to cause a JSON parsing error on the client side, as the client will
    attempt to parse the plain text as JSON and fail. This can lead to a "crash"
    or unhandled exception if the client's error handling for JSON parsing is not robust.
    """
    logging.info(f"Received {request.method} request to /non-json-with-json-header")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    # Return plain text, but with a JSON content type header
    return "This is not JSON, but the header says it is!", 200, {'Content-Type': 'application/json'}

@app.route('/empty-structured-json', methods=['GET', 'POST'])
def empty_structured_json_endpoint():
    """
    This endpoint returns a valid JSON object, but with empty or null values
    for keys that a client application (like FastGPT) might expect to contain
    meaningful data. This directly targets "empty model flow output" errors.

    You can modify 'response_data' below to test different scenarios:
    1.  'text': "" (empty string) - current default
    2.  'text': None (null value) - uncomment the line below
    3.  Omit 'text' key entirely - comment out the 'text' line
    4.  Omit 'output' key entirely - comment out the 'output' dictionary
    5.  'output': None (null output object) - uncomment the line below
    """
    logging.info(f"Received {request.method} request to /empty-structured-json")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    # --- Modify this 'response_data' dictionary to test different "empty" scenarios ---
    response_data = {
        "output": {
            "text": "", # Scenario 1: Empty string for text
            # "text": None, # Scenario 2: Uncomment to test with 'text' as null
            "tokens": 0,
            "status": "success",
            "model_response": None
        },
        # "output": None, # Scenario 5: Uncomment to test with 'output' as null
        # Scenario 4: Comment out the entire 'output' dictionary above to test missing 'output' key
        "details": {},
        "metadata": []
    }
    # ---------------------------------------------------------------------------------
    
    return jsonify(response_data), 200

@app.route('/no-content-204', methods=['GET', 'POST'])
def no_content_204_endpoint():
    """
    This endpoint returns an HTTP 204 No Content status.
    This explicitly tells the client that the request was successful but there is no
    response body. If the webhook app expects *any* content, even an empty JSON object,
    this might trigger an "empty response" error at a lower level than JSON parsing.
    """
    logging.info(f"Received {request.method} request to /no-content-204")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    # Return 204 No Content status. No body should be sent with 204.
    return Response(status=204)

@app.route('/html-like-response', methods=['GET', 'POST'])
def html_like_response_endpoint():
    """
    This endpoint returns a simple HTML-like string with a 'Content-Type: text/html' header.
    If the webhook app expects JSON or plain text, receiving HTML could lead to
    parsing errors or an interpretation of the model output as "empty" because
    it cannot extract the expected data from the HTML structure.
    """
    logging.info(f"Received {request.method} request to /html-like-response")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    # Return a simple HTML string
    html_content = "<html><body><h1>Hello from Test API!</h1><p>This is an HTML response.</p></body></html>"
    return Response(html_content, mimetype='text/html')

@app.route('/empty-body-200', methods=['GET', 'POST'])
def empty_body_200_endpoint():
    """
    This endpoint returns an HTTP 200 OK status with a completely empty response body.
    This is different from a 204 No Content, as it implies a body *could* be present
    but isn't. Some client-side parsers or webhook systems might interpret this
    as an "empty" response if they expect any content at all.
    """
    logging.info(f"Received {request.method} request to /empty-body-200")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    # Return an empty string with 200 OK status and no specific content-type
    # This often defaults to 'text/plain' or no content-type, which can be problematic
    return "", 200

@app.route('/simple-unexpected-json', methods=['GET', 'POST'])
def simple_unexpected_json_endpoint():
    """
    This endpoint returns a valid JSON object, but it's a very simple, flat structure.
    If FastGPT expects a complex, nested structure for its model flow output,
    this simple JSON might be interpreted as "empty" or "not normal" because
    it lacks the expected keys or nesting.
    """
    logging.info(f"Received {request.method} request to /simple-unexpected-json")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    # Return a simple, flat JSON object
    return jsonify({"status": "ok", "message": "This is a simple response."}), 200

@app.route('/specific-llm-like-response', methods=['GET', 'POST'])
def specific_llm_like_response_endpoint():
    """
    This endpoint returns a JSON structure that mimics a common LLM API response,
    but with placeholder "string" values and an HTML-like tag in the content.
    This is designed to test if FastGPT's model flow validation specifically
    checks for actual generated content rather than just the presence of keys.
    """
    logging.info(f"Received {request.method} request to /specific-llm-like-response")
    if request.method == 'POST':
        if request.is_json:
            logging.info(f"POST JSON data: {request.json}")
        else:
            logging.info(f"POST form data: {request.form}")
    
    response_data = {
        "choices": [
            {
                "message": {
                    "role": "string",
                    "content": "string<>"
                },
                "finish_reason": "string",
                "index": "string"
            }
        ]
    }
    return jsonify(response_data), 200


# Run the Flask application
if __name__ == '__main__':
    # You can run this on a specific host and port.
    # For local testing, '0.0.0.0' makes it accessible from your network,
    # and 5000 is the default Flask port.
    # If deploying, ensure it's accessible from your third-party app.
    app.run(host='0.0.0.0', port=5000, debug=False) # Set debug=False for production use
