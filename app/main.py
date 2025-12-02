from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.v1 import auth, movies, ratings, list, rankings, reviews, users, feed


# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cineminha API",
    description="API para la red social de películas Cineminha",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(rankings.router, prefix="/api/v1/rankings", tags=["rankings"])
app.include_router(list.router, prefix="/api/v1/lists", tags=["lists"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(movies.router, prefix="/api/v1/movies", tags=["movies"])
app.include_router(ratings.router, prefix="/api/v1/ratings", tags=["ratings"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(feed.router, prefix="/api/v1/feed", tags=["feed"])

@app.get("/")
def read_root():
    return {
        "message": "Cineminha API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}