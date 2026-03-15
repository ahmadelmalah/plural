from sqladmin import ModelView

from app.models import Context, Persona, User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.username, User.created_at]
    column_searchable_list = [User.email, User.username]
    column_sortable_list = [User.id, User.email, User.username, User.created_at]
    column_default_sort = ("created_at", True)
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class ContextAdmin(ModelView, model=Context):
    column_list = [Context.id, Context.name, Context.description, Context.created_at]
    column_searchable_list = [Context.name]
    column_sortable_list = [Context.id, Context.name, Context.created_at]
    column_default_sort = ("name", False)
    name = "Context"
    name_plural = "Contexts"
    icon = "fa-solid fa-layer-group"


class PersonaAdmin(ModelView, model=Persona):
    column_list = [Persona.id, Persona.user_id, Persona.name, Persona.is_public, Persona.created_at]
    column_searchable_list = [Persona.name]
    column_sortable_list = [Persona.id, Persona.user_id, Persona.name, Persona.is_public, Persona.created_at]
    column_default_sort = ("created_at", True)
    name = "Persona"
    name_plural = "Personas"
    icon = "fa-solid fa-masks-theater"
