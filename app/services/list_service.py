from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from app.models.list import List, list_movies
from app.schemas.list import ListCreate, ListUpdate


class ListService:

    @staticmethod
    def create_list(db: Session, user_id: int, list_data: ListCreate) -> List:
        """Crear lista"""
        new_list = List(
            user_id=user_id,
            name=list_data.name,
            description=list_data.description,
            is_public=list_data.is_public,
            is_collaborative=list_data.is_collaborative
        )

        db.add(new_list)
        db.commit()
        db.refresh(new_list)
        return new_list

    @staticmethod
    def get_user_lists(db: Session, user_id: int):
        """Obtener listas del usuario"""
        lists = db.query(List).filter(List.user_id == user_id).all()

        # Agregar conteo de películas
        result = []
        for lst in lists:
            movies_count = db.execute(
                text("SELECT COUNT(*) FROM list_movies WHERE list_id = :list_id"),
                {"list_id": lst.id}
            ).scalar()

            list_dict = {
                "id": lst.id,
                "user_id": lst.user_id,
                "name": lst.name,
                "description": lst.description,
                "is_public": lst.is_public,
                "is_collaborative": lst.is_collaborative,
                "created_at": lst.created_at,
                "updated_at": lst.updated_at,
                "movies_count": movies_count or 0,
                "user": lst.user
            }
            result.append(list_dict)

        return result

    @staticmethod
    def get_list_detail(db: Session, list_id: int, user_id: int):
        """Obtener detalle de lista con películas"""
        lst = db.query(List).filter(List.id == list_id).first()

        if not lst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lista no encontrada"
            )

        # Verificar permisos
        if not lst.is_public and lst.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta lista"
            )

        # Obtener películas
        movies = db.execute(
            text("""
                SELECT movie_tmdb_id, added_at, position 
                FROM list_movies 
                WHERE list_id = :list_id 
                ORDER BY position, added_at DESC
            """),
            {"list_id": list_id}
        ).fetchall()

        movies_count = len(movies)

        return {
            "id": lst.id,
            "user_id": lst.user_id,
            "name": lst.name,
            "description": lst.description,
            "is_public": lst.is_public,
            "is_collaborative": lst.is_collaborative,
            "created_at": lst.created_at,
            "updated_at": lst.updated_at,
            "movies_count": movies_count,
            "user": lst.user,
            "movies": [
                {
                    "movie_tmdb_id": m[0],
                    "added_at": m[1],
                    "position": m[2]
                } for m in movies
            ]
        }

    @staticmethod
    def update_list(db: Session, list_id: int, user_id: int, list_data: ListUpdate) -> List:
        """Actualizar lista"""
        lst = db.query(List).filter(List.id == list_id, List.user_id == user_id).first()

        if not lst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lista no encontrada"
            )

        if list_data.name is not None:
            lst.name = list_data.name
        if list_data.description is not None:
            lst.description = list_data.description
        if list_data.is_public is not None:
            lst.is_public = list_data.is_public

        db.commit()
        db.refresh(lst)
        return lst

    @staticmethod
    def delete_list(db: Session, list_id: int, user_id: int) -> bool:
        """Eliminar lista"""
        lst = db.query(List).filter(List.id == list_id, List.user_id == user_id).first()

        if not lst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lista no encontrada"
            )

        db.delete(lst)
        db.commit()
        return True

    @staticmethod
    def add_movie_to_list(db: Session, list_id: int, user_id: int, movie_tmdb_id: int) -> bool:
        """Agregar película a lista"""
        lst = db.query(List).filter(List.id == list_id).first()

        if not lst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lista no encontrada"
            )

        # Verificar permisos
        if lst.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar esta lista"
            )

        # Verificar si ya existe
        existing = db.execute(
            text("SELECT id FROM list_movies WHERE list_id = :list_id AND movie_tmdb_id = :movie_id"),
            {"list_id": list_id, "movie_id": movie_tmdb_id}
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La película ya está en la lista"
            )

        # Agregar película
        db.execute(
            text("INSERT INTO list_movies (list_id, movie_tmdb_id, position) VALUES (:list_id, :movie_id, 0)"),
            {"list_id": list_id, "movie_id": movie_tmdb_id}
        )
        db.commit()
        return True

    @staticmethod
    def remove_movie_from_list(db: Session, list_id: int, user_id: int, movie_tmdb_id: int) -> bool:
        """Quitar película de lista"""
        lst = db.query(List).filter(List.id == list_id).first()

        if not lst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lista no encontrada"
            )

        # Verificar permisos
        if lst.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar esta lista"
            )

        # Eliminar película
        result = db.execute(
            text("DELETE FROM list_movies WHERE list_id = :list_id AND movie_tmdb_id = :movie_id"),
            {"list_id": list_id, "movie_id": movie_tmdb_id}
        )
        db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La película no está en la lista"
            )

        return True

    @staticmethod
    def check_movie_in_lists(db: Session, user_id: int, movie_tmdb_id: int):
        """Verificar en qué listas está una película"""
        lists = db.query(List).filter(List.user_id == user_id).all()

        result = []
        for lst in lists:
            in_list = db.execute(
                text("SELECT id FROM list_movies WHERE list_id = :list_id AND movie_tmdb_id = :movie_id"),
                {"list_id": lst.id, "movie_id": movie_tmdb_id}
            ).first()

            result.append({
                "list_id": lst.id,
                "list_name": lst.name,
                "in_list": in_list is not None
            })

        return result