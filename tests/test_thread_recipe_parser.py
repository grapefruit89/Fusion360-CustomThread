"""
Unit tests for Thread Recipe Parser module (src/thread_recipe_parser.py).
"""

import json
import pytest
from pathlib import Path

from src.thread_recipe_parser import (
    ThreadRecipe,
    ThreadRecipeSize,
    ThreadRecipeError,
    ThreadRecipeSyntaxError,
    ThreadRecipeValidationError,
    parse_thread_recipe,
    parse_thread_recipe_file,
)


@pytest.fixture
def valid_recipe_dict():
    return {
        "schema": "thread-recipe/1",
        "name": "PCO1881_PET_Deckel_3DPrint",
        "customName": "[3D-Print] PCO1881 - PET Flasche (Deckel)",
        "filename": "PCO1881_PET_Deckel.xml",
        "unit": "mm",
        "angle": 60,
        "sortOrder": 250,
        "profile": "iso-metric",
        "clearances": [0.10, 0.15, 0.20],
        "cases": ["real"],
        "sizes": [
            {
                "designation": "PCO 1881",
                "ctd": "PCO1881",
                "nominal": 28.0,
                "pitch": 2.7,
                "minor": None,
                "pitchDia": None,
                "crestFlat": None,
                "rootFlat": None,
            }
        ],
        "meta": {
            "purpose": "Deckel für PET-Getränkeflasche",
            "confidence": "high",
        },
    }


def test_valid_recipe_parsing(valid_recipe_dict, tmp_path):
    """Test 1: Valid recipe parsing from string and file."""
    json_str = json.dumps(valid_recipe_dict)
    recipe = parse_thread_recipe(json_str)

    assert isinstance(recipe, ThreadRecipe)
    assert recipe.schema == "thread-recipe/1"
    assert recipe.name == "PCO1881_PET_Deckel_3DPrint"
    assert recipe.custom_name == "[3D-Print] PCO1881 - PET Flasche (Deckel)"
    assert recipe.customName == recipe.custom_name
    assert recipe.angle == 60.0
    assert recipe.sort_order == 250
    assert recipe.sortOrder == 250
    assert len(recipe.sizes) == 1

    size = recipe.sizes[0]
    assert isinstance(size, ThreadRecipeSize)
    assert size.designation == "PCO 1881"
    assert size.nominal == 28.0
    assert size.pitch == 2.7
    assert size.tpi is None

    # Test parse_thread_recipe_file
    file_path = tmp_path / "valid_recipe.json"
    file_path.write_text(json_str, encoding="utf-8")
    recipe_from_file = parse_thread_recipe_file(file_path)
    assert recipe_from_file.name == recipe.name


def test_missing_nominal_field(valid_recipe_dict):
    """Test 2: Size entry missing required nominal field."""
    del valid_recipe_dict["sizes"][0]["nominal"]
    json_str = json.dumps(valid_recipe_dict)

    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json_str)
    assert "missing required field 'nominal'" in str(exc_info.value)


def test_missing_pitch_field(valid_recipe_dict):
    """Test 3: Missing both pitch and tpi fields."""
    del valid_recipe_dict["sizes"][0]["pitch"]
    json_str = json.dumps(valid_recipe_dict)

    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json_str)
    assert "missing required field 'pitch' or 'tpi'" in str(exc_info.value)


def test_both_pitch_and_tpi_specified(valid_recipe_dict):
    """Test specifying both pitch and tpi fields."""
    valid_recipe_dict["sizes"][0]["tpi"] = 10.0
    json_str = json.dumps(valid_recipe_dict)

    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json_str)
    assert "specifies both 'pitch' and 'tpi'" in str(exc_info.value)


def test_malformed_json_syntax_error():
    """Test 4: Malformed JSON syntax error."""
    malformed_json = '{"schema": "thread-recipe/1", "name": "Test", '

    with pytest.raises(ThreadRecipeSyntaxError) as exc_info:
        parse_thread_recipe(malformed_json)
    assert "JSON syntax error" in str(exc_info.value)


def test_invalid_field_data_types(valid_recipe_dict):
    """Test 5: Invalid field data types (e.g. nominal as string, angle as string)."""
    # 5a. nominal as string
    recipe_str_nominal = json.loads(json.dumps(valid_recipe_dict))
    recipe_str_nominal["sizes"][0]["nominal"] = "28.0"
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_str_nominal))
    assert "must be numeric" in str(exc_info.value)

    # 5b. angle as string
    recipe_str_angle = json.loads(json.dumps(valid_recipe_dict))
    recipe_str_angle["angle"] = "60"
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_str_angle))
    assert "must be numeric" in str(exc_info.value)

    # 5c. sortOrder as bool
    recipe_bool_sort = json.loads(json.dumps(valid_recipe_dict))
    recipe_bool_sort["sortOrder"] = True
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_bool_sort))
    assert "must be a valid integer" in str(exc_info.value)


