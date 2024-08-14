# class FieldType(str, Enum):
#     """Field Type Enum."""

#     TRADE_DATA = "trade_data"
#     MARKET_DATA = "market_data"
#     SIGNAL_DATA = "signal_data"
#     DATE_DATA = "date_data"


# class EvaluateField(BaseModel):
#     """Evaluate Field Model."""

#     field: str = Field(
#         description="The field name to evaluate.",
#         examples=["SPX Index", "trade_date", "expiry_date", "price", "volume"],
#     )
#     field_type: FieldType = Field(
#         description="The field type to be evaluated.",
#         examples=["trade_data", "market_data", "signal_data"],
#     )


# class ComparisonField(BaseModel):
#     """Comparison Field Model."""

#     field: str | None = Field(
#         default=None,
#         description="The field name to evaluate.",
#         examples=["SPX Index", "trade_date", "price", "volume"],
#     )
#     field_type: FieldType | None = Field(
#         default=None,
#         description="The field type to be evaluated.",
#         examples=[
#             "trade_data",
#             "market_data",  # if market data should specify asset_class
#             "signal_data",
#         ],
#     )
#     unit: str | None = Field(
#         default=None, description="Unit for value.", examples=["day", "month", "year"]
#     )
#     value: int | float | date | str | None = Field(
#         default=None,
#         description="The value to compare against.",
#         examples=[100, 0.9, date(2024, 2, 4), "current_date"],
#     )
#     # do we need a value type or units? e.g. number of months/days

#     @model_validator(mode="after")
#     def post_validate_model(self):
#         """Post validate model."""
#         # assert self.value or (self.field and self.field_type)

#         # if units, can validate based on value/field
#         return self


# class DateConditionType(str, Enum):
#     """Date Condition Type Enum."""

#     DAYS_BEFORE_EXPIRY = "days_before_expiry"
#     DAYS_AFTER_OPEN = "days_after_open"
