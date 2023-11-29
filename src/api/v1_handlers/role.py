from uuid import UUID
import logging
import logging.config

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.role import ResponseRole, RequestNewRoleToUser, RequestRole
from src.services.role import RoleService, get_role_service
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

role_router = APIRouter(prefix="/role")


@role_router.post("/new",
                  response_model=ResponseRole,
                  summary="Отправить запрос на создание новой роли",
                  description="Создает новую роль и возвращает новый объект role",
                  response_description="object Role")
async def create_new_role(role_body: RequestRole,
                          role_service: RoleService = Depends(get_role_service)) -> ResponseRole:
    new_role = await role_service.create_role(role_body.name)
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не удалось создать роль"
        )
    return new_role


@role_router.patch("/update",
                   response_model=ResponseRole,
                   summary="запрос на обновление существующей роли",
                   description="Обновляет существующую роль и возвращает новый объект role",
                   response_description="object Role")
async def update_existed_role(role_id: UUID,
                              role_body: RequestRole,
                              role_service: RoleService = Depends(get_role_service)) -> ResponseRole:
    updated_role = await role_service.update_role(role_id, role_body.name)
    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Роль не обновлена"
        )
    return ResponseRole(id=updated_role.id, name=updated_role.name)


@role_router.get("/",
                 response_model=ResponseRole,
                 summary="запрос на существующую роль",
                 description="Получает существующую роль и возвращает новый объект role",
                 response_description="object Role")
async def get_existed_role(role_id: UUID,
                           role_service: RoleService = Depends(get_role_service)) -> ResponseRole:
    role = await role_service.read_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не существует"
        )
    return ResponseRole(id=role.id, name=role.name)


@role_router.delete("/",
                    response_model=bool,
                    summary="Запрос на удаление существующей роли",
                    description="Удаляет существующую роль и возвращает объект bool",
                    response_description="True or False")
async def delete_existed_role(role_id: UUID,
                              role_service: RoleService = Depends(get_role_service)):
    delete_role_id = await role_service.delete_role(role_id)
    if not delete_role_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не найдена"
        )
    return bool(delete_role_id)


@role_router.get("/user",
                 response_model=list[ResponseRole],
                 summary="Запрос на получение роли пользователя",
                 description="Получение списка ролей пользователя",
                 response_description="UUID, name")
async def get_user_role(user_id: UUID,
                        role_service: RoleService = Depends(get_role_service)):
    log_msg = f'{user_id=}, {role_service=}'
    log.debug(log_msg)
    roles = await role_service.get_user_access_area(user_id)
    log_msg = f'{roles=}'
    log.debug(log_msg)
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role не обнаружен"
        )
    return roles


@role_router.post("/role-to-user",
                  response_model=bool,
                  summary="Запрос на добавление новой роли пользователю",
                  description="Добавьте новую роль пользователю",
                  response_description="True or False")
async def set_role_to_user(role_body: RequestNewRoleToUser,
                           role_service: RoleService = Depends(get_role_service)):
    updated_user = await role_service.set_role_to_user(role_body.user_id, role_body.role_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не найдена"
        )
    return bool(updated_user)


@role_router.delete("/role-to-user",
                    response_model=bool,
                    summary="Запрос на удаление роли пользователя",
                    description="Удаление роли у пользователя",
                    response_description="True or False")
async def remove_from_role_user(role_body: RequestNewRoleToUser,
                                role_service: RoleService = Depends(get_role_service)):
    updated_user = await role_service.remove_role_from_user(role_body.user_id,
                                                            role_body.role_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не найдена"
        )
    return bool(updated_user)
