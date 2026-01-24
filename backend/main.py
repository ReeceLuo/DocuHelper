from fastapi import FastAPI
from routes import AuthRoutes, FilesRoutes
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "DocuHelper",
    description = "A RAG application that helps you with your documents.",
    version = "1.0.0"
)

# Include routers
app.include_router(AuthRoutes.router)
app.include_router(FilesRoutes.router)

@app.get("/")
def root():
    return {"Message": "App is running"}