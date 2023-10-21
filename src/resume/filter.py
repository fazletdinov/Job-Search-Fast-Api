from fastapi_filter.contrib.sqlalchemy import Filter

from .models import Resume

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