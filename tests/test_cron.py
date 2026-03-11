import pytest
from syndicate import convert_input_to_cron_expression


@pytest.mark.parametrize(
    "rate, time, expected",
    [
        ("hourly", None, "0 * * * *"),
        ("daily", None, "0 9 * * *"),
        ("weekly", None, "0 9 * * 1"),
        ("monthly", None, "0 9 1 * *"),
        ("daily", "14:00", "0 14 * * *"),
        ("weekly", "Monday 09:00", "0 9 * * 1"),
        ("weekly", "Tuesday 18:30", "30 18 * * 2"),
        ("weekly", "Friday 23:45", "45 23 * * 5"),
        ("monthly", "1 00:00", "0 0 1 * *"),
        ("monthly", "15 12:30", "30 12 1 * *"),
        ("hourly", "15:00", "0 * * * *"),
        ("hourly", "15:30", "30 * * * *"),
        ("custom", "0 0 * * 0", "0 0 * * 0"),
        ("custom", "30 14 * * 1-5", "30 14 * * 1-5"),
    ],
)
def test_convert_input_to_cron_expression(rate, time, expected):
    assert convert_input_to_cron_expression(rate, time) == expected


@pytest.mark.parametrize(
    "rate, time",
    [
        ("daily", "invalid-time"),
        ("weekly", "invalid-time"),
        ("monthly", "invalid-time"),
        ("hourly", "invalid-time"),
        ("custom", "invalid-time"),
    ],
)
def test_throws_value_error_for_invalid_time(rate, time):
    with pytest.raises(ValueError):
        convert_input_to_cron_expression(rate, time)


@pytest.mark.parametrize(
    "rate, time",
    [
        ("custom", "invalid-cron"),
        ("custom", "0 0 * *"),  # Missing fields
        ("custom", "0 0 * * * * * *"),  # Too many fields
        ("custom", "invalid cron expression"),
    ],
)
def test_throws_value_error_for_invalid_custom_cron(rate, time):
    with pytest.raises(ValueError):
        convert_input_to_cron_expression(rate, time)


@pytest.mark.parametrize(
    "rate, time",
    [
        ("invalid-rate", None),
        ("unknown", None),
        ("unsupported", None),
    ],
)
def test_throws_value_error_for_invalid_rate(rate, time):
    with pytest.raises(ValueError):
        convert_input_to_cron_expression(rate, time)
