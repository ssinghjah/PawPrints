from flask import Flask, json, request
import toml
import library

HOST = "127.0.0.1"
PORT = 8080

server_app = Flask(__name__)

@server_app.route('/parselogline', methods=['POST'])
def run_api():
    try:
        print(request.json)
        http_response_status = 400 
        response = {"status": 0, "result": {}}
        if "log" in request.json:
             log = request.json["log"]
             response = library.parse_for_viz(log)
             http_response_status = 200 

        # Return execution result
        http_response = server_app.response_class(
            response = json.dumps(response),
            status = http_response_status,
            mimetype = 'application/json'
        )
        return http_response
    except Exception as e:
        print(e)
        http_response_status = 400 
        response = {"status": 0, "result": {}, "error": "Internal Server Error: " + str(e)}
        http_response = server_app.response_class(
            response = json.dumps(response),
            status = http_response_status,
            mimetype = 'application/json'
        )
        return http_response

if __name__ == '__main__':  
    server_app.run(host=HOST, port=PORT)