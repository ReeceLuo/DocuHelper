from fastapi import FastAPI, include_router



app = FastAPI(
    title = "DocuHelper",
    description = "A RAG application that helps you with your documents.",
    version = "1.0.0"
)



@app.get("/")
def root():
    return {"Message": "App is running"}