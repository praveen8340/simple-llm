import unicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn
from controller.llm_main import study_llm

def test_method(request):
    return JSONResponse({"message": "Hello World"})


routes = [
    Route(path="/test", endpoint=test_method, methods=["GET"]),
    Route(path="/study", endpoint=study_llm, methods=["POST"]),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8800,
        log_level="info",
        server_header=False,
    )