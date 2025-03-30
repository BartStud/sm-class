import uuid
from typing import List, Any, Optional

from fastapi import APIRouter, HTTPException, status, Query

from app import crud, schemas
from app.dependencies.db import DatabaseDep
from app.dependencies.auth import CurrentUserDep
from app.schemas.class_student import ClassStudentRequestCreate, ClassStudentStatus

router = APIRouter()


@router.post(
    "/", response_model=schemas.SchoolClass, status_code=status.HTTP_201_CREATED
)
async def create_school_class(
    *,
    db: DatabaseDep,
    class_in: schemas.SchoolClassCreate,
    current_user: CurrentUserDep,  # Add authorization check if needed
) -> Any:
    """
    Create new school class. (Permissions check might be needed)
    """
    # Add permission check: e.g., if current_user['realm_access']['roles'] has 'admin'
    new_class = await crud.school_class.create(db=db, obj_in=class_in)
    return new_class


@router.get("/", response_model=List[schemas.SchoolClass])
async def read_school_classes(
    db: DatabaseDep,
    current_user: CurrentUserDep,  # Might filter based on user or just require auth
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve school classes.
    """
    classes = await crud.school_class.get_multi(db, skip=skip, limit=limit)
    return classes


@router.get("/{class_id}", response_model=schemas.SchoolClass)
async def read_school_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    current_user: CurrentUserDep,  # Check if user is related to the class?
) -> Any:
    """
    Get school class by ID.
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")
    # Add permission check if necessary
    return school_class


@router.put("/{class_id}", response_model=schemas.SchoolClass)
async def update_school_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    class_in: schemas.SchoolClassUpdate,
    current_user: CurrentUserDep,  # Check permissions
) -> Any:
    """
    Update a school class.
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")
    # Add permission check (e.g., is user an admin or collector for this class?)
    updated_class = await crud.school_class.update(
        db=db, db_obj=school_class, obj_in=class_in
    )
    return updated_class


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    current_user: CurrentUserDep,  # Check permissions (likely admin only)
) -> None:
    """
    Delete a school class. (Ensure cascade deletes are intended)
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")
    # Add permission check (e.g., admin role)
    await crud.school_class.remove(db=db, id=class_id)
    return None  # Return None for 204


# --- Endpoints for related models (ClassStudent, ClassCollector) ---


# @router.post(
#     "/{class_id}/students/",
#     response_model=schemas.ClassStudent,
#     status_code=status.HTTP_201_CREATED,
# )
# async def add_student_to_class(
#     *,
#     db: DatabaseDep,
#     class_id: uuid.UUID,
#     student_in: schemas.ClassStudentCreate,
#     current_user: CurrentUserDep,  # Check permissions (e.g., collector/admin)
# ) -> Any:
#     """
#     Add a student to a specific class.
#     """
#     school_class = await crud.school_class.get(db=db, id=class_id)
#     if not school_class:
#         raise HTTPException(status_code=404, detail="School Class not found")
#     # Add permission checks
#     # TODO: Check if student_id exists in Keycloak?
#     class_student = await crud.class_student.create_for_class(
#         db=db, obj_in=student_in, class_id=class_id
#     )
#     return class_student


# Modyfikacja endpointu listującego studentów, aby filtrował po statusie
@router.get(
    "/{class_id}/students/",
    response_model=List[schemas.ClassStudent],
    summary="List students in a class (filter by status)",
)
async def list_students_in_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.ClassStudentStatus] = Query(
        None, description="Filter by student status (e.g., pending, active)"
    ),  # Filtr statusu
) -> Any:
    """
    List students assigned to a specific class.
    Can be filtered by status (e.g., to show pending requests for collectors).
    Requires appropriate permissions.
    """
    # Sprawdź, czy klasa istnieje
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    # TODO: Sprawdź uprawnienia - czy current_user jest skarbnikiem tej klasy LUB rodzicem dziecka w tej klasie LUB adminem?
    # is_collector = await crud.class_collector.is_active_collector_for_class(db, user_id=current_user['sub'], class_id=class_id)
    # if not is_collector and not is_admin... :
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view students for this class")

    students = await crud.class_student.get_multi_by_class(
        db=db,
        class_id=class_id,
        skip=skip,
        limit=limit,
        status=status,  # Przekaż filtr statusu
    )
    return students


