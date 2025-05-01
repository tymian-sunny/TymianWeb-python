from flask import Flask, Response, request
import time
from flask_cors import CORS

from controller.SearchController import SearchController

app = Flask(__name__)
CORS(app)
@app.route('/test')
def stream():
    def generate():
        # Simulate fetching large resources incrementally
        for i in range(10):
            time.sleep(1)  # Simulate time taken to fetch each resource
            yield f"data: Resource {i}\n\n"  # SSE format: "data: <message>\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route('/getAnimePlayUrl',methods = ['GET'])
def getAnimePlayUrl():
    name = request.args.get('name')
    searchController = SearchController()
    return Response(searchController.get_anime(name), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)