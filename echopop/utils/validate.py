"""
Validation functions.
"""

# TODO: Compile all package validators here since they may not belong elsewhere
import re
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, get_args

import numpy as np
import pandas as pd

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from pandera import DataFrameModel, Field, check
from pandera.typing import Series
from pandera.errors import SchemaError, SchemaErrors

# CLASS-SPECIFIC CORE API
class posint(int):
    """Positive-only integer (includes 0)"""

    __failstate__ = "must be a non-negative integer"

    def __new__(cls, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Value must be a non-negative integer.")
        return super().__new__(cls, value)


class posfloat(float):
    """Positive-only float (includes 0.0)"""

    __failstate__ = "must be a non-negative float"

    def __new__(cls, value):
        if not isinstance(value, (float, int)) or value < 0:
            raise ValueError("Value must be a non-negative float.")
        return super().__new__(cls, value)


class realposfloat(posfloat):
    """Real number positive-only float (includes 0.0)"""

    __failstate__ = "must be a non-negative real number"

    def __new__(cls, value):
        if not isinstance(value, (float, int)) or np.isinf(value):  # Check if value is infinity
            raise ValueError(f"Value {cls.__failstate__}.")
        return super().__new__(cls, value)


class realcircle(realposfloat):
    """Real number in a unit circle"""

    __failstate__ = "must be a non-negative real angle (as a 'float') between 0.0 and 360.0 degrees"

    def __new__(cls, value):
        if not isinstance(value, (float, int)) or (value < 0.0 or value > 360.0):
            raise ValueError(f"Value {cls.__failstate__}.")
        return super().__new__(cls, value)


class FileSettings(BaseModel):
    """
    Parameter file settings
    """

    directory: str
    sheetname: str


class StratifiedSurveyMeanParameters(BaseModel, arbitrary_types_allowed=True):
    """
    Stratified sampling parameters
    """

    strata_transect_proportion: posfloat
    num_replicates: posint
    mesh_transects_per_latitude: posint

    @field_validator("num_replicates", "mesh_transects_per_latitude", mode="before")
    def validate_posint(cls, v):
        return posint(v)

    @field_validator("strata_transect_proportion", mode="before")
    def validate_posfloat(cls, v):
        return posfloat(v)


class KrigingParameters(BaseModel, arbitrary_types_allowed=True):
    """
    Kriging model parameters
    """

    A0: posfloat
    longitude_reference: float
    longitude_offset: float
    latitude_offset: float

    @field_validator("A0", mode="before")
    def validate_posfloat(cls, v):
        return posfloat(v)


class HaulTransectMap(BaseModel, arbitrary_types_allowed=True):
    """
    Haul-to-transect key mapping generation parameters
    """

    save_file_template: str
    country_code: List[str]
    file_settings: Dict[str, FileSettings]

    @model_validator(mode="before")
    def validate_country_files(cls, values):
        # ---- Get the country code list
        country_codes = values.get("country_code", [])
        # ---- Get file settings keys
        file_settings_keys = list(values.get("file_settings", {}).keys())
        # ---- Keys within `file_settings` must match those defined in `country_code`
        if not set(file_settings_keys) == set(country_codes):
            # ---- Raise error
            raise ValueError(
                f"File settings keys {file_settings_keys} must match those defined in "
                f"'country_code' ({country_codes})."
            )
        # ---- Return values
        return values

    @field_validator("save_file_template", mode="after")
    def validate_save_file_template(cls, v):
        # ---- Find all strings contained within curly braces
        template_ids = re.findall(r"{(.*?)}", v)
        # ---- Evaluate valid id's
        if not set(template_ids).issubset(set(["YEAR", "COUNTRY"])):
            # ---- Get the unknown IDs
            unknown_ids = set(template_ids) - set(["YEAR", "COUNTRY"])
            # ---- Raise Error
            raise ValueError(
                f"Haul-to-transect mapping save file template ({v}) contains invalid identifiers "
                f"({list(unknown_ids)}). Valid identifiers within the filename template (bounded "
                f"by curly braces) include: ['YEAR', 'COUNTRY']."
            )
        # ---- Return values
        return v


class PatternParts(BaseModel):
    """
    String pattern parts
    """

    pattern: str
    label: str


class TransectRegionMap(BaseModel, arbitrary_types_allowed=True):
    """
    Transect-to-region mapping parameters
    """

    save_file_template: str
    save_file_directory: str
    save_file_sheetname: str
    pattern: str
    parts: Dict[str, List[PatternParts]]

    @model_validator(mode="before")
    def validate_pattern_parts(cls, values):
        # ---- Get the country code list
        pattern_codes = values.get("pattern", "")
        # ---- Extract the codes
        codes = re.findall(r"{(.*?)}", pattern_codes)
        # ---- Get file settings keys
        parts_keys = list(values.get("parts", {}).keys())
        # ---- Keys within `file_settings` must match those defined in `country_code`
        if not set(parts_keys) == set(codes):
            # ---- Raise error
            raise ValueError(
                f"Defined pattern dictionary keys {parts_keys} must match those defined in "
                f"'pattern' ({codes})."
            )
        # ---- Return values
        return values

    @field_validator("save_file_template", mode="after")
    def validate_save_file_template(cls, v):
        # ---- Find all strings contained within curly braces
        template_ids = re.findall(r"{(.*?)}", v)
        # ---- Evaluate valid id's
        if not set(template_ids).issubset(set(["YEAR", "COUNTRY", "GROUP"])):
            # ---- Get the unknown IDs
            unknown_ids = set(template_ids) - set(["YEAR", "COUNTRY", "GROUP"])
            # ---- Raise Error
            raise ValueError(
                f"Transect-to-region mapping save file template ({v}) contains invalid identifiers "
                f"({list(unknown_ids)}). Valid identifiers within the filename template (bounded "
                f"by curly braces) include: ['YEAR', 'COUNTRY', 'GROUP']."
            )
        # ---- Return value
        return v

    @field_validator("pattern", mode="after")
    def validate_pattern(cls, v):
        # ---- Find all strings contained within curly braces
        template_ids = re.findall(r"{(.*?)}", v)
        # ---- Evaluate valid id's
        if not set(template_ids).issubset(set(["REGION_CLASS", "HAUL_NUM", "COUNTRY"])):
            # ---- Get the unknown IDs
            unknown_ids = set(template_ids) - set(["REGION_CLASS", "HAUL_NUM", "COUNTRY"])
            # ---- Raise Error
            raise ValueError(
                f"Transect-to-region mapping save file template ({v}) contains invalid identifiers "
                f"({list(unknown_ids)}). Valid identifiers within the filename template (bounded "
                f"by curly braces) include: ['REGION_CLASS', 'HAUL_NUM', 'COUNTRY']."
            )
            # ---- Return value
        return v


class TSLRegressionParameters(BaseModel):
    """
    Target strength - length regression parameters
    """

    number_code: int
    TS_L_slope: float = Field(allow_inf_nan=False)
    TS_L_intercept: float = Field(allow_inf_nan=False)
    length_units: str


class Geospatial(BaseModel):
    """
    Geospatial parameters
    """

    init: str

    @field_validator("init", mode="before")
    def validate_init(cls, v):
        # ---- Convert to a string if read in as an integer
        if isinstance(v, (int, float)):
            v = str(v)
        # ---- Convert to lowercase
        v = v.lower()
        # ---- Mold the entry into the expected format that includes a preceding 'epsg:'
        if not v.startswith("epsg"):
            v = "epsg:" + v
        # ---- Ensure that the colon is present
        if ":" not in v:
            v = "epsg:" + v.split("epsg")[1]
        # ---- Evaluate whether the pre-validator succeeded in finding an acceptable format
        if not re.match(r"^epsg:\d+$", v):
            raise ValueError(
                f"Echopop cannot parse the defined EPSG code ('{v}'). EPSG codes most be formatted "
                f"with strings beginning with 'epsg:' followed by the integer number code (e.g. "
                f"'epsg:4326')."
            )
        # ---- Return the pre-validated entry
        return v


class NASCExports(BaseModel, arbitrary_types_allowed=True):
    """
    NASC export processing parameters
    """

    export_file_directory: str
    nasc_export_directory: str
    save_file_template: str
    save_file_sheetname: str
    regions: Dict[str, List[str]]
    max_transect_spacing: realposfloat
    file_columns: List[str]

    @field_validator("max_transect_spacing", mode="before")
    def validate_realposfloat(cls, v):
        return realposfloat(v)

    @field_validator("save_file_template", mode="after")
    def validate_save_file_template(cls, v):
        # ---- Find all strings contained within curly braces
        template_ids = re.findall(r"{(.*?)}", v)
        # ---- Evaluate valid id's
        if not set(template_ids).issubset(set(["REGION", "YEAR", "GROUP"])):
            # ---- Get the unknown IDs
            unknown_ids = set(template_ids) - set(["REGION", "YEAR", "GROUP"])
            # ---- Raise Error
            raise ValueError(
                f"Haul-to-transect mapping save file template ({v}) contains invalid identifiers "
                f"({list(unknown_ids)}). Valid identifiers within the filename template (bounded "
                f"by curly braces) include: ['YEAR', 'REGION', 'GROUP']."
            )
        # ---- Return values
        return v


class CONFIG_INIT_MODEL(BaseModel, arbitrary_types_allowed=True):
    """
    Initialization parameter configuration YAML validator
    """

    stratified_survey_mean_parameters: StratifiedSurveyMeanParameters
    kriging_parameters: KrigingParameters
    bio_hake_age_bin: List[Union[posint, realposfloat]]
    bio_hake_len_bin: List[Union[posint, realposfloat]]
    TS_length_regression_parameters: Dict[str, TSLRegressionParameters]
    geospatial: Geospatial
    nasc_exports: Optional[NASCExports] = None
    haul_to_transect_mapping: Optional[HaulTransectMap] = None
    transect_region_mapping: Optional[TransectRegionMap] = None

    def __init__(self, filename, **kwargs):
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            # Customize error message
            new_message = str(e).replace(
                self.__class__.__name__, f"configuration parameters defined in {filename}"
            )
            raise ValueError(new_message) from e

    @field_validator("bio_hake_age_bin", "bio_hake_len_bin", mode="before")
    def validate_interval(cls, v):
        # ---- Check Union typing
        try:
            all(
                isinstance(value, (int, float))
                and (posint(value) if isinstance(value, int) else realposfloat(value))
                for value in v
            )
        except ValueError as e:
            raise ValueError(f"Invalid value detected within list. Every {str(e).lower()}")
        # ---- Check length
        if not len(v) == 3:
            raise ValueError(
                "Interval list must have a length of 3: "
                "['starting_value', 'ending_value', 'number']."
            )
        # ---- Check for any that may be 'realposfloat'
        any_posfloat = any(isinstance(value, (realposfloat, float)) for value in v)
        # ---- If true, then convert
        if any_posfloat:
            return [posint(value) if i == 2 else realposfloat(value) for i, value in enumerate(v)]
        else:
            return [posint(value) for value in v]


class XLSXFiles(BaseModel):
    """
    .xlsx file tree structure
    """

    filename: str
    sheetname: Union[str, List[str]]


class BiologicalFiles(BaseModel):
    """
    Biological data files
    """

    length: Union[Dict[str, XLSXFiles], XLSXFiles]
    specimen: Union[Dict[str, XLSXFiles], XLSXFiles]
    catch: Union[Dict[str, XLSXFiles], XLSXFiles]
    haul_to_transect: Union[Dict[str, XLSXFiles], XLSXFiles]


class KrigingFiles(BaseModel):
    """
    Kriging data files
    """

    vario_krig_para: XLSXFiles
    isobath_200m: XLSXFiles
    mesh: XLSXFiles


class StratificationFiles(BaseModel):
    """
    Stratification data files
    """

    strata: XLSXFiles
    geo_strata: XLSXFiles


class CONFIG_DATA_MODEL(BaseModel):
    """
    Data file configuration YAML validator
    """

    survey_year: int
    biological: BiologicalFiles
    stratification: StratificationFiles
    NASC: Dict[str, XLSXFiles]
    gear_data: Dict[str, XLSXFiles]
    kriging: KrigingFiles
    data_root_dir: Optional[str] = None
    CAN_haul_offset: Optional[int] = None
    ship_id: Optional[Union[int, str, float]] = None
    export_regions: Optional[Dict[str, XLSXFiles]] = None

    def __init__(self, filename, **kwargs):
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            # Customize error message
            new_message = str(e).replace(
                self.__class__.__name__, f"configured data files defined in {filename}"
            )
            raise ValueError(new_message) from e


# Validation functions
def describe_type(expected_type: Any) -> str:
    """
    Convert a type hint into a human-readable string.
    """

    if hasattr(expected_type, "__failstate__"):
        return expected_type.__failstate__

    if hasattr(expected_type, "__origin__"):
        origin = expected_type.__origin__

        if origin is Literal:
            return f"one of {expected_type.__args__}"

        if origin is Union:
            args = expected_type.__args__
            descriptions = [describe_type(arg) for arg in args if arg is not type(None)]
            if not descriptions:
                return "any value"
            return " or ".join(descriptions)

        if origin is np.ndarray:
            return "numpy.ndarray of floats"

        if origin is list:
            item_type = expected_type.__args__[0]
            return f"list of '{describe_type(item_type)}'"

    if isinstance(expected_type, type):
        return f"'{expected_type.__name__}'"

    # return str(expected_type)
    return f"'{expected_type}'"


def validate_type(value: Any, expected_type: Any) -> bool:
    """
    Validate if the value matches the expected type.
    """

    # Handle numpy.ndarray
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is np.ndarray:
        return (
            isinstance(value, np.ndarray)
            and np.issubdtype(value.dtype, np.number)
            # and value.dtype == np.float64
        )

    # Handle base `type` case
    if isinstance(expected_type, type):
        # ---- Handle `posint`
        if expected_type in [posint, posfloat, realposfloat, realcircle]:
            try:
                expected_type(value)
                return True
            except (TypeError, ValueError):
                return False
        else:
            return isinstance(value, expected_type)

    # Handle Union
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is Union:
        return any(validate_type(value, arg) for arg in expected_type.__args__)

    # Handle Literal
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is Literal:
        # ---- Get allowed values
        allowed_values = get_args(expected_type)
        if isinstance(value, np.ndarray):
            allowed_values_array = np.array(list(allowed_values), dtype=object)
            value_array = np.array(value, dtype=object)
            return np.array_equal(np.sort(value_array), np.sort(allowed_values_array))
        return value in allowed_values

    # Handle List
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is list:
        if not isinstance(value, list):
            return False
        item_type = expected_type.__args__[0]
        return all(validate_type(item, item_type) for item in value)

    # # Handle numpy.ndarray
    # if hasattr(expected_type, "__origin__") and expected_type.__origin__ is np.ndarray:
    #     return (
    #         isinstance(value, np.ndarray)
    #         and np.issubdtype(value.dtype, np.number)
    #         # and value.dtype == np.float64
    #     )

    return False


def validate_typed_dict(data: Dict[str, Any], expected_types: Dict[str, Any]) -> None:
    """
    Validate a dictionary against expected types.
    """
    for key, expected_type in expected_types.items():
        if key in data:
            if not validate_type(data[key], expected_type):
                expected_description = describe_type(expected_type)
                actual_description = type(data[key]).__name__
                if hasattr(expected_type, "__failstate__"):
                    raise TypeError(
                        f"Value for '{key}' ({data[key]}, type: '{actual_description}') "
                        f"{expected_description}."
                    )
                else:
                    raise TypeError(
                        f"Value for '{key}' ({data[key]}, type: '{actual_description}') does not "
                        f"match expected type {expected_description}."
                    )


# Validation classes
class VariogramBase(TypedDict, total=False):
    model: Union[str, List[str]]
    n_lags: posint
    lag_resolution: Optional[realposfloat]
    max_range: Optional[realposfloat]
    sill: Optional[realposfloat]
    nugget: Optional[realposfloat]
    hole_effect_range: Optional[realposfloat]
    correlation_range: Optional[realposfloat]
    enhance_semivariance: Optional[bool]
    decay_power: Optional[realposfloat]

    # Define default values
    DEFAULT_VALUES = {
        "model": ["bessel", "exponential"],
        "n_lags": 30,
        "lag_resolution": None,
        "max_range": None,
        "sill": None,
        "nugget": None,
        "hole_effect_range": None,
        "correlation_range": None,
        "enhance_semivariance": None,
        "decay_power": None,
    }

    # Root default values -- used for reinitialization
    _ROOT_DEFAULT = {
        "model": ["bessel", "exponential"],
        "n_lags": 30,
        "lag_resolution": None,
        "max_range": None,
        "sill": None,
        "nugget": None,
        "hole_effect_range": None,
        "correlation_range": None,
        "enhance_semivariance": None,
        "decay_power": None,
    }

    # Define the expected datatypes
    EXPECTED_DTYPES = {
        "model": Union[str, List[str]],
        "n_lags": posint,
        "lag_resolution": Optional[realposfloat],
        "max_range": Optional[realposfloat],
        "sill": Optional[realposfloat],
        "nugget": Optional[realposfloat],
        "hole_effect_range": Optional[realposfloat],
        "correlation_range": Optional[realposfloat],
        "enhance_semivariance": Optional[bool],
        "decay_power": Optional[realposfloat],
    }

    @classmethod
    def create(
        cls,
        model: Union[str, List[str]] = None,
        n_lags: posint = None,
        lag_resolution: Optional[realposfloat] = None,
        max_range: Optional[realposfloat] = None,
        sill: Optional[realposfloat] = None,
        nugget: Optional[realposfloat] = None,
        hole_effect_range: Optional[realposfloat] = None,
        correlation_range: Optional[realposfloat] = None,
        enhance_semivariance: Optional[posfloat] = None,
        decay_power: Optional[realposfloat] = None,
        **kwargs,
    ) -> "VariogramBase":
        """
        Base variogram model parameters

        Parameters
        ----------
        model: Union[str, List[str]]
            A string or list of model names. A single name represents a single family model. Two
            inputs represent the desired composite model (e.g. the composite J-Bessel and
            exponential model). Defaults to: ['bessel', 'exponential']. Available models and their
            required arguments can be reviewed in the :fun:`echopop.spatial.variogram.variogram`
            function.
        n_lags: posint
            See the `variogram_parameters` argument in
            :fun:`echopop.spatial.variogram.empirical_variogram` for more details on
            `n_lags`.
        sill: Optional[realposfloat]
            See the description of `sill` in
            :fun:`echopop.spatial.variogram.variogram`.
        nugget: Optional[realposfloat]
            See the description of `nugget` in
            :fun:`echopop.spatial.variogram.variogram`.
        correlation_range: Optional[realposfloat]
            See the description of `correlation_range` in
            :fun:`echopop.spatial.variogram.variogram`.
        hole_effect_range: Optional[realposfloat]
            See the description of `hole_effect_range` in
            :fun:`echopop.spatial.variogram.variogram`.
        decay_power: Optional[realposfloat]
            See the description of `decay_power` in
            :fun:`echopop.spatial.variogram.variogram`.
        enhanced_semivariance: Optional[bool]
            See the description of `enhanced_semivariance` in
            :fun:`echopop.spatial.variogram.variogram`.
        max_range: Optional[realposfloat]
            An optional input defining the maximum lag distance range that will be computed for
            fitting the theoretical variogram parameters.

        Returns
        ----------
        VariogramBase: A validated dictionary with the user-defined variogram parameter values and
        default values for any missing parameters/keys.
        """

        # User-defined parameters
        inputs = {
            "model": model,
            "n_lags": n_lags,
            "lag_resolution": lag_resolution,
            "max_range": max_range,
            "sill": sill,
            "nugget": nugget,
            "hole_effect_range": hole_effect_range,
            "correlation_range": correlation_range,
            "enhance_semivariance": enhance_semivariance,
            "decay_power": decay_power,
        }

        # Drop missing `inputs`
        input_filtered = {key: value for key, value in inputs.items() if value is not None}

        # Merge the default values with those provided by the user
        # ---- Copy defaults
        params = cls.DEFAULT_VALUES.copy()
        # ---- Update
        params.update(input_filtered)

        # Filter the parameter keys
        filtered_params = {key: params[key] for key in cls.EXPECTED_DTYPES if key in params}

        # Validate the parameter datatypes
        cls.validate(filtered_params)

        return filtered_params

    # Create updating method
    @classmethod
    def update_defaults(cls, new_defaults: Dict[str, Any]):
        """
        Update the DEFAULT_VALUES attribute with new default values.

        Parameters
        ----------
        new_defaults: Dict[str, Any]
            A dictionary containing the new default values.

        Raises
        ----------
        ValueError:
            If any new default value does not match the expected datatype.
        """

        # Filter the parameter keys
        filtered_new_defaults = {
            key: new_defaults[key] for key in cls.EXPECTED_DTYPES if key in new_defaults
        }

        # Validate the parameter datatypes
        cls.validate(filtered_new_defaults)

        # Update `DEFAULT_VALUES` attribute
        cls.DEFAULT_VALUES.update(filtered_new_defaults)

    # Create default value restoration method
    @classmethod
    def restore_defaults(cls):
        """
        Restore DEFAULT_VALUES attribute to original pre-updated state.
        """

        # Restore original state
        cls.DEFAULT_VALUES.update(cls._ROOT_DEFAULT)

    # Create validation method
    @staticmethod
    def validate(data: Dict[str, Any]):
        """
        Validate the input dictionary against the `VariogramBase` class definition/schema.

        Parameters
        ----------
        data: Dict[str, Any]
            A dictionary containing the parameters that will be validated.

        Raises
        ----------
        TypedError:
            If any value does not match the expected datatype.
        """

        # Define expected datatypes
        validate_typed_dict(data, VariogramBase.EXPECTED_DTYPES)
        # FOR DEBUGGING
        # --------
        # print("Validate passed.")
        # --------


class VariogramEmpirical(TypedDict, total=False):
    # Provide the type-hints
    azimuth_range: realcircle
    force_lag_zero: bool
    standardize_coordinates: bool

    # Define default values
    DEFAULT_VALUES = {
        "azimuth_range": 360.0,
        "force_lag_zero": True,
        "standardize_coordinates": True,
    }

    # Define the expected datatypes
    EXPECTED_DTYPES = {
        "azimuth_range": realcircle,
        "force_lag_zero": bool,
        "standardize_coordinates": bool,
    }

    @classmethod
    def create(
        cls,
        azimuth_range: realcircle = 360.0,
        force_lag_zero: bool = True,
        standardize_coordinates: bool = True,
        **kwargs,
    ) -> "VariogramEmpirical":
        """
        Empirical variogram parameters

        Parameters
        ----------
        azimuth_range: float
            The total azimuth angle range that is allowed for constraining
            the relative angles between spatial points, particularly for cases where a high degree
            of directionality is assumed.
        force_lag_zero: bool
            See the `variogram_parameters` argument in
            :fun:`echopop.spatial.variogram.empirical_variogram` for more details on
            `force_lag_zero`.
        standardize_coordinates: bool
            When set to `True`, transect coordinates are standardized using reference coordinates.

        Returns
        ----------
        VariogramEmpirical: A validated dictionary with the user-defined empirical variogram
        parameter values and default values for any missing parameters/keys.
        """

        # User-defined parameters
        inputs = {
            "azimuth_range": azimuth_range,
            "force_lag_zero": force_lag_zero,
            "standardize_coordinates": standardize_coordinates,
        }

        # Drop missing `inputs`
        input_filtered = {key: value for key, value in inputs.items() if value is not None}

        # Merge the default values with those provided by the user
        # ---- Copy defaults
        params = cls.DEFAULT_VALUES.copy()
        # ---- Update
        params.update(input_filtered)

        # Filter the parameter keys
        filtered_params = {key: params[key] for key in cls.EXPECTED_DTYPES if key in params}

        # Validate the parameter datatypes
        cls.validate(filtered_params)

        return filtered_params

    # Create validation method
    @staticmethod
    def validate(data: Dict[str, Any]):
        """
        Validate the input dictionary against the `VariogramBase` class definition/schema.

        Parameters
        ----------
        data: Dict[str, Any]
            A dictionary containing the parameters that will be validated.

        Raises
        ----------
        TypedError:
            If any value does not match the expected datatype.
        """

        # Define expected datatypes
        validate_typed_dict(data, VariogramEmpirical.EXPECTED_DTYPES)
        # FOR DEBUGGING
        # --------
        # print("Validate passed.")
        # --------


class VariogramOptimize(TypedDict):
    max_fun_evaluations: posint
    cost_fun_tolerance: realposfloat
    gradient_tolerance: realposfloat
    finite_step_size: realposfloat
    trust_region_solver: Literal["base", "exact"]
    x_scale: Union[Literal["jacobian"], np.ndarray[realposfloat]]
    jacobian_approx: Literal["forward", "central"]

    # Define default values
    DEFAULT_VALUES = {
        "max_fun_evaluations": 500,
        "cost_fun_tolerance": 1e-6,
        "solution_tolerance": 1e-6,
        "gradient_tolerance": 1e-4,
        "finite_step_size": 1e-8,
        "trust_region_solver": "exact",
        "x_scale": "jacobian",
        "jacobian_approx": "central",
    }

    # Define the expected datatypes
    EXPECTED_DTYPES = {
        "max_fun_evaluations": posint,
        "cost_fun_tolerance": realposfloat,
        "solution_tolerance": realposfloat,
        "gradient_tolerance": realposfloat,
        "finite_step_size": realposfloat,
        "trust_region_solver": Literal["base", "exact"],
        "x_scale": Union[Literal["jacobian"], np.ndarray[realposfloat]],
        "jacobian_approx": Literal["central", "forward"],
    }

    @classmethod
    def create(
        cls,
        max_fun_evaluations: posint = 500,
        cost_fun_tolerance: realposfloat = 1e-6,
        solution_tolerance: realposfloat = 1e-6,
        gradient_tolerance: realposfloat = 1e-4,
        finite_step_size: realposfloat = 1e-8,
        trust_region_solver: Literal["exact", "base"] = "exact",
        x_scale: Union[Literal["jacobian"], np.ndarray[realposfloat]] = "jacobian",
        jacobian_approx: Literal["central", "forward"] = "central",
        **kwargs,
    ) -> "VariogramOptimize":
        """
        Base variogram model parameters

        Parameters
        ----------
        max_fun_evaluations: posint
            The maximum number of evaluations. Defaults to 500.
        cost_fun_tolerance: realposfloat
            Threshold used for determining convergence via incremental changes of the cost function.
            Defaults to 1e-6.
        solution_tolerance: realposfloat
            Threshold used for determining convergence via change of the independent variables.
            Defaults to 1e-8.
        gradient_tolerance: realposfloat
            Threshold used for determining convergence via the gradient norma. Defaults to 1e-8.
        finite_step_size: realposfloat
            The relative step sizes used for approximating the Jacobian via finite differences.
        trust_region_solver: Literal["exact", "base"]
            The method used for solving the trust-region problem by either using the Jacobian
            computed from the first iteration (`"base"`) or via singular value decomposition
            (`"exact"`). Defaults to "exact".
        x_scale: Union[Literal["jacobian"], np.ndarray[realposfloat]]
            When `x_scale="jacobian"`, the characteristic scale is updated across numerical
            iterations via the inverse norms of the Jacobian matrix. Otherwise, a `np.ndarray`
            of the same length as `fit_parameters` can provide a constant scaling factor.
        jacobian_approx: Literal["forward", "central"]
            Indicates whether forward differencing (`"forward"`) or central differencing
            (`"central"`) should be used to approximate the Jacobian matrix.

        Returns
        ----------
        VariogramOptimize: A validated dictionary with the user-defined variogram optimizatization
        parameter values and default values for any missing parameters/keys.
        """

        # User-defined parameters
        inputs = {
            "max_fun_evaluations": max_fun_evaluations,
            "cost_fun_tolerance": cost_fun_tolerance,
            "solution_tolerance": solution_tolerance,
            "gradient_tolerance": gradient_tolerance,
            "finite_step_size": finite_step_size,
            "trust_region_solver": trust_region_solver,
            "x_scale": x_scale,
            "jacobian_approx": jacobian_approx,
        }

        # Merge the default values with those provided by the user
        params = {**cls.DEFAULT_VALUES, **inputs}

        # Filter the parameter keys
        filtered_params = {key: params[key] for key in cls.EXPECTED_DTYPES if key in params}

        # Validate the parameter datatypes
        cls.validate(filtered_params)

        return filtered_params

    # Create validation method
    @staticmethod
    def validate(data: Dict[str, Any]):
        """
        Validate the input dictionary against the `VariogramBase` class definition/schema.

        Parameters
        ----------
        data: Dict[str, Any]
            A dictionary containing the parameters that will be validated.

        Raises
        ----------
        TypedError:
            If any value does not match the expected datatype.
        """

        # Define expected datatypes
        validate_typed_dict(data, VariogramOptimize.EXPECTED_DTYPES)
        # FOR DEBUGGING
        # --------
        # print("Validate passed.")


class InitialValues(TypedDict):
    """Initial values type-class"""

    min: Optional[posfloat]
    value: Optional[realposfloat]
    max: Optional[posfloat]

    # Default values for parameters
    DEFAULT_STRUCTURE = {"min": 0.0, "value": 0.0, "max": np.inf}

    # Define expected types for parameter details
    EXPECTED_DTYPES = {
        "min": Optional[posfloat],
        "value": Optional[realposfloat],
        "max": Optional[posfloat],
    }


class VariogramInitial(TypedDict, total=False):
    fit_parameters: Union[List[str], Dict[str, InitialValues]]

    # Define valid parameters
    VALID_PARAMETERS = ["correlation_range", "decay_power", "hole_effect_range", "nugget", "sill"]

    def __init__(self, fit_parameters: Union[List[str], Dict[str, InitialValues]]):
        # Initialize the instance
        self.fit_parameters = fit_parameters

    @classmethod
    def create(
        cls, fit_parameters: Union[List[str], Dict[str, InitialValues]]
    ) -> "VariogramInitial":
        """
        Create a ParameterConfig from a list of parameter names or a dictionary.
        """

        # Fill missing keys
        if isinstance(fit_parameters, list):
            fit_parameters = {
                param: InitialValues.DEFAULT_STRUCTURE.copy() for param in fit_parameters
            }
        else:
            for param, details in fit_parameters.items():
                if not isinstance(details, dict):
                    raise TypeError(f"Value for '{param}' must be a dictionary.")
                for key in InitialValues.DEFAULT_STRUCTURE:
                    if key not in details:
                        fit_parameters[param][key] = InitialValues.DEFAULT_STRUCTURE[key]

        # Validate
        cls.validate(fit_parameters)

        # Update order
        fit_parameters = {
            param: {
                key: fit_parameters[param][key] for key in InitialValues.DEFAULT_STRUCTURE.keys()
            }
            for param in fit_parameters.keys()
        }

        return cls(fit_parameters)

    @staticmethod
    def validate(params: Dict[str, InitialValues]) -> None:
        """
        Validate the input dictionary against the expected structure.
        """

        # Subset `fit_parameters` to only include the appropriate parameters
        unexpected_param = set(params.keys()).difference(VariogramInitial.VALID_PARAMETERS)
        # ---- Raise Error
        if unexpected_param:
            # ---- Create list
            unexpected_list = ", ".join(f"'{par}'" for par in unexpected_param)
            # ---- Format expected list
            expected_list = ", ".join(f"'{par}'" for par in VariogramInitial.VALID_PARAMETERS)
            # ---- Print Error
            raise ValueError(
                f"Unexpected parameter(s): {unexpected_list}. Initial values ('min', 'value' "
                f"and 'max') for variogram optimization are only accepted/valid for the "
                f"following parameters: {expected_list}."
            )

        # Validate type
        for param, details in params.items():
            try:
                validate_typed_dict(details, InitialValues.EXPECTED_DTYPES)
            except Exception as e:
                raise TypeError(f"Parameter '{param}': initial {str(e)[0].lower() + str(e)[1:]}")

        # Ensure that values are ordered appropriately
        invalid_values = [
            key
            for key, value in params.items()
            if not (value["min"] <= value["value"] <= value["max"])
        ]
        # ---- Raise Error
        if invalid_values:
            # ---- Add outer apostrophes
            invalid_list = ", ".join(f"'{par}'" for par in invalid_values)
            # ---- Print
            raise TypeError(
                f"Invalid initial values for: {invalid_list}. Values must satisfy the logic: "
                f"`min` <= value` <= `max`."
            )

        # FOR DEBUGGING
        # --------
        # print("Validate passed.")
        # --------

####################################################################################################
# PANDERA VALIDATORS
# --------------------------------------------------------------------------------------------------
def extract_errors(data, key="error"):
    """
    Utility function for extract `pandera.SchemaError` and `pandera.SchemaErrors` messages
    """
    errors = []
    
    if isinstance(data, dict):
        # If the current level is a dictionary, iterate through its keys
        for k, v in data.items():
            if k == key:
                errors.append(f"   -{v.capitalize()}")  # Append the error message if key matches
            else:
                errors.extend(extract_errors(v, key))  # Recursively search nested dictionaries
    elif isinstance(data, list):
        # If the current level is a list, iterate through its elements
        for item in data:
            errors.extend(extract_errors(item, key))  # Recursively search nested lists
    
    return errors
class BaseDataFrame(DataFrameModel):

    class Config:
        drop_invalid_rows=True

    @classmethod
    def get_column_types(cls) -> dict:
        # Get the schema of the DataFrameModel
        schema = cls.to_schema()
        column_types = {}
        
        # Iterate over columns in the schema
        for column_name, column_schema in schema.columns.items():
            # Access the dtype directly
            column_types[column_name] = column_schema.dtype
        
        return column_types   

    @classmethod
    def judge(cls, df: pd.DataFrame) -> pd.DataFrame:
        # ---- Collect errors
        errors = []
        try:
            return cls.validate(df, lazy=True)
        except SchemaErrors as e:
            e.__traceback__ = None
            errors.append(e)
        # ---- If Errors occur:
        if errors:
            # ---- Join unique errors
            errors_stk = "\n".join(extract_errors(errors[0].message))
            # ---- Format the error message
            message = (
                f"The following DataFrame validation errors were flagged: \n"
                f"{errors_stk}"
            )
            # ---- Raise Error
            raise SchemaError(cls, df, message)

    @classmethod
    def validate_df(cls, df):
        # --- Format the column names
        df.columns = [col.lower() for col in df.columns]
        # ---- Get column types
        column_types = cls.get_column_types()
        # ---- Initialize column names
        valid_cols = []
        # Apply type coercion based on column types and alias patterns
        for column_name, dtype in column_types.items():
            pandas_dtype = str(dtype)  # Convert dtype to string directly
            if not dtype:
                pandas_dtype = int
            
            # Apply coercion based on column patterns            
            for col in df.columns:
                if re.match(column_name, col):
                    # ---- Populate valid column names
                    valid_cols.append(col)
                    # Coerce the column to the appropriate dtype
                    if df[col].dtype == object and dtype.type.kind in ["i", "u", "f"]:
                        df[col] = df[col].astype(float).astype(pandas_dtype)
                    else:
                        df[col] = df[col].astype(pandas_dtype, errors="ignore")        
        # ---- Pass to validation
        return cls.judge(df.filter(valid_cols))

class LengthBiodata(BaseDataFrame):
    haul_num: Series = Field(nullable=False)
    length: Series[float] = Field(gt=0.0, nullable=False)
    length_count: Series[int] = Field(ge=0, nullable=False)
    sex: Series = Field(nullable=False)
    species_id: Series = Field(nullable=False)

    @check("haul_num", name="'haul_num' element-wise datatypes",
           error="Column datatype should be either 'int' or 'float'")
    def validate_haul_num(cls, haul_num: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in haul_num])

    @check("sex", name="'sex' element-wise datatypes",
           error=(
               "Column datatype should either be all 'int', or all 'str' contained within "
               "['male', 'm', 'female', 'f', 'unsexed', 'u']"
            ))
    def validate_sex(cls, sex: Series) -> Series[bool]:
        # ---- Check if value is 'int'
        if all(isinstance(x, str) for x in sex):
            return Series([value in ["male", "female", "unsexed", "m", "f", "u"] for value in sex])
        else:
            return Series([isinstance(value, int) for value in sex])

    @check("species_id", name="'species_id' element-wise datatypes",
           error="Column datatype should be either 'int', 'float', or 'str'")
    def validate_species_id(cls, species_id: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float, str)) for value in species_id])

