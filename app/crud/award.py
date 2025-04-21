from typing import List, Optional, Dict, Any, Union
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.award import Award, UserAward
from app.schemas.award import AwardCreate, AwardUpdate, UserAwardCreate, UserAwardUpdate


class CRUDAward(CRUDBase[Award, AwardCreate, AwardUpdate]):
    def create(
        self, db: Session, *, obj_in: AwardCreate
    ) -> Award:
        obj_in_data = obj_in.dict()
        
        # Generate UUID for the award
        db_obj = Award(id=str(uuid.uuid4()), **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_category(
        self, db: Session, *, category: str
    ) -> List[Award]:
        return db.query(Award).filter(Award.category == category).all()
    
    def get_with_user_count(
        self, db: Session, *, id: str
    ) -> Dict[str, Any]:
        award = db.query(Award).filter(Award.id == id).first()
        if not award:
            return None
        
        user_count = db.query(UserAward).filter(UserAward.award_id == id).count()
        
        result = {
            **award.__dict__,
            "user_count": user_count
        }
        
        return result


class CRUDUserAward(CRUDBase[UserAward, UserAwardCreate, UserAwardUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: UserAwardCreate, user_id: str
    ) -> UserAward:
        obj_in_data = obj_in.dict()
        
        # Check if user already has this award
        existing = db.query(UserAward).filter(
            and_(
                UserAward.user_id == user_id,
                UserAward.award_id == obj_in_data["award_id"]
            )
        ).first()
        
        if existing:
            # Update existing award
            for field in obj_in_data:
                if hasattr(existing, field):
                    setattr(existing, field, obj_in_data[field])
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        
        # Generate UUID for the user award
        db_obj = UserAward(id=str(uuid.uuid4()), user_id=user_id, **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_user(
        self, db: Session, *, user_id: str
    ) -> List[UserAward]:
        return db.query(UserAward).filter(UserAward.user_id == user_id).all()
    
    def get_by_user_and_award(
        self, db: Session, *, user_id: str, award_id: str
    ) -> Optional[UserAward]:
        return db.query(UserAward).filter(
            and_(
                UserAward.user_id == user_id,
                UserAward.award_id == award_id
            )
        ).first()
    
    def check_user_has_award(
        self, db: Session, *, user_id: str, award_id: str
    ) -> bool:
        return db.query(UserAward).filter(
            and_(
                UserAward.user_id == user_id,
                UserAward.award_id == award_id
            )
        ).first() is not None


award = CRUDAward(Award)
user_award = CRUDUserAward(UserAward)
