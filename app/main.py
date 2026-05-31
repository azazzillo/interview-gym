# Python
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# Local
from app.api.post import router as post_router
from app.api.auth import router as auth_router
from app.api.interview import router as interview_router
from app.api.task import router as task_router


app = FastAPI(
    title="InterviewGYM",
    description=" ",
    docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media"
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.include_router(post_router)
app.include_router(auth_router)
app.include_router(interview_router)
app.include_router(task_router)


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="localhost", 
        port=8080
    )