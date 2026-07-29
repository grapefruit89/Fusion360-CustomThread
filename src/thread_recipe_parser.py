"""
Thread Recipe Parser module.
Parses and validates JSON thread recipes according to schema thread-recipe/1.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ThreadRecipeError(Exception):
    """Base exception for thread recipe parsing and validation errors."""
    pass


class ThreadRecipeSyntaxError(ThreadRecipeError):
    """Raised when JSON parsing fails due to syntax errors."""
    pass


class ThreadRecipeValidationError(ThreadRecipeError):
    """Raised when recipe schema, data type, domain range, or geometric validation fails."""
    pass


@dataclass
class ThreadRecipeSize:
    designation: str
    nominal: float
    pitch: Optional[float] = None
    tpi: Optional[float] = None
    ctd: Optional[str] = None
    minor: Optional[float] = None
    pitch_dia: Optional[float] = None
    crest_flat: Optional[float] = None
    root_flat: Optional[float] = None
    profile: Optional[str] = None

    @property
    def pitchDia(self) -> Optional[float]:
        return self.pitch_dia

    @property
    def crestFlat(self) -> Optional[float]:
        return self.crest_flat

    @property
    def rootFlat(self) -> Optional[float]:
        return self.root_flat


@dataclass
class ThreadRecipe:
    schema: str
    name: str
    custom_name: str
    angle: float
    sort_order: int
    sizes: List[ThreadRecipeSize]
    filename: Optional[str] = None
    unit: str = "mm"
    profile: Optional[str] = None
    clearances: Optional[List[float]] = None
    cases: Optional[List[str]] = None
    external_only: bool = False
    meta: Optional[Dict[str, Any]] = None

    @property
    def customName(self) -> str:
        return self.custom_name

    @property
    def sortOrder(self) -> int:
        return self.sort_order

    @property
    def externalOnly(self) -> bool:
        return self.external_only


def _is_number(val: Any) -> bool:
    """Returns True if val is int or float and not bool, and not NaN or Inf."""
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        return False
    try:
        if math.isnan(val) or math.isinf(val):
            return False
    except (TypeError, ValueError, OverflowError):
        return False
    return True


def _check_string(val: Any, field_name: str) -> str:
    if not isinstance(val, str):
        raise ThreadRecipeValidationError(
            f"Field '{field_name}' must be a string, got {type(val).__name__} ({val!r})."
        )
    return val


def _check_number(val: Any, field_name: str) -> float:
    if not _is_number(val):
        raise ThreadRecipeValidationError(
            f"Field '{field_name}' must be numeric (int/float), got {type(val).__name__} ({val!r})."
        )
    return float(val)


def _check_bool(val: Any, field_name: str) -> bool:
    if not isinstance(val, bool):
        raise ThreadRecipeValidationError(
            f"Field '{field_name}' must be a boolean, got {type(val).__name__} ({val!r})."
        )
    return val


def parse_thread_recipe(json_str: str) -> ThreadRecipe:
    """Parse JSON string and validate against thread-recipe/1 schema."""
    if not isinstance(json_str, str):
        raise ThreadRecipeSyntaxError(
            f"Expected JSON string input, got {type(json_str).__name__}."
        )

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ThreadRecipeSyntaxError(
            f"JSON syntax error at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ThreadRecipeValidationError("JSON root must be an object dictionary.")

    # 1. Mandatory 'schema'
    if "schema" not in data:
        raise ThreadRecipeValidationError("Missing mandatory root field 'schema'.")
    schema = _check_string(data["schema"], "schema")
    if schema != "thread-recipe/1":
        raise ThreadRecipeValidationError(
            f"Field 'schema' must be 'thread-recipe/1', got {schema!r}."
        )

    # 2. Mandatory 'name'
    if "name" not in data:
        raise ThreadRecipeValidationError("Missing mandatory root field 'name'.")
    name = _check_string(data["name"], "name")
    if not name.strip():
        raise ThreadRecipeValidationError("Field 'name' cannot be empty.")

    # 3. Mandatory 'customName' / 'custom_name'
    c_name_val = data.get("customName") if data.get("customName") is not None else data.get("custom_name")
    if c_name_val is None:
        raise ThreadRecipeValidationError("Missing mandatory root field 'customName' or 'custom_name'.")
    custom_name = _check_string(c_name_val, "customName/custom_name")
    if not custom_name.startswith("[3D-Print]"):
        raise ThreadRecipeValidationError(
            f"Field 'customName' must start with '[3D-Print]', got {custom_name!r}."
        )

    # 4. Mandatory 'angle'
    if "angle" not in data:
        raise ThreadRecipeValidationError("Missing mandatory root field 'angle'.")
    angle = _check_number(data["angle"], "angle")
    if not (10 <= angle <= 120):
        raise ThreadRecipeValidationError(
            f"Field 'angle' must be between 10 and 120, got {angle}."
        )

    # 5. Mandatory 'sortOrder' / 'sort_order'
    so_val = data.get("sortOrder") if data.get("sortOrder") is not None else data.get("sort_order")
    if so_val is None:
        raise ThreadRecipeValidationError("Missing mandatory root field 'sortOrder' or 'sort_order'.")
    if isinstance(so_val, bool) or not isinstance(so_val, (int, float)):
        raise ThreadRecipeValidationError(
            f"Field 'sortOrder' must be a valid integer, got {type(so_val).__name__} ({so_val!r})."
        )
    if isinstance(so_val, float):
        if math.isnan(so_val) or math.isinf(so_val) or not so_val.is_integer() or abs(so_val) > 1e15:
            raise ThreadRecipeValidationError(
                f"Field 'sortOrder' must be a valid integer, got {so_val!r}."
            )
    if isinstance(so_val, (int, float)) and abs(so_val) > 1e15:
        raise ThreadRecipeValidationError(
            f"Field 'sortOrder' must be a valid integer, got {so_val!r}."
        )
    sort_order = int(so_val)
    if sort_order < 200:
        raise ThreadRecipeValidationError(
            f"Field 'sortOrder' must be >= 200 (Autodesk reserves 1-63), got {sort_order}."
        )

    # 6. Mandatory 'sizes'
    if "sizes" not in data:
        raise ThreadRecipeValidationError("Missing mandatory root field 'sizes'.")
    sizes_raw = data["sizes"]
    if not isinstance(sizes_raw, list):
        raise ThreadRecipeValidationError(
            f"Field 'sizes' must be a list, got {type(sizes_raw).__name__}."
        )
    if len(sizes_raw) == 0:
        raise ThreadRecipeValidationError("Field 'sizes' list cannot be empty.")

    # Validate each size entry
    sizes: List[ThreadRecipeSize] = []
    for idx, sz in enumerate(sizes_raw):
        if not isinstance(sz, dict):
            raise ThreadRecipeValidationError(
                f"Element at sizes[{idx}] must be an object dictionary."
            )

        # designation
        if "designation" not in sz:
            raise ThreadRecipeValidationError(
                f"Size at index {idx} missing required field 'designation'."
            )
        designation = _check_string(sz["designation"], f"sizes[{idx}].designation")

        # nominal
        if "nominal" not in sz:
            raise ThreadRecipeValidationError(
                f"Size '{designation}' missing required field 'nominal'."
            )
        nominal = _check_number(sz["nominal"], f"Size '{designation}'.nominal")
        if nominal <= 0:
            raise ThreadRecipeValidationError(
                f"Size '{designation}' field 'nominal' must be positive (> 0), got {nominal}."
            )

        # pitch and tpi
        has_pitch = "pitch" in sz and sz["pitch"] is not None
        has_tpi = "tpi" in sz and sz["tpi"] is not None

        if has_pitch and has_tpi:
            raise ThreadRecipeValidationError(
                f"Size '{designation}' specifies both 'pitch' and 'tpi'; exactly one must be specified."
            )
        if not has_pitch and not has_tpi:
            raise ThreadRecipeValidationError(
                f"Size '{designation}' missing required field 'pitch' or 'tpi'."
            )

        pitch_val: Optional[float] = None
        tpi_val: Optional[float] = None
        effective_pitch: float

        if has_pitch:
            pitch_val = _check_number(sz["pitch"], f"Size '{designation}'.pitch")
            if pitch_val <= 0:
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' field 'pitch' must be positive (> 0), got {pitch_val}."
                )
            effective_pitch = pitch_val
        else:
            tpi_val = _check_number(sz["tpi"], f"Size '{designation}'.tpi")
            if tpi_val <= 0:
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' field 'tpi' must be positive (> 0), got {tpi_val}."
                )
            effective_pitch = 25.4 / tpi_val

        # Domain range check: pitch < nominal
        if effective_pitch >= nominal:
            raise ThreadRecipeValidationError(
                f"Size '{designation}' geometric error: pitch ({effective_pitch}) must be strictly less than nominal diameter ({nominal})."
            )

        # Optional fields validation
        ctd = _check_string(sz["ctd"], f"Size '{designation}'.ctd") if "ctd" in sz and sz["ctd"] is not None else None

        minor_val: Optional[float] = None
        if "minor" in sz and sz["minor"] is not None:
            minor_val = _check_number(sz["minor"], f"Size '{designation}'.minor")
            if minor_val <= 0:
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' field 'minor' must be positive (> 0), got {minor_val}."
                )

        pitch_dia_val: Optional[float] = None
        pd_raw = sz.get("pitchDia") if sz.get("pitchDia") is not None else sz.get("pitch_dia")
        if pd_raw is not None:
            pitch_dia_val = _check_number(pd_raw, f"Size '{designation}'.pitchDia")
            if pitch_dia_val <= 0:
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' field 'pitchDia' must be positive (> 0), got {pitch_dia_val}."
                )

        # Geometric constraint check: nominal > pitchDia > minor
        if pitch_dia_val is not None and minor_val is not None:
            if not (nominal > pitch_dia_val > minor_val):
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' geometric constraint violated: nominal ({nominal}) > pitchDia ({pitch_dia_val}) > minor ({minor_val})."
                )
        elif pitch_dia_val is not None:
            if not (nominal > pitch_dia_val):
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' geometric constraint violated: nominal ({nominal}) > pitchDia ({pitch_dia_val})."
                )
        elif minor_val is not None:
            if not (nominal > minor_val):
                raise ThreadRecipeValidationError(
                    f"Size '{designation}' geometric constraint violated: nominal ({nominal}) > minor ({minor_val})."
                )

        crest_flat_val: Optional[float] = None
        cf_raw = sz.get("crestFlat") if sz.get("crestFlat") is not None else sz.get("crest_flat")
        if cf_raw is not None:
            crest_flat_val = _check_number(cf_raw, f"Size '{designation}'.crestFlat")

        root_flat_val: Optional[float] = None
        rf_raw = sz.get("rootFlat") if sz.get("rootFlat") is not None else sz.get("root_flat")
        if rf_raw is not None:
            root_flat_val = _check_number(rf_raw, f"Size '{designation}'.rootFlat")

        profile_val: Optional[str] = None
        if "profile" in sz and sz["profile"] is not None:
            profile_val = _check_string(sz["profile"], f"Size '{designation}'.profile")

        sizes.append(
            ThreadRecipeSize(
                designation=designation,
                nominal=nominal,
                pitch=pitch_val,
                tpi=tpi_val,
                ctd=ctd,
                minor=minor_val,
                pitch_dia=pitch_dia_val,
                crest_flat=crest_flat_val,
                root_flat=root_flat_val,
                profile=profile_val,
            )
        )

    # Optional root fields
    filename = _check_string(data["filename"], "filename") if "filename" in data and data["filename"] is not None else None
    unit = _check_string(data["unit"], "unit") if "unit" in data and data["unit"] is not None else "mm"
    root_profile = _check_string(data["profile"], "profile") if "profile" in data and data["profile"] is not None else None

    clearances: Optional[List[float]] = None
    if "clearances" in data and data["clearances"] is not None:
        cl_raw = data["clearances"]
        if not isinstance(cl_raw, list):
            raise ThreadRecipeValidationError("Field 'clearances' must be a list of numbers.")
        clearances = [_check_number(c, f"clearances[{i}]") for i, c in enumerate(cl_raw)]

    cases: Optional[List[str]] = None
    if "cases" in data and data["cases"] is not None:
        cs_raw = data["cases"]
        if not isinstance(cs_raw, list):
            raise ThreadRecipeValidationError("Field 'cases' must be a list of strings.")
        cases = [_check_string(c, f"cases[{i}]") for i, c in enumerate(cs_raw)]

    ext_only_raw = data.get("externalOnly") if data.get("externalOnly") is not None else data.get("external_only")
    external_only = _check_bool(ext_only_raw, "externalOnly") if ext_only_raw is not None else False

    meta = data.get("meta")
    if meta is not None and not isinstance(meta, dict):
        raise ThreadRecipeValidationError("Field 'meta' must be a dictionary.")

    return ThreadRecipe(
        schema=schema,
        name=name,
        custom_name=custom_name,
        angle=angle,
        sort_order=sort_order,
        sizes=sizes,
        filename=filename,
        unit=unit,
        profile=root_profile,
        clearances=clearances,
        cases=cases,
        external_only=external_only,
        meta=meta,
    )


def parse_thread_recipe_file(filepath: Union[str, Path]) -> ThreadRecipe:
    """Read a JSON thread recipe file and parse its contents."""
    if not (isinstance(filepath, (str, Path)) or hasattr(filepath, "__fspath__")):
        raise ThreadRecipeValidationError(
            f"File path must be a string or Path object, got {type(filepath).__name__} ({filepath!r})."
        )
    path = Path(filepath)
    if not path.is_file():
        raise ThreadRecipeError(f"File not found: {path}")

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        raise ThreadRecipeError(f"Error reading file {path}: {exc}") from exc

    return parse_thread_recipe(content)
