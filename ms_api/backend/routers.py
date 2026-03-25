from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, join, and_
from typing import List, Dict, Any
import crud, schemas
from database import get_db, get_sql_queries
import models

router = APIRouter()

def create_response_with_sql(data: Any) -> Dict[str, Any]:
    """Создает ответ с добавлением SQL запросов"""
    sql_queries = get_sql_queries()
    
    response_data = {
        "data": data,
        "sql": [
            {
                'query': query['statement'].strip(),
                'parameters': str(query['parameters']),
                'executemany': query['executemany']
            } for query in sql_queries
        ]
    }
    return response_data

# ==================== ВЛАДЕЛЬЦЫ (OWNERS) ====================
@router.get("/owners/", tags=["👥 Владельцы"])
def read_owners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех владельцев экспонатов"""
    owners = crud.get_owners(db, skip=skip, limit=limit)
    return create_response_with_sql(owners)

@router.get("/owners/{owner_id}", tags=["👥 Владельцы"])
def read_owner(owner_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном владельце по ID"""
    db_owner = crud.get_owner(db, owner_id=owner_id)
    if db_owner is None:
        raise HTTPException(status_code=404, detail="Владелец не найден")
    return create_response_with_sql(db_owner)

@router.get("/owners/{email}/wings", tags=["👥 Владельцы"])
def get_owner_wings_by_email(email: str, db: Session = Depends(get_db)):
    """Получить все экспонаты владельца по email"""
    owner = crud.get_owner_by_email(db, email)
    if not owner:
        raise HTTPException(status_code=404, detail="Владелец не найден")
    
    wings = crud.get_wings_by_owner_with_details(db, owner.id)
    return create_response_with_sql(wings)

# ==================== ЭКСПОНАТЫ (WINGS) ====================
@router.get("/wings/", tags=["🖼️ Экспонаты"])
def read_wings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех экспонатов"""
    wings = db.query(models.Wing).offset(skip).limit(limit).all()
    return create_response_with_sql(wings)

@router.get("/wings/{wing_id}", tags=["🖼️ Экспонаты"])
def read_wing(wing_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном экспонате по ID"""
    wing = crud.get_wing(db, wing_id=wing_id)
    if not wing:
        raise HTTPException(status_code=404, detail="Экспонат не найден")
    return create_response_with_sql(wing)

