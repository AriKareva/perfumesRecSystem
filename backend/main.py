import logging
from db.connection import init_db, Base, db_engine
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from perfumes.routes import perfumes_router
from auth.routes import auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def app_start():
    logger.info("Приложение запускается...")
    init_db()

@app.get('/')
async def root():
    return {'message' : 'Perfumes Recomendarion System'}


app.include_router(perfumes_router)
app.include_router(auth_router)


# Конфигурация OpenAPI для Swagger с поддержкой Bearer токена
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title='Perfume Recomendation System',
        version='1.0.0',
        description='API для системы подбора парфюмов',
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Добавляем Bearer ко всем protected endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if isinstance(method, dict):
                if "connections" in str(method):
                    method["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
