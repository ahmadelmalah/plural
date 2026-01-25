from sqladmin import ModelView

from app.models import Persona, User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.username, User.created_at]
    column_searchable_list = [User.email, User.username]
    column_sortable_list = [User.id, User.email, User.username, User.created_at]
    column_default_sort = ("created_at", True)
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class PersonaAdmin(ModelView, model=Persona):
    column_list = [Persona.id, Persona.user_id, Persona.name, Persona.is_public, Persona.created_at]
    column_searchable_list = [Persona.name]
    column_sortable_list = [Persona.id, Persona.user_id, Persona.name, Persona.is_public, Persona.created_at]
    column_default_sort = ("created_at", True)
    name = "Persona"
    name_plural = "Personas"
    icon = "fa-solid fa-masks-theater"
