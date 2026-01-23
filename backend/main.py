import logging
from urllib.request import Request
from db.connection import init_db, Base, db_engine
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from perfumes.routes import perfumes_router
from auth.routes import auth_router
from ratings.routes import ratings_router
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Perfume Recommendation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
    },
    security=[{"HTTPBearer": []}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно для отладки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_headers(request: Request, call_next):
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    print(f"=== Request Headers ===")
    print(f"Auth Header: {auth_header}")
    print(f"All Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    print(f"Response Status: {response.status_code}")
    return response

@app.on_event("startup")
async def app_start():
    logger.info("Приложение запускается...")
    init_db()

@app.get('/')
async def root():
    return {'message' : 'Perfumes Recomendarion System'}


app.include_router(perfumes_router)
app.include_router(auth_router)
app.include_router(ratings_router)
