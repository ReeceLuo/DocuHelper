from fastapi import APIRouter, HTTPException, status



router = APIRouter(
    prefix = "/chat",
    tags = ["Chat"]
)


