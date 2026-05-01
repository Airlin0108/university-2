from pydantic import BaseModel, Field

class Student(BaseModel):
    name: str = Field(..., min_length=2, description="Nombre completo del estudiante")
    age: int = Field(..., gt=0, description="Edad del estudiante en años")
    grade: float = Field(..., ge=0, le=5, description="Nota del estudiante entre 0.0 y 5.0")

class StudentResponse(Student):
    id: int