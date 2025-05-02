from functools import wraps

from flask import Flask, Response, request,make_response
import time
from flask_cors import CORS

from controller.SearchController import SearchController

app = Flask(__name__)
CORS(app)

# 装饰器封装的缓存处理逻辑
def cache_control(max_age=3600):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            resp.headers['Cache-Control'] = f'public, max-age={max_age}'
            return resp
        return wrapped
    return decorator

@app.route('/test')
def stream():
    def generate():
        # Simulate fetching large resources incrementally
        for i in range(10):
            time.sleep(1)  # Simulate time taken to fetch each resource
            yield f"data: Resource {i}\n\n"  # SSE format: "data: <message>\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route('/getAnimePlayUrl',methods = ['GET'])
@cache_control(max_age=600)
def getAnimePlayUrl():
    name = request.args.get('name')
    searchController = SearchController()
    return Response(searchController.get_anime(name), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)