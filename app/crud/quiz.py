from typing import List, Optional, Dict, Any, Union
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.quiz import Quiz, QuizQuestion, QuizAnswer, UserQuizAttempt
from app.schemas.quiz import (
    QuizCreate, QuizUpdate,
    QuizQuestionCreate, QuizQuestionUpdate,
    QuizAnswerCreate, QuizAnswerUpdate,
    UserQuizAttemptCreate, UserQuizAttemptUpdate
)


class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    def create_with_questions(
        self, db: Session, *, obj_in: QuizCreate
    ) -> Quiz:
        questions_data = obj_in.questions or []
        obj_in_data = obj_in.dict(exclude={"questions"})
        
        # Generate UUID for the quiz
        db_obj = Quiz(id=str(uuid.uuid4()), **obj_in_data)
        db.add(db_obj)
        db.flush()  # Flush to get the ID
        
        # Create questions
        for question_data in questions_data:
            self.create_question(db, quiz_id=db_obj.id, obj_in=question_data)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_question(
        self, db: Session, *, quiz_id: str, obj_in: QuizQuestionCreate
    ) -> QuizQuestion:
        answers_data = obj_in.answers or []
        obj_in_data = obj_in.dict(exclude={"answers"})
        
        # Generate UUID for the question
        db_obj = QuizQuestion(id=str(uuid.uuid4()), quiz_id=quiz_id, **obj_in_data)
        db.add(db_obj)
        db.flush()  # Flush to get the ID
        
        # Create answers
        for answer_data in answers_data:
            self.create_answer(db, question_id=db_obj.id, obj_in=answer_data)
        
        return db_obj
    
    def create_answer(
        self, db: Session, *, question_id: str, obj_in: QuizAnswerCreate
    ) -> QuizAnswer:
        obj_in_data = obj_in.dict()
        
        # Generate UUID for the answer
        db_obj = QuizAnswer(id=str(uuid.uuid4()), question_id=question_id, **obj_in_data)
        db.add(db_obj)
        return db_obj
    
    def get_by_content(
        self, db: Session, *, content_type: str, content_id: str
    ) -> Optional[Quiz]:
        return db.query(Quiz).filter(
            and_(
                Quiz.content_type == content_type,
                Quiz.content_id == content_id
            )
        ).first()
    
    def get_with_questions(
        self, db: Session, *, id: str
    ) -> Optional[Quiz]:
        return db.query(Quiz).filter(Quiz.id == id).first()
    
    def update_question(
        self, db: Session, *, db_obj: QuizQuestion, obj_in: Union[QuizQuestionUpdate, Dict[str, Any]]
    ) -> QuizQuestion:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle answers separately
        answers_data = update_data.pop("answers", None)
        
        # Update question fields
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        # Update answers if provided
        if answers_data:
            for answer_data in answers_data:
                if "id" in answer_data:
                    # Update existing answer
                    answer_id = answer_data.pop("id")
                    db_answer = db.query(QuizAnswer).filter(QuizAnswer.id == answer_id).first()
                    if db_answer:
                        for field in answer_data:
                            if hasattr(db_answer, field):
                                setattr(db_answer, field, answer_data[field])
                else:
                    # Create new answer
                    self.create_answer(db, question_id=db_obj.id, obj_in=QuizAnswerCreate(**answer_data))
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete_question(
        self, db: Session, *, id: str
    ) -> QuizQuestion:
        obj = db.query(QuizQuestion).filter(QuizQuestion.id == id).first()
        db.delete(obj)
        db.commit()
        return obj
    
    def delete_answer(
        self, db: Session, *, id: str
    ) -> QuizAnswer:
        obj = db.query(QuizAnswer).filter(QuizAnswer.id == id).first()
        db.delete(obj)
        db.commit()
        return obj


class CRUDUserQuizAttempt(CRUDBase[UserQuizAttempt, UserQuizAttemptCreate, UserQuizAttemptUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: UserQuizAttemptCreate, user_id: str
    ) -> UserQuizAttempt:
        obj_in_data = obj_in.dict()
        
        # Generate UUID for the attempt
        db_obj = UserQuizAttempt(id=str(uuid.uuid4()), user_id=user_id, **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_user_and_quiz(
        self, db: Session, *, user_id: str, quiz_id: str
    ) -> List[UserQuizAttempt]:
        return db.query(UserQuizAttempt).filter(
            and_(
                UserQuizAttempt.user_id == user_id,
                UserQuizAttempt.quiz_id == quiz_id
            )
        ).all()
    
    def get_latest_by_user_and_quiz(
        self, db: Session, *, user_id: str, quiz_id: str
    ) -> Optional[UserQuizAttempt]:
        return db.query(UserQuizAttempt).filter(
            and_(
                UserQuizAttempt.user_id == user_id,
                UserQuizAttempt.quiz_id == quiz_id
            )
        ).order_by(UserQuizAttempt.started_at.desc()).first()
    
    def get_best_by_user_and_quiz(
        self, db: Session, *, user_id: str, quiz_id: str
    ) -> Optional[UserQuizAttempt]:
        return db.query(UserQuizAttempt).filter(
            and_(
                UserQuizAttempt.user_id == user_id,
                UserQuizAttempt.quiz_id == quiz_id
            )
        ).order_by(UserQuizAttempt.score.desc()).first()


quiz = CRUDQuiz(Quiz)
user_quiz_attempt = CRUDUserQuizAttempt(UserQuizAttempt)