@router.put(
    "/{class_id}/students/{class_student_id}", response_model=schemas.ClassStudent
)
async def update_class_student_assignment(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    class_student_id: uuid.UUID,
    student_in: schemas.ClassStudentUpdate,  # Schema do aktualizacji (np. tylko data 'end')
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. collector/admin)
) -> Any:
    """
    Update details of a student's assignment to a class (e.g., set end date).
    """
    # Sprawdź, czy klasa istnieje
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    # Pobierz konkretne przypisanie studenta
    class_student = await crud.class_student.get(db=db, id=class_student_id)
    if not class_student or class_student.class_id != class_id:
        raise HTTPException(
            status_code=404, detail="Class-Student assignment not found for this class"
        )

    # TODO: Sprawdź uprawnienia (np. czy current_user jest adminem lub skarbnikiem tej klasy)

    updated_assignment = await crud.class_student.update(
        db=db, db_obj=class_student, obj_in=student_in
    )
    return updated_assignment


@router.delete(
    "/{class_id}/students/{class_student_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_student_from_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    class_student_id: uuid.UUID,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. collector/admin)
) -> None:
    """
    Remove a student's assignment record from a class (Hard delete).
    Consider using PUT to set an end date instead for historical tracking.
    """
    # Sprawdź, czy klasa istnieje
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    # Pobierz przypisanie
    class_student = await crud.class_student.get(db=db, id=class_student_id)
    if not class_student or class_student.class_id != class_id:
        raise HTTPException(
            status_code=404, detail="Class-Student assignment not found for this class"
        )

    # TODO: Sprawdź uprawnienia

    await crud.class_student.remove(db=db, id=class_student_id)
    return None


# --- ClassCollector Endpoints ---


@router.post(
    "/{class_id}/collectors/",
    response_model=schemas.ClassCollector,
    status_code=status.HTTP_201_CREATED,
)
async def add_collector_to_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    collector_in: schemas.ClassCollectorCreate,  # Zawiera parent_id, start, end
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. admin)
) -> Any:
    """
    Assign a collector (parent) to a specific class.
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    # TODO: Sprawdź uprawnienia (np. tylko admin może dodawać skarbników?)
    # TODO: Opcjonalnie sprawdź, czy parent_id istnieje w Keycloak

    class_collector = await crud.class_collector.create_for_class(
        db=db, obj_in=collector_in, class_id=class_id
    )
    return class_collector


@router.get("/{class_id}/collectors/", response_model=List[schemas.ClassCollector])
async def list_collectors_for_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. członek klasy/admin)
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,  # Opcjonalny parametr do filtrowania aktywnych
) -> Any:
    """
    List collectors assigned to a specific class.
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    # TODO: Sprawdź uprawnienia

    collectors = await crud.class_collector.get_multi_by_class(
        db=db, class_id=class_id, skip=skip, limit=limit, only_active=active_only
    )
    return collectors


