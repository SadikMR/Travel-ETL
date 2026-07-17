from tests.test_data.common_data import (
    QUERY_PARAMS,
    BOOKINGS,
    TRANSFORMED_BOOKINGS,
    LOADED_COUNT,
    EMPTY_LIST,
    EMPTY_DICT,
    NONE_VALUE,
    CONNECTION_ERROR,
)

VALUE_ERROR_MESSAGE = (
    "Both 'updated_from' and 'updated_to' must be provided."
)

NO_DATA_NULL_MESSAGE = (
    "No booking data received from API: response was empty or null."
)

NO_DATA_INVALID_MESSAGE = (
    "No booking data received from API: response was not a list."
)

NO_DATA_EMPTY_MESSAGE = (
    "No booking data received from API: response was empty."
)

API_REQUEST_FAILED_MESSAGE = (
    f"API request failed: {CONNECTION_ERROR}"
)