def test_out_of_bounds_domain_errors(valid_recipe_dict):
    """Test 6: Out of bounds / domain range / geometric errors."""
    # 6a. sortOrder < 200
    recipe_low_sort = json.loads(json.dumps(valid_recipe_dict))
    recipe_low_sort["sortOrder"] = 150
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_low_sort))
    assert "must be >= 200" in str(exc_info.value)

    # 6b. nominal <= 0
    recipe_neg_nominal = json.loads(json.dumps(valid_recipe_dict))
    recipe_neg_nominal["sizes"][0]["nominal"] = -5.0
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_neg_nominal))
    assert "must be positive" in str(exc_info.value)

    # 6c. pitch >= nominal
    recipe_large_pitch = json.loads(json.dumps(valid_recipe_dict))
    recipe_large_pitch["sizes"][0]["pitch"] = 30.0
    recipe_large_pitch["sizes"][0]["nominal"] = 28.0
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_large_pitch))
    assert "must be strictly less than nominal diameter" in str(exc_info.value)

    # 6d. nominal > pitchDia > minor geometric constraint violation
    recipe_geom_violation = json.loads(json.dumps(valid_recipe_dict))
    recipe_geom_violation["sizes"][0]["nominal"] = 28.0
    recipe_geom_violation["sizes"][0]["pitchDia"] = 25.0
    recipe_geom_violation["sizes"][0]["minor"] = 26.0  # minor > pitchDia!
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_geom_violation))
    assert "geometric constraint violated" in str(exc_info.value)


def test_invalid_schema_header(valid_recipe_dict):
    """Test schema header validation."""
    valid_recipe_dict["schema"] = "invalid-schema/2"
    json_str = json.dumps(valid_recipe_dict)

    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json_str)
    assert "must be 'thread-recipe/1'" in str(exc_info.value)


def test_invalid_custom_name_prefix(valid_recipe_dict):
    """Test customName prefix validation."""
    valid_recipe_dict["customName"] = "Standard Thread PCO1881"
    json_str = json.dumps(valid_recipe_dict)

    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json_str)
    assert "must start with '[3D-Print]'" in str(exc_info.value)


def test_valid_tpi_recipe(valid_recipe_dict):
    """Test valid recipe using TPI instead of pitch."""
    del valid_recipe_dict["sizes"][0]["pitch"]
    valid_recipe_dict["sizes"][0]["tpi"] = 10.0
    json_str = json.dumps(valid_recipe_dict)

    recipe = parse_thread_recipe(json_str)
    assert recipe.sizes[0].tpi == 10.0
    assert recipe.sizes[0].pitch is None


def test_nan_inf_number_validation(valid_recipe_dict):
    """Test that NaN and Inf values raise ThreadRecipeValidationError."""
    # 1. NaN in numeric field angle
    recipe_nan_angle = json.loads(json.dumps(valid_recipe_dict))
    recipe_nan_angle["angle"] = float("nan")
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_nan_angle))
    assert "must be numeric" in str(exc_info.value)

    # 2. Inf in numeric field nominal
    recipe_inf_nominal = json.loads(json.dumps(valid_recipe_dict))
    recipe_inf_nominal["sizes"][0]["nominal"] = float("inf")
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_inf_nominal))
    assert "must be numeric" in str(exc_info.value)

    # 3. -Inf in numeric field pitch
    recipe_neginf_pitch = json.loads(json.dumps(valid_recipe_dict))
    recipe_neginf_pitch["sizes"][0]["pitch"] = float("-inf")
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_neginf_pitch))
    assert "must be numeric" in str(exc_info.value)


def test_sort_order_nan_inf(valid_recipe_dict):
    """Test sortOrder handling for NaN, Inf, and non-integer values."""
    # 1. NaN in sortOrder
    recipe_nan_sort = json.loads(json.dumps(valid_recipe_dict))
    recipe_nan_sort["sortOrder"] = float("nan")
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_nan_sort))
    assert "Field 'sortOrder' must be a valid integer" in str(exc_info.value)

    # 2. Inf in sortOrder
    recipe_inf_sort = json.loads(json.dumps(valid_recipe_dict))
    recipe_inf_sort["sortOrder"] = float("inf")
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_inf_sort))
    assert "Field 'sortOrder' must be a valid integer" in str(exc_info.value)

    # 3. Overflow float in sortOrder
    recipe_overflow_sort = json.loads(json.dumps(valid_recipe_dict))
    recipe_overflow_sort["sortOrder"] = 1e308
    with pytest.raises(ThreadRecipeValidationError) as exc_info:
        parse_thread_recipe(json.dumps(recipe_overflow_sort))
    assert "Field 'sortOrder' must be a valid integer" in str(exc_info.value)


def test_crest_flat_snake_case_fallback(valid_recipe_dict):
    """Test retrieving crest_flat when specified in snake_case."""
    recipe_dict = json.loads(json.dumps(valid_recipe_dict))
    # Replace crestFlat key with crest_flat key
    del recipe_dict["sizes"][0]["crestFlat"]
    recipe_dict["sizes"][0]["crest_flat"] = 0.35
    recipe_dict["sizes"][0]["root_flat"] = 0.15

    json_str = json.dumps(recipe_dict)
    recipe = parse_thread_recipe(json_str)

    assert recipe.sizes[0].crest_flat == 0.35
    assert recipe.sizes[0].crestFlat == 0.35
    assert recipe.sizes[0].root_flat == 0.15
    assert recipe.sizes[0].rootFlat == 0.15


def test_parse_file_invalid_path_type():
    """Test parse_thread_recipe_file with non-string, non-Path arguments."""
    invalid_paths = [123, [1, 2], None, {"path": "recipe.json"}, 3.14]
    for invalid_path in invalid_paths:
        with pytest.raises(ThreadRecipeValidationError) as exc_info:
            parse_thread_recipe_file(invalid_path)
        assert "File path must be a string or Path object, got" in str(exc_info.value)

