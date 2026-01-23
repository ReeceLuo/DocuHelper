from fastapi import FastAPI, include_router

from routes import AuthRoutes

app = FastAPI(
    title = "DocuHelper",

    description = "A RAG application that helps you with your documents.",
    version = "1.0.0"
)

app.include_router(AuthRoutes.router)

@app.get("/")
def root():
    return {"Message": "App is running"}