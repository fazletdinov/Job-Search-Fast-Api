from fastapi_filter.contrib.sqlalchemy import Filter

from .models import Vacansy

class VacansyFilter(Filter):
    place_of_work: str | None = None
    place_of_work__in: list[str] | None = None
    required_specialt__in: list[str] | None = None
    required_experience__ilike: str | None = None
    custom_order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Vacansy
        ordering_field_name = "custom_order_by"
        search_model_fields = ["place_of_work", "required_specialt", "required_experience"]