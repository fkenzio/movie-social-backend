from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.list import ListCreate, ListUpdate, ListResponse, ListDetailResponse
from app.services.list_service import ListService

router = APIRouter()

@router.post("/", response_model=ListResponse)
def create_list(
    list_data: ListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva lista"""
    new_list = ListService.create_list(db, current_user.id, list_data)
    return {**new_list.__dict__, "movies_count": 0}

@router.get("/", response_model=List[ListResponse])
def get_my_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener mis listas"""
    return ListService.get_user_lists(db, current_user.id)

@router.get("/{list_id}", response_model=ListDetailResponse)
def get_list_detail(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de lista"""
    return ListService.get_list_detail(db, list_id, current_user.id)

@router.put("/{list_id}", response_model=ListResponse)
def update_list(
    list_id: int,
    list_data: ListUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar lista"""
    updated_list = ListService.update_list(db, list_id, current_user.id, list_data)
    return {**updated_list.__dict__, "movies_count": 0}

@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar lista"""
    ListService.delete_list(db, list_id, current_user.id)
    return {"message": "Lista eliminada"}

@router.post("/{list_id}/movies/{movie_tmdb_id}")
def add_movie_to_list(
    list_id: int,
    movie_tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar película a lista"""
    ListService.add_movie_to_list(db, list_id, current_user.id, movie_tmdb_id)
    return {"message": "Película agregada a la lista"}

@router.delete("/{list_id}/movies/{movie_tmdb_id}")
def remove_movie_from_list(
    list_id: int,
    movie_tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quitar película de lista"""
    ListService.remove_movie_from_list(db, list_id, current_user.id, movie_tmdb_id)
    return {"message": "Película eliminada de la lista"}

@router.get("/check/{movie_tmdb_id}")
def check_movie_in_lists(
    movie_tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verificar en qué listas está una película"""
    return ListService.check_movie_in_lists(db, current_user.id, movie_tmdb_id)