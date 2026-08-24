"""Response models for the BLUETTI cloud API."""

from pydantic import BaseModel


class UserProduct(BaseModel):
    """A device/power station bound to a BLUETTI account."""

    sn: str
    stateList: list
    online: str
    model: str | None = None
    name: str | None = None
    isBindByCurUser: str | None = None
