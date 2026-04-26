from fastapi import HTTPException, Depends
from models.student_model import Student
from sqlalchemy.orm import Session
from models.db_model import Students as StudentDB
from database import get_db

class StudentController:
    @staticmethod
    def get_all(db: Session=Depends(get_db)) -> list[dict]:
        return db.query(StudentDB).all()
    
    @staticmethod
    def get_by_id(student_id: int, db: Session= Depends(get_db))->dict:
        student = db.query(StudentDB).filter(StudentDB.id == student_id).first()

        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student
    
    @staticmethod
    def create(student: Student, db: Session= Depends(get_db))->dict:
        new_student = StudentDB(**student.model_dump())
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student

    @staticmethod
    def update(student_id: int, update_data: Student, db: Session = Depends(get_db)) -> dict:
        student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        for key, value in update_data.model_dump().items():
            setattr(student, key, value)

        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def delete(student_id: int, db: Session = Depends(get_db)) -> dict:
        student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        db.delete(student)
        db.commit()
        return {"message": "Estudiante eliminado"}