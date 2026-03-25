from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
import models
import schemas

def get_owner_with_most_wings(db: Session):
    result = (db.query(
        models.Owner.id,
        models.Owner.email,
        models.Owner.first_name,
        models.Owner.last_name,
        func.count(models.Wing.id).label('wings_count')
    )
    .join(models.Wing)
    .group_by(models.Owner.id, models.Owner.email, models.Owner.first_name, models.Owner.last_name)
    .order_by(desc('wings_count'))
    .first())
    
    if result:
        return schemas.OwnerStats(
            owner_id=result[0],
            email=result[1],
            first_name=result[2],
            last_name=result[3],
            wings_count=result[4]
        )
    return None

def get_wings_by_owner_with_details(db: Session, owner_id: int):
    """Получить экспонаты владельца с детальной информацией о владельце и типе"""
    return (db.query(models.Wing)
            .options(
                joinedload(models.Wing.owner),
                joinedload(models.Wing.type)
            )
            .filter(models.Wing.owner_id == owner_id)
            .all())

# 📌 НОВЫЕ ФУНКЦИИ ДЛЯ РЕДАКТИРОВАНИЯ И УДАЛЕНИЯ
def update_wing(db: Session, wing_id: int, wing_update: schemas.WingCreate):
    """Обновить информацию об экспонате"""
    wing = db.query(models.Wing).filter(models.Wing.id == wing_id).first()
    if wing:
        for key, value in wing_update.dict().items():
            setattr(wing, key, value)
        db.commit()
        db.refresh(wing)
    return wing

def create_move(db: Session, move: schemas.MoveCreate):
    """Создать новое перемещение"""
    db_move = models.Move(**move.dict())
    db.add(db_move)
    db.commit()
    db.refresh(db_move)
    return db_move

def delete_move(db: Session, move_id: int):
    """Удалить перемещение"""
    move = db.query(models.Move).filter(models.Move.id == move_id).first()
    if move:
        db.delete(move)
        db.commit()
        return True
    return False

# Остальные функции остаются без изменений
def get_owner(db: Session, owner_id: int):
    return db.query(models.Owner).filter(models.Owner.id == owner_id).first()

def get_owner_by_email(db: Session, email: str):
    return db.query(models.Owner).filter(models.Owner.email == email).first()

def get_owners(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Owner).offset(skip).limit(limit).all()

def create_owner(db: Session, owner: schemas.OwnerCreate):
    db_owner = models.Owner(**owner.dict())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner

def get_wing(db: Session, wing_id: int):
    return db.query(models.Wing).filter(models.Wing.id == wing_id).first()

def get_wings_by_owner(db: Session, owner_id: int):
    return db.query(models.Wing).filter(models.Wing.owner_id == owner_id).all()

def create_wing(db: Session, wing: schemas.WingCreate):
    db_wing = models.Wing(**wing.dict())
    db.add(db_wing)
    db.commit()
    db.refresh(db_wing)
    return db_wing

def get_most_expensive_wing_move(db: Session):
    result = (db.query(models.Move)
             .order_by(desc(models.Move.price))
             .first())
    return result

def get_most_profitable_wing(db: Session):
    result = (db.query(
        models.Wing.id,
        models.Wing.name,
        func.sum(models.Move.price * models.Wing.profit * models.Place.scale).label('total_profit'),
        func.count(models.Move.id).label('total_moves')
    )
    .join(models.Move)
    .join(models.Place)
    .group_by(models.Wing.id, models.Wing.name)
    .order_by(desc('total_profit'))
    .first())
    
    if result:
        return schemas.WingProfitability(
            wing_id=result[0],
            wing_name=result[1],
            total_profit=result[2],
            total_moves=result[3],
            avg_profit_per_move=result[2] / result[3] if result[3] > 0 else 0
        )
    return None

def get_most_profitable_place(db: Session):
    result = (db.query(
        models.Place.id,
        models.Place.location,
        func.sum(models.Move.price * models.Wing.profit * models.Place.scale).label('total_revenue'),
        func.count(models.Move.id).label('total_moves')
    )
    .join(models.Move)
    .join(models.Wing)
    .group_by(models.Place.id, models.Place.location)
    .order_by(desc('total_revenue'))
    .first())
    
    if result:
        return schemas.PlaceProfitability(
            place_id=result[0],
            location=result[1],
            total_revenue=result[2],
            total_moves=result[3]
        )
    return None

def get_most_popular_type(db: Session):
    result = (db.query(
        models.Type.name,
        func.count(models.Wing.id).label('wings_count')
    )
    .join(models.Wing)
    .group_by(models.Type.name)
    .order_by(desc('wings_count'))
    .first())
    return {"name": result[0], "wings_count": result[1]}

def get_wing_move_frequency(db: Session, wing_id: int):
    moves_count = db.query(models.Move).filter(models.Move.wing_id == wing_id).count()
    first_move = db.query(models.Move).filter(models.Move.wing_id == wing_id).order_by(models.Move.dt).first()
    last_move = db.query(models.Move).filter(models.Move.wing_id == wing_id).order_by(desc(models.Move.dt)).first()
    
    if moves_count > 1 and first_move and last_move:
        days_diff = (last_move.dt - first_move.dt).days
        avg_days_between_moves = days_diff / (moves_count - 1) if moves_count > 1 else 0
        return {
            "wing_id": wing_id,
            "total_moves": moves_count,
            "avg_days_between_moves": avg_days_between_moves
        }
    return None

def get_owners_with_specific_lastname(db: Session):
    result = (
        db.query(
            models.Owner.id,
            models.Owner.last_name,
            models.Owner.first_name,
            models.Owner.middle_name
        )
        .filter(models.Owner.last_name.like('%ова'))
        .all()
    )
    return [
        {
            "id": r[0],
            "last_name": r[1],
            "first_name": r[2],
            "middle_name": r[3]
        }
        for r in result
    ]

