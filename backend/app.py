import os

from quart import Quart

app = Quart(__name__)


@app.route("/api")
async def json():
    return {"hello": "world"}


if __name__ == "__main__":
    port = os.environ.get('PORT', None)
    host = os.environ.get('HOST', None)

    app.run(debug=True, host=host, port=port)