@router.put(
    "/{class_id}/collectors/{class_collector_id}", response_model=schemas.ClassCollector
)
async def update_class_collector_assignment(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    class_collector_id: uuid.UUID,
    collector_in: schemas.ClassCollectorUpdate,  # Schema do aktualizacji (np. data 'end')
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. admin)
) -> Any:
    """
    Update details of a collector's assignment (e.g., set end date).
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    class_collector = await crud.class_collector.get(db=db, id=class_collector_id)
    if not class_collector or class_collector.class_id != class_id:
        raise HTTPException(
            status_code=404,
            detail="Class-Collector assignment not found for this class",
        )

    # TODO: Sprawdź uprawnienia

    updated_assignment = await crud.class_collector.update(
        db=db, db_obj=class_collector, obj_in=collector_in
    )
    return updated_assignment


@router.delete(
    "/{class_id}/collectors/{class_collector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_collector_from_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    class_collector_id: uuid.UUID,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. admin)
) -> None:
    """
    Remove a collector's assignment record from a class (Hard delete).
    """
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    class_collector = await crud.class_collector.get(db=db, id=class_collector_id)
    if not class_collector or class_collector.class_id != class_id:
        raise HTTPException(
            status_code=404,
            detail="Class-Collector assignment not found for this class",
        )

    # TODO: Sprawdź uprawnienia

    await crud.class_collector.remove(db=db, id=class_collector_id)
    return None


@router.post(
    "/{class_id}/request-student-join",  # Zmieniona ścieżka dla jasności
    response_model=schemas.ClassStudent,
    status_code=status.HTTP_201_CREATED,
    summary="Parent: Request to add own child to a class",
)
async def request_add_student_to_class(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    request_in: ClassStudentRequestCreate,  # Oczekuje tylko student_id
    current_user: CurrentUserDep,  # To jest rodzic
) -> Any:
    """
    Endpoint for a logged-in parent to request adding their child
    (specified by student_id) to a specific class (class_id).
    Creates a ClassStudent entry with PENDING status.
    """
    parent_id = current_user.get("sub")
    if not parent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # --- WAŻNE: Weryfikacja Własności Dziecka ---
    # Tutaj POWINNA nastąpić weryfikacja, czy student_id z request_in
    # rzeczywiście należy do zalogowanego rodzica (parent_id).
    # Wymaga to wywołania UserService.
    # Zostawiam TODO, bo wymaga klienta HTTP i konfiguracji.
    # is_owner = await user_service_client.verify_child_ownership(parent_id, request_in.student_id, token=request.headers.get("Authorization"))
    # if not is_owner:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only request to add your own children.")
    # --- Koniec Weryfikacji ---

    # Sprawdź, czy klasa istnieje
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="School Class not found"
        )

    try:
        class_student_request = await crud.class_student.create_request(
            db=db,
            obj_in=request_in,
            class_id=class_id,
            requested_by_parent_id=parent_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return class_student_request


@router.patch(
    "/{class_id}/students/{class_student_id}/status",
    response_model=schemas.ClassStudent,
    summary="Collector: Approve or reject a pending student join request",
)
async def update_class_student_status(
    *,
    db: DatabaseDep,
    class_id: uuid.UUID,
    class_student_id: uuid.UUID,
    status_update: schemas.ClassStudentStatusUpdate,  # Oczekuje np. {"status": "active"}
    current_user: CurrentUserDep,  # To powinien być skarbnik
) -> Any:
    """
    Endpoint for a Class Collector to change the status of a student's
    assignment to a class (e.g., approve PENDING to ACTIVE, or REJECTED).
    Requires collector permissions for the class.
    """
    collector_id = current_user.get("sub")
    if not collector_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Sprawdź, czy klasa istnieje
    school_class = await crud.school_class.get(db=db, id=class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="School Class not found")

    # --- WAŻNE: Sprawdzenie uprawnień Skarbnika ---
    # TODO: Sprawdź, czy collector_id jest AKTYWNYM skarbnikiem DLA TEJ KLASY (class_id)
    # is_collector = await crud.class_collector.is_active_collector_for_class(db, user_id=collector_id, class_id=class_id)
    # if not is_collector:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an active collector for this class.")
    # --- Koniec Sprawdzania Uprawnień ---

    # Pobierz przypisanie studenta
    class_student = await crud.class_student.get(db=db, id=class_student_id)
    if not class_student or class_student.class_id != class_id:
        raise HTTPException(
            status_code=404, detail="Class-Student assignment not found for this class"
        )

    # Sprawdź, czy status dozwolony (np. nie można odrzucić już aktywnego?)
    if (
        class_student.status == ClassStudentStatus.ACTIVE
        and status_update.status != ClassStudentStatus.ENDED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status of an already active student, except to 'ended'.",
        )
    if class_student.status == ClassStudentStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status of a rejected request.",
        )

    try:
        updated_assignment = await crud.class_student.update_status(
            db=db, db_obj=class_student, new_status=status_update.status
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return updated_assignment
