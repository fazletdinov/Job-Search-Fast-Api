from fastapi_filter.contrib.sqlalchemy import Filter

from src.database.models import Vacansy, Resume


class VacansyFilter(Filter):
    place_of_work: str | None = None
    place_of_work__in: list[str] | None = None
    required_specialt__in: list[str] | None = None
    required_experience__ilike: str | None = None
    custom_order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Vacansy
        ordering_field_name = "custom_order_by"
        search_model_fields = ["place_of_work",
                               "required_specialt", "required_experience"]


class ResumeFilter(Filter):
    first_name__ilike: str | None = None
    age__in: list[int] | None = None
    experience__in: list[str] | None = None
    education__in: list[str] | None = None
    custom_order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Resume
        ordering_field_name = "custom_order_by"
        search_model_fields = ["first_name", "age", "experience", "education"]