class CatchBiodata(BaseDataFrame):
    haul_num: Series = Field(ge=0.0, nullable=False)
    haul_weight: Series[float] = Field(ge=0.0, nullable=False)
    species_id: Series = Field(ge=0.0, nullable=False)

    @check("haul_num", name="'haul_num' element-wise datatypes",
              error="Column datatype should be either 'int' or 'float'")
    def validate_haul_num(cls, haul_num: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in haul_num])

    @check("species_id", name="'species_id' element-wise datatypes",
              error="Column datatype should be either 'int', 'float', or 'str'")
    def validate_species_id(cls, species_id: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float, str)) for value in species_id])

class SpecimenBiodata(BaseDataFrame):
    age: Series = Field(nullable=False)
    haul_num: Series = Field(nullable=False)
    length: Series[float] = Field(gt=0.0, nullable=False)
    sex: Series = Field(nullable=False)
    species_id: Series = Field(nullable=False)
    weight: Series[float] = Field(gt=0.0, nullable=False)
        
    @check("age", "haul_num", name="element-wise datatypes",
           error="Column datatype should be either 'int' or 'float'")
    def validate_haul_num(cls, v: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in v])

    @check("sex", name="'sex' element-wise datatypes",
           error=(
               "Column datatype should either be all 'int', or all 'str' contained within "
               "['male', 'm', 'female', 'f', 'unsexed', 'u']"
            ))
    def validate_sex(cls, sex: Series) -> Series[bool]:
        # ---- Check if value is 'int'
        if all(isinstance(x, str) for x in sex):
            return Series([value in ["male", "female", "unsexed", "m", "f", "u"] for value in sex])
        else:
            return Series([isinstance(value, int) for value in sex])

    @check("species_id", name="'species_id' element-wise datatypes",
           error="Column datatype should be either 'int', 'float', or 'str'")
    def validate_species_id(cls, species_id: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float, str)) for value in species_id])

