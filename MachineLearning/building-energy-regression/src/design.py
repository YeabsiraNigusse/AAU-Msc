"""Validation shared by the API and the Streamlit form."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]


class BuildingDesign(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    relative_compactness: Annotated[float, Field(gt=0, le=1)]
    surface_area: Positive
    wall_area: Positive
    roof_area: Positive
    overall_height: Positive
    glazing_area: Annotated[float, Field(ge=0, le=1)]
    orientation: Annotated[int, Field(ge=2, le=5)]
    glazing_area_distribution: Annotated[int, Field(ge=0, le=5)]

    @model_validator(mode="after")
    def check_design(self):
        if max(self.wall_area, self.roof_area) > self.surface_area:
            raise ValueError("Wall and roof areas must each be at most the surface area")
        if (self.glazing_area == 0) != (self.glazing_area_distribution == 0):
            raise ValueError("Use distribution code 0 exactly when glazing area is zero")
        return self
