from marshmallow import Schema, fields


class UserRegisterSchema(Schema):
    email = fields.Str(
        required=True, description="email пользователя. До 256 символов")
    first_name = fields.Str(required=True)
    class_number = fields.Int(required=True)
    password = fields.Str(required=True)


class TokenResponseSchema(Schema):
    token = fields.Str(description="Токен для взаимодействия с аккаунтом")


class UserAuthSchema(Schema):
    identifier = fields.Str(required=True)
    password = fields.Str(required=True)


class SubjectSchema(Schema):
    subject = fields.Str()
    current_score = fields.Float()
    desired_score = fields.Float()


class UserProfileSchema(Schema):
    email = fields.Str()
    first_name = fields.Str()
    class_number = fields.Int()
    subjects = fields.List(fields.Nested(SubjectSchema))
    verified = fields.Bool(description="Верифицирован ли аккаунт")


class UserEditSchema(Schema):
    email = fields.Str(
        required=False, description="email пользователя. До 256 символов")
    first_name = fields.Str(required=False)
    class_number = fields.Int(required=False)
    password_old = fields.Str(required=False)
    password_new = fields.Str(required=False)
    subjects = fields.List(fields.Nested(SubjectSchema), required=False)


class UrlSchema(Schema):
    url = fields.Str(
        required=False, description="Ссылка на продление подписки")


class ErrorDetailSchema(Schema):
    """Схема для детального описания одной ошибки."""
    name = fields.Str(description="Имя параметра, вызвавшего ошибку")
    type = fields.Str(description="Тип ошибки (например, missing)")
    message = fields.Str(description="Сообщение об ошибке")
    value = fields.Raw(
        description="Значение параметра, если оно было передано", allow_none=True)


class Error400Schema(Schema):
    """Основная схема ответа с ошибками."""
    error = fields.Str(description="Общее сообщение об ошибке")
    errors = fields.List(fields.Nested(ErrorDetailSchema),
                         description="Список детальных ошибок")
    received_params = fields.Dict(
        description="Параметры, которые были успешно получены")


class AlreadyBeenTaken(Schema):
    name = fields.Str(description="Название переменной, которая занята")
    error = fields.Str(description="Описание, что переменная занята")


class ForgotPasswordSchema(Schema):
    identifier = fields.Str(
        required=True, description="Email или логин пользователя")
    new_password = fields.Str(required=True, description="Новый пароль")


class ForgotPasswordConfirmSchema(Schema):
    confirm = fields.Str(
        required=True, description="Код подтверждения для изменения пароля")