class HaulTransect(BaseDataFrame):
    haul_num: Series = Field(nullable=False)
    transect_num: Series = Field(nullable=False)
    
    @check("haul_num", "transect_num", name="element-wise datatypes",
           error="Column datatype should be either 'int' or 'float'")
    def validate_haul_num(cls, v: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in v])

class KSStrata(BaseDataFrame):
    fraction: Series[float] = Field(ge=0.0, le=1.0, nullable=False, regex=True)
    haul: Series = Field(nullable=False, regex=True)
    stratum: Series = Field(nullable=False, regex=True)
    
    @check("haul", name="element-wise datatypes",
           error="Column datatype should be either 'int' or 'float'")
    def validate_haul(cls, v: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in v])

    @check("stratum", name="'stratum' element-wise datatypes",
           error="Column datatype should be either 'int', 'float', or 'str'")
    def validate_stratum(cls, stratum: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float, str)) for value in stratum])

class GeoStrata(KSStrata):
    haul: Series = Field(nullable=False, regex=True)
    northlimit_latitude: Series[float] = Field(ge=-90.0, le=90.0, nullable=False)
    stratum: Series = Field(nullable=False, regex=True)

class AcousticData(BaseDataFrame):
    haul: Series = Field(nullable=False, regex=True)
    latitude: Series[float] = Field(ge=-90.0, le=90.0, nullable=False, regex=True, coerce=True)
    longitude: Series[float] = Field(ge=-180.0, le=180.0, nullable=False, regex=True, coerce=True)
    nasc: Series[float] = Field(ge=0.0, nullable=False, coerce=True)
    transect: Series = Field(nullable=False, regex=True)
    transect_spacing: Series[float] = Field(ge=0.0, nullable=False, regex=False, coerce=True)
    vessel_log_start: Series[float] = Field(ge=0.0, nullable=False, coerce=True)
    vessel_log_end: Series[float] = Field(ge=0.0, nullable=False, coerce=True)
    
    @check("haul", name="element-wise datatypes",
           error="Column datatype should be either 'int' or 'float'")
    def validate_haul(cls, v: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in v])
    
    @check("transect", name="element-wise datatypes",
           error="Column datatype should be either 'int' or 'float'")
    def validate_transect(cls, v: Series) -> Series[bool]:
        return Series([isinstance(value, (int, float)) for value in v])

