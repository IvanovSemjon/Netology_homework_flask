import pydantic
from errors import HttpError


class BaseAdsRequest(pydantic.BaseModel):
    title: str
    text: str

    @pydantic.field_validator("text")
    @classmethod
    def secure_len_symbols(cls, v: str):
        if len(v) <= 10:
            raise ValueError("The ads is too short")
        return v

    @pydantic.field_validator("title")
    @classmethod
    def validate_title(cls, v: str):
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v


class CreateAdsRequest(BaseAdsRequest):
    pass


class UpdateAdsRequest(BaseAdsRequest):
    title: str | None = None
    text: str | None = None


class CreateUserRequest(pydantic.BaseModel):
    email: str
    password: str

    @pydantic.field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v


class UpdateUserRequest(pydantic.BaseModel):
    email: str | None = None
    password: str | None = None


class LoginRequest(pydantic.BaseModel):
    email: str
    password: str


def validate(
    schema: type[
        CreateAdsRequest
        | UpdateAdsRequest
        | CreateUserRequest
        | UpdateUserRequest
        | LoginRequest
    ],
    json_data: dict,
):
    try:
        schema_instance = schema(**json_data)
        return schema_instance.model_dump(exclude_none=True)
    except pydantic.ValidationError as er:
        errors = er.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)
