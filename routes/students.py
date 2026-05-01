from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.student_model import Student
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController
from database import get_db

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/")
def get_students(db: Session = Depends(get_db), _=Depends(AuthController.require_auth)): 
    return StudentController.get_all(db)

@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db), _=Depends(AuthController.require_auth)):
    return StudentController.get_by_id(student_id,db)

@router.post("/")
def create_students(student: Student, db: Session = Depends(get_db), _=Depends(AuthController.require_auth)): 
    return StudentController.create(student,db)

@router.put("/{student_id}")
def update_student(student_id: int, update_data: Student, db: Session = Depends(get_db), _=Depends(AuthController.require_auth)): 
    return StudentController.update(student_id, update_data, db)

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), _=Depends(AuthController.require_auth)): 
    return StudentController.delete(student_id, db)