@router.put("/wings/{wing_id}", tags=["🖼️ Экспонаты"])
def update_wing(wing_id: int, wing_update: schemas.WingCreate, db: Session = Depends(get_db)):
    """Редактировать информацию об экспонате"""
    # Проверяем существование экспоната
    existing_wing = crud.get_wing(db, wing_id=wing_id)
    if not existing_wing:
        raise HTTPException(status_code=404, detail="Экспонат не найден")
    
    # Проверяем существование владельца
    owner = crud.get_owner(db, owner_id=wing_update.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Владелец не найден")
    
    # Проверяем существование типа
    wing_type = db.query(models.Type).filter(models.Type.id == wing_update.type_id).first()
    if not wing_type:
        raise HTTPException(status_code=404, detail="Тип экспоната не найден")
    
    # Обновляем экспонат
    updated_wing = crud.update_wing(db, wing_id=wing_id, wing_update=wing_update)
    return create_response_with_sql(updated_wing)

# ==================== ПЕРЕМЕЩЕНИЯ (MOVES) ====================
@router.get("/moves/", tags=["🚚 Перемещения"])
def read_moves(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех перемещений экспонатов"""
    moves = db.query(models.Move).offset(skip).limit(limit).all()
    return create_response_with_sql(moves)

@router.post("/moves/", tags=["🚚 Перемещения"])
def create_move(move: schemas.MoveCreate, db: Session = Depends(get_db)):
    """Создать новое перемещение экспоната"""
    # Проверяем существование экспоната
    wing = crud.get_wing(db, wing_id=move.wing_id)
    if not wing:
        raise HTTPException(status_code=404, detail="Экспонат не найден")
    
    # Проверяем существование места
    place = db.query(models.Place).filter(models.Place.id == move.place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Место выставки не найдено")
    
    # Создаем перемещение
    new_move = crud.create_move(db, move=move)
    return create_response_with_sql(new_move)

@router.delete("/moves/{move_id}", tags=["🚚 Перемещения"])
def delete_move(move_id: int, db: Session = Depends(get_db)):
    """Удалить перемещение по ID"""
    # Проверяем существование перемещения
    existing_move = db.query(models.Move).filter(models.Move.id == move_id).first()
    if not existing_move:
        raise HTTPException(status_code=404, detail="Перемещение не найдено")
    
    # Удаляем перемещение
    result = crud.delete_move(db, move_id=move_id)
    return create_response_with_sql({"message": "Перемещение успешно удалено", "deleted_id": move_id})

# ==================== МЕСТА ВЫСТАВОК (PLACES) ====================
@router.get("/places/", tags=["🏛️ Места выставок"])
def read_places(db: Session = Depends(get_db)):
    """Получить список всех мест выставок"""
    places = db.query(models.Place).all()
    return create_response_with_sql(places)

@router.get("/places/{place_id}", tags=["🏛️ Места выставок"])
def read_place(place_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном месте выставки по ID"""
    place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Место выставки не найдено")
    return create_response_with_sql(place)

# ==================== ТИПЫ ЭКСПОНАТОВ (TYPES) ====================
@router.get("/types/", tags=["🏷️ Типы экспонатов"])
def read_types(db: Session = Depends(get_db)):
    """Получить список всех типов экспонатов"""
    types = db.query(models.Type).all()
    return create_response_with_sql(types)

@router.get("/types/{type_id}", tags=["🏷️ Типы экспонатов"])
def read_type(type_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном типе экспоната по ID"""
    wing_type = db.query(models.Type).filter(models.Type.id == type_id).first()
    if not wing_type:
        raise HTTPException(status_code=404, detail="Тип экспоната не найден")
    return create_response_with_sql(wing_type)

# ==================== АНАЛИТИКА (ANALYTICS) ====================
@router.get("/analytics/owner-most-wings", tags=["📊 Аналитика"])
def get_owner_with_most_wings(db: Session = Depends(get_db)):
    """Владелец с наибольшим количеством экспонатов"""
    result = crud.get_owner_with_most_wings(db)
    return create_response_with_sql(result)

@router.get("/analytics/most-expensive-wing", tags=["📊 Аналитика"])
def get_most_expensive_wing_move(db: Session = Depends(get_db)):
    """Самый дорогой экспонат в передвижении"""
    move = crud.get_most_expensive_wing_move(db)
    if not move:
        raise HTTPException(status_code=404, detail="Перемещения не найдены")
    
    result = {
        "wing_id": move.wing_id,
        "wing_name": move.wing.name,
        "price": move.price,
        "date": move.dt.isoformat() if move.dt else None
    }
    return create_response_with_sql(result)

@router.get("/analytics/most-profitable-wing", tags=["📊 Аналитика"])
def get_most_profitable_wing(db: Session = Depends(get_db)):
    """Самый прибыльный экспонат"""
    result = crud.get_most_profitable_wing(db)
    if not result:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    return create_response_with_sql(result)

@router.get("/analytics/most-profitable-place", tags=["📊 Аналитика"])
def get_most_profitable_place(db: Session = Depends(get_db)):
    """Самое прибыльное место выставки"""
    result = crud.get_most_profitable_place(db)
    if not result:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    return create_response_with_sql(result)

@router.get("/analytics/most-popular-type", tags=["📊 Аналитика"])
def get_most_popular_type(db: Session = Depends(get_db)):
    """Самый популярный тип экспоната"""
    result = crud.get_most_popular_type(db)
    return create_response_with_sql(result)

@router.get("/analytics/wing-move-frequency/{wing_id}", tags=["📊 Аналитика"])
def get_wing_move_frequency(wing_id: int, db: Session = Depends(get_db)):
    """Частота передвижения конкретного экспоната"""
    result = crud.get_wing_move_frequency(db, wing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Перемещения для этого экспоната не найдены")
    return create_response_with_sql(result)

@router.get("/analytics/owners_with_specific_lastname", tags=["📊 Аналитика"])
def get_owners_with_specific_lastname(db: Session = Depends(get_db)):
    """Найти всех владельцев, фамилии которых заканчиваются на «ова» """
    result = crud.get_owners_with_specific_lastname(db)
    if result is None:
        raise HTTPException(status_code=404, detail="Таких фамилий нет")
    return create_response_with_sql(result)

# ==================== НОВЫЙ ENDPOINT ДЛЯ ЗАДАНИЯ 9 ====================
@router.get("/analytics/premium-exponats", tags=["📊 Аналитика"])
def get_premium_exponats(
    db: Session = Depends(get_db),
    limit: int = 10,
    min_price: float = 30000.0
):
    """
    Возвращает список самых дорогих перемещений экспонатов (price > 30000).
    Топ-10 самых дорогих экспонатов для рекламных кампаний.
    """
    # Формируем запрос с JOIN таблиц moves, wings и types
    query = (
        select(
            models.Move.id.label("move_id"),
            models.Wing.name.label("wing_name"),
            models.Type.name.label("type_name"),
            models.Move.price
        )
        .join(models.Wing, models.Move.wing_id == models.Wing.id)
        .join(models.Type, models.Wing.type_id == models.Type.id)
        .where(models.Move.price > min_price)
        .order_by(models.Move.price.desc())
        .limit(limit)
    )
    
    # Выполняем запрос
    result = db.execute(query)
    premium_exponats = result.all()
    
    # Преобразуем результат в список словарей для правильного форматирования
    formatted_result = []
    for row in premium_exponats:
        formatted_result.append({
            "move_id": row.move_id,
            "wing_name": row.wing_name,
            "type_name": row.type_name,
            "price": float(row.price)  # Преобразуем в float для корректного JSON
        })
    
    # Возвращаем результат через стандартную обертку с SQL запросами
    return create_response_with_sql(formatted_result)

# ==================== НОВЫЙ ENDPOINT ДЛЯ ЗАДАНИЯ 9 (ПРОДВИНУТЫЙ УРОВЕНЬ) ====================
@router.get("/analytics/spb-places-above-average", tags=["📊 Аналитика"])
def get_spb_places_above_average(
    db: Session = Depends(get_db)
):
    """
    Показывает площадки в Санкт-Петербурге с масштабом выше среднего.
    Продвинутый уровень задания 9.
    """
    from sqlalchemy import func
    
    # 1. Вычисляем средний масштаб по всем площадкам
    avg_scale_result = db.query(func.avg(models.Place.scale)).scalar()
    avg_scale = float(avg_scale_result) if avg_scale_result else 0
    
    # 2. Ищем площадки в Санкт-Петербурге с масштабом выше среднего
    #    Используем LIKE для поиска "Санкт-Петербург", "СПб", "Saint Petersburg" и т.д.
    places = db.query(models.Place).filter(
        models.Place.location.contains("Санкт-Петербург") |
        models.Place.location.contains("СПб") |
        models.Place.location.contains("Saint Petersburg") |
        models.Place.location.contains("Spb"),
        models.Place.scale > avg_scale
    ).all()
    
    # 3. Форматируем результат
    formatted_result = []
    for place in places:
        formatted_result.append({
            "place_id": place.id,
            "location": place.location,
            "scale": float(place.scale),
            "average_scale": avg_scale
        })
    
    # 4. Если ничего не найдено, возвращаем понятное сообщение
    if not formatted_result:
        return create_response_with_sql({
            "message": "Площадки в Санкт-Петербурге с масштабом выше среднего не найдены",
            "average_scale": avg_scale
        })
    
    return create_response_with_sql(formatted_result)


# ==================== НОВЫЙ ENDPOINT ДЛЯ ЗАДАНИЯ 9 (ПРОСТОЙ УРОВЕНЬ) ====================
@router.get("/analytics/spb-places", tags=["📊 Аналитика"])
def get_spb_places(
    db: Session = Depends(get_db)
):
    """
    Находит все выставочные площадки в Санкт-Петербурге.
    Простой уровень задания 9.
    """
    # Ищем все площадки в Санкт-Петербурге (без фильтра по масштабу)
    places = db.query(models.Place).filter(
        models.Place.location.contains("Санкт-Петербург") |
        models.Place.location.contains("СПб") |
        models.Place.location.contains("Saint Petersburg") |
        models.Place.location.contains("Spb")
    ).all()
    
    # Форматируем результат
    formatted_result = []
    for place in places:
        formatted_result.append({
            "place_id": place.id,
            "location": place.location,
            "scale": float(place.scale)
        })
    
    # Если ничего не найдено, возвращаем понятное сообщение
    if not formatted_result:
        return create_response_with_sql({
            "message": "Площадки в Санкт-Петербурге не найдены"
        })
    
    return create_response_with_sql(formatted_result)