import asyncio
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from starlette import status  # Potrzebne do gather

from app import crud, models, schemas
from app.dependencies.auth import CurrentUserDep
from app.dependencies.db import DatabaseDep
from app.models.enums import ClassStudentStatus
from app.services import user_service_api  # Importuj klienta

router = APIRouter()


class ClassInfoForParent(schemas.SchoolClass):  # Dziedziczymy z SchoolClass
    student_id: str  # Dodajemy informację, które dziecko uczęszcza


@router.get(
    "/me/children/classes",
    response_model=List[ClassInfoForParent],  # Zwracamy listę klas z dodanym student_id
    summary="Parent: List classes attended by my children",
)
async def get_my_children_classes(
    *,
    db: DatabaseDep,
    current_user: CurrentUserDep,
    request: Request  # Inject Request object to get headers
) -> Any:
    """
    Retrieves a list of classes that the logged-in parent's children
    are actively participating in. Requires communication with UserService.
    """
    parent_id = current_user.get("sub")
    if not parent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # 1. Pobierz ID dzieci rodzica z UserService
    try:
        child_ids = await user_service_api.get_children_for_parent(parent_id, request)
    except HTTPException as e:
        # Przekazujemy błąd z klienta HTTP dalej
        raise e

    if not child_ids:
        return []  # Rodzic nie ma dzieci lub wystąpił błąd w UserService

    # 2. Dla każdego dziecka, znajdź jego AKTYWNE przypisania do klas w CollectionService
    tasks = []
    for student_id in child_ids:
        # Uruchamiamy zapytania równolegle
        tasks.append(
            crud.class_student.get_multi_by_student(
                db=db,
                student_id=student_id,
                status=ClassStudentStatus.ACTIVE,  # Tylko aktywne!
            )
        )

    results = await asyncio.gather(*tasks)

    # 3. Zbierz unikalne ID klas i połącz z ID studenta
    class_student_map: Dict[uuid.UUID, str] = {}  # Mapa class_id -> student_id
    active_class_ids = set()
    for student_assignments in results:
        for assignment in student_assignments:
            if (
                assignment.class_id not in class_student_map
            ):  # Weź pierwsze znalezione dziecko dla danej klasy
                class_student_map[assignment.class_id] = assignment.student_id
            active_class_ids.add(assignment.class_id)

    if not active_class_ids:
        return []

    # 4. Pobierz szczegóły tych klas
    # TODO: Potrzebujemy CRUD dla SchoolClass do pobierania wielu klas po ID
    # school_classes = await crud.school_class.get_multi_by_ids(db, ids=list(active_class_ids))
    # Zakładając, że taka funkcja istnieje:
    school_classes_db = await db.execute(
        select(models.SchoolClass).filter(models.SchoolClass.id.in_(active_class_ids))
    )
    school_classes = school_classes_db.scalars().all()

    # 5. Przygotuj odpowiedź, dodając student_id do danych klasy
    response_data = []
    for school_class in school_classes:
        class_info = ClassInfoForParent.from_orm(
            school_class
        )  # Użyj Pydantic do konwersji
        class_info.student_id = class_student_map.get(
            school_class.id, "unknown"
        )  # Powinno zawsze znaleźć
        response_data.append(class_info)

    return response_data
