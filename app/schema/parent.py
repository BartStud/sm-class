from pydantic import BaseModel


class ProfileData(BaseModel):
    # keycloak data
    id: str | None = None
    name: str | None = None
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    username: str | None = None