class IsobathData(BaseDataFrame):
    latitude: Series[float] = Field(ge=-90.0, le=90.0, nullable=False, regex=True, coerce=True, 
                                    alias=".*latitude.*")
    longitude: Series[float] = Field(ge=-180.0, le=180.0, nullable=False, regex=True, coerce=True, 
                                    alias=".*longitude.*")
class KrigingMesh(IsobathData):
    fraction: Series[float] = Field(ge=0.0, le=1.0, nullable=False, regex=True, coerce=True,
                                    alias=".*fraction.*")

class VarioKrigingPara(BaseDataFrame):
    y_offset: Series[float] = Field(ge=-90.0, le=90.0, nullable=False, alias="dataprep.y_offset")
    corr: Series[float] = Field(ge=0.0, nullable=False, alias="vario.corr")
    hole: Series[float] = Field(ge=0.0, nullable=False, alias="vario.hole")
    lscl: Series[float] = Field(ge=0.0, nullable=False, alias="vario.lscl")
    model: Series[int] = Field(nullable=False, alias="vario.model")
    nugt: Series[float] = Field(ge=0.0, nullable=False, alias="vario.nugt")
    powr: Series[float] = Field(ge=0.0, nullable=False, alias="vario.powr")
    range: Series[float] = Field(ge=0.0, nullable=False, alias="vario.range")
    res: Series[float] = Field(gt=0.0, nullable=False, alias="vario.res")
    sill: Series[float] = Field(ge=0.0, nullable=False, alias="vario.sill")  
    ytox_ratio: Series[float] = Field(nullable=False, alias="vario.ytox_ratio")
    ztox_ratio: Series[float] = Field(nullable=False, alias="vario.ztox_ratio")
    blk_nx: Series[int] = Field(gt=0, nullable=False, alias="krig.blk_nx")
    blk_ny: Series[int] = Field(gt=0, nullable=False, alias="krig.blk_ny")
    blk_nz: Series[int] = Field(gt=0, nullable=False, alias="krig.blk_nz")
    dx0: Series[float] = Field(ge=-180.0, le=180.0, nullable=False, alias="krig.dx0")
    dx: Series[float] = Field(nullable=False, alias="krig.dx")
    dy0: Series[float] = Field(ge=-90.0, le=90.0, nullable=False, alias="krig.dy0")
    dy: Series[float] = Field(nullable=False, alias="krig.dy")
    dz: Series[float] = Field(nullable=False, alias="krig.dz")
    elim: Series[float] = Field(nullable=False, alias="krig.elim")
    eps: Series[float] = Field(nullable=False, alias="krig.eps")
    kmax: Series[int] = Field(gt=0, nullable=False, alias="krig.kmax")
    kmin: Series[int] = Field(gt=0, nullable=False, alias="krig.kmin")
    nx: Series[int] = Field(gt=0, nullable=False, alias="krig.nx")
    ny: Series[int] = Field(gt=0, nullable=False, alias="krig.ny")
    nz: Series[int] = Field(gt=0, nullable=False, alias="krig.nz")
    ratio: Series[float] = Field(nullable=False, alias="krig.ratio")
    srad: Series[float] = Field(gt=0.0, nullable=False, alias="krig.srad")
    x_res: Series[float] = Field(nullable=False, alias="krig.x_res")
    xmin: Series[float] = Field(nullable=False, alias="krig.xmin")
    xmax: Series[float] = Field(nullable=False, alias="krig.xmax")
    xmin0: Series[float] = Field(ge=-180.0, le=180.0, nullable=False, alias="krig.xmin0")
    xmax0: Series[float] = Field(ge=-180.0, le=180.0, nullable=False, alias="krig.xmax0")    
    y_res: Series[float] = Field(nullable=False, alias="krig.y_res")
    ymin: Series[float] = Field(nullable=False, alias="krig.ymin")
    ymax: Series[float] = Field(nullable=False, alias="krig.ymax")
    ymin0: Series[float] = Field(ge=-90.0, le=90.0, nullable=False, alias="krig.ymin0")
    ymax0: Series[float] = Field(ge=-90.0, le=90.0, nullable=False, alias="krig.ymax0")