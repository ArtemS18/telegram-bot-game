from marshmallow import Schema as MarshmallowSchema, fields, post_load

from app.store.tg_api.models import (
    CallbackQuery,
    Chat,
    EditMessageText,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    Message,
    Update,
    User,
)


class Schema(MarshmallowSchema):
    class Meta:
        unknown = "exclude"


class UserSchema(Schema):
    id = fields.Int(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(allow_none=True)
    username = fields.Str(allow_none=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class ChatSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(allow_none=True)

    @post_load
    def make_chat(self, data, **kwargs):
        return Chat(**data)


class MessageSchema(Schema):
    message_id = fields.Int(required=True)
    from_user = fields.Nested(UserSchema, data_key="from")
    date = fields.Int(required=True)
    chat = fields.Nested(ChatSchema, required=True)
    text = fields.Str(allow_none=True)

    @post_load
    def make_message(self, data, **kwargs):
        return Message(**data)


class InlineQuerySchema(Schema):
    id = fields.Int(required=True)
    from_user = fields.Nested(UserSchema, data_key="from")
    query = fields.Str(required=True)
    offset = fields.Str(required=True)

    @post_load
    def make_inline_query(self, data, **kwargs):
        return InlineQuery(**data)


class CallbackQuerySchema(Schema):
    id = fields.Int(required=True)
    from_user = fields.Nested(UserSchema, data_key="from")
    message = fields.Nested(MessageSchema, allow_none=True)
    data = fields.Str(required=True)

    @post_load
    def make_callback_query(self, data, **kwargs):
        return CallbackQuery(**data)


class InlineKeyboardButtonSchema(Schema):
    text = fields.Str(required=True)
    # url = fields.Str(allow_none=True, missing=None)
    callback_data = fields.Str(allow_none=True)

    @post_load
    def make_inline_keyboard_button(self, data, **kwargs):
        return InlineKeyboardButton(**data)


class InlineKeyboardMarkupSchema(Schema):
    inline_keyboard = fields.List(
        fields.List(fields.Nested(InlineKeyboardButtonSchema)), required=True
    )

    @post_load
    def make_inline_keyboard_markup(self, data, **kwargs):
        return InlineKeyboardMarkup(**data)


class UpdateSchema(Schema):
    update_id = fields.Int(required=True)
    message = fields.Nested(MessageSchema, allow_none=True)
    inline_query = fields.Nested(InlineQuerySchema, allow_none=True)
    callback_query = fields.Nested(CallbackQuerySchema, allow_none=True)

    @post_load
    def make_update(self, data, **kwargs):
        return Update(**data)


class EditMessageTextSchema(Schema):
    chat_id = fields.Str(required=True)
    message_id = fields.Str(required=True)
    text = fields.Str(required=True)

    @post_load
    def make_update(self, data, **kwargs):
        return EditMessageText(**data)
