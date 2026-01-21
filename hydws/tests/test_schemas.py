from datetime import datetime

from hydws.schemas import BoreholeSectionSchema, HydraulicSampleSchema


class TestSchemas:
    """Test bidirectional transformation: nested API <-> flat DB."""

    def test_nested_input_flattens(self):
        """Nested JSON input populates flat fields."""
        data = {"datetime": {"value": "2021-01-01T00:00:00"},
                "toppressure": {"value": 1.0, "uncertainty": 0.1}}
        schema = HydraulicSampleSchema.model_validate(data)
        assert schema.toppressure_value == 1.0
        assert schema.toppressure_uncertainty == 0.1

    def test_flat_input_works(self):
        """Already-flat input (simulating ORM) still works."""
        data = {"datetime_value": datetime(2021, 1, 1),
                "toppressure_value": 1.0}
        schema = HydraulicSampleSchema.model_validate(data)
        assert schema.toppressure_value == 1.0

    def test_flat_dict_returns_flat(self):
        """flat_dict() returns flat field names for DB insertion."""
        data = {"datetime": {"value": "2021-01-01T00:00:00"},
                "toppressure": {"value": 1.0}}
        schema = HydraulicSampleSchema.model_validate(data)
        flat = schema.flat_dict()
        assert "toppressure_value" in flat
        assert "toppressure" not in flat

    def test_flat_dict_exclude_unset(self):
        """exclude_unset=True only includes explicitly set fields."""
        data = {"datetime": {"value": "2021-01-01T00:00:00"},
                "toppressure": {"value": 1.0}}
        schema = HydraulicSampleSchema.model_validate(data)
        flat = schema.flat_dict(exclude_unset=True)
        assert "toppressure_value" in flat
        assert "bottomtemperature_value" not in flat

    def test_model_dump_nested_output(self):
        """model_dump() returns nested structure via computed_field."""
        data = {"datetime": {"value": "2021-01-01T00:00:00"},
                "toppressure": {"value": 1.0}}
        schema = HydraulicSampleSchema.model_validate(data)
        dumped = schema.model_dump(exclude_none=True)
        assert "toppressure" in dumped
        assert dumped["toppressure"]["value"] == 1.0

    def test_section_with_hydraulics(self):
        """Nested sections flatten recursively."""
        data = {
            "publicid": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Section 1",
            "starttime": "2021-01-01T00:00:00",
            "endtime": "2021-12-31T00:00:00",
            "hydraulics": [
                {"datetime": {"value": "2021-01-01T00:00:00"},
                 "toppressure": {"value": 1.0}}
            ]
        }
        schema = BoreholeSectionSchema.model_validate(data)
        flat = schema.flat_dict()
        assert flat["hydraulics"][0]["toppressure_value"] == 1.0
