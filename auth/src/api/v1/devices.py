from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path

from schemas.device import DeviceDBSchema, DeviceGetSchema, DeviceUpdateSchema
from schemas.token import TokenPayload
from services.devices_service import DeviceService, get_device_service
from services.token_service import get_payload_from_token

router = APIRouter()

# TODO: добавить проверку что пользователь может только свои устройства смотреть и изменять (по user_id из токена)


@router.get(
    "/",
    response_model=list[DeviceDBSchema],
    description="Получение списка устройств пользователя",
    status_code=HTTPStatus.OK,
)
async def get_all_devices(
    device_service: Annotated[DeviceService, Depends(get_device_service)],
    token_payload: Annotated[TokenPayload, Depends(get_payload_from_token)],
) -> list[DeviceDBSchema]:
    devices = await device_service.list_devices_by_user_id(
        user_id=token_payload.user_id
    )
    return devices


@router.get(
    "/{device_id}",
    response_model=DeviceGetSchema,
    description="Получение информации об устройстве пользователя",
    status_code=HTTPStatus.OK,
)
async def get_device(
    device_service: Annotated[DeviceService, Depends(get_device_service)],
    device_id: str = Path(description="id устройства"),
) -> DeviceGetSchema | HTTPException:
    device = await device_service.get_device_by_id(device_id=UUID(device_id))
    return device


@router.patch(
    "/{device_id}",
    response_model=DeviceGetSchema,
    description="Изменение устройства пользователя",
    status_code=HTTPStatus.OK,
)
async def update_device(
    device_service: Annotated[DeviceService, Depends(get_device_service)],
    device_id: UUID = Path(description="id устройства"),
    device_update_data: DeviceUpdateSchema = Body(
        description="Введите новые данные устройства"
    ),
) -> DeviceGetSchema | HTTPException:
    device = await device_service.update_device(
        device_id=device_id, device_update_data=device_update_data
    )
    return device


@router.delete(
    "/{device_id}",
    description="Удаление устройства пользователя",
    status_code=HTTPStatus.OK,
    response_model=None,
)
async def delete_device(
    device_service: Annotated[DeviceService, Depends(get_device_service)],
    device_id: UUID = Path(description="id устройства"),
) -> dict[str, str] | HTTPException:
    await device_service.delete_device(device_id=device_id)
    return {"status": "устройство удалено"}
