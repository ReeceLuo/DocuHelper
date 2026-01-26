from fastapi import FastAPI

from routes import AuthRoutes, FileRoutes

app = FastAPI(
    title = "DocuHelper",
    description = "A RAG application that helps you with your documents.",
    version = "1.0.0"
)

app.include_router(AuthRoutes.router)
app.include_router(FileRoutes.router)

@app.get("/")
def root():
    return {"Message": "App is running"}