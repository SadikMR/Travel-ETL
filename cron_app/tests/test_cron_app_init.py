"""Tests for cron_app module initialization and run functions."""

from unittest.mock import Mock, patch
import pytest

import cron_app
from cronjobs.booking import run


class TestCronAppInit:
    """Tests for cron_app.create_app() and cron_app.run_cron()."""

    def test_initialize_sentry_initializes_sdk_when_dsn_present(self) -> None:
        """Verify Sentry initializes when a DSN is configured."""
        with patch.object(cron_app.Config, "SENTRY_DSN", "https://example@sentry.io/1"), patch.object(cron_app.Config, "SENTRY_ENVIRONMENT", "test"), patch.object(cron_app.Config, "SENTRY_TRACES_SAMPLE_RATE", 0.5), patch.object(cron_app.sentry_sdk, "init") as mock_init:
            cron_app.initialize_sentry()

            mock_init.assert_called_once_with(
                dsn="https://example@sentry.io/1",
                environment="test",
                traces_sample_rate=0.5,
                send_default_pii=True,
            )

    def test_create_app_initializes_database(self) -> None:
        """Verify create_app initializes database and creates tables."""
        result = cron_app.create_app()

        assert result is cron_app.db
        # Verify db object is available
        assert hasattr(cron_app.db, "initialize")
        assert hasattr(cron_app.db, "create_all")

    def test_run_cron_invokes_create_app_and_booking_run(self) -> None:
        """Verify run_cron() calls create_app and booking.run()."""
        with patch("cronjobs.booking.run") as mock_run:
            cron_app.run_cron()

            # Verify booking.run was called
            mock_run.assert_called_once_with()


class TestBookingRunFunction:
    """Tests for cronjobs.booking.run() wrapper function."""

    def test_run_invokes_booking_cron_with_dates(self) -> None:
        """Verify run() function creates BookingCron and calls run()."""
        with patch("cronjobs.booking.BookingCron") as mock_cron_cls:
            mock_cron = mock_cron_cls.return_value

            run(updated_from="2026-07-12", updated_to="2026-07-13")

            mock_cron_cls.assert_called_once_with(
                updated_from="2026-07-12",
                updated_to="2026-07-13",
            )
            mock_cron.run.assert_called_once_with()

    def test_run_invokes_booking_cron_with_none_dates(self) -> None:
        """Verify run() function works with None dates."""
        with patch("cronjobs.booking.BookingCron") as mock_cron_cls:
            mock_cron = mock_cron_cls.return_value

            run()

            mock_cron_cls.assert_called_once_with(
                updated_from=None,
                updated_to=None,
            )
            mock_cron.run.assert_called_once_with()
