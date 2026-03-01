"""
MAVLink interface for drone flight controller communication.

This module provides a simulated MAVLink interface for development and
testing. All commands are logged rather than sent to real hardware.
Replace the method bodies with actual pymavlink calls for live integration.
"""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

VALID_FLIGHT_MODES = ['STABILIZE', 'LOITER', 'RTL', 'LAND', 'GUIDED', 'AUTO', 'ALT_HOLD']


class MAVLinkInterface:
    """
    Simulated MAVLink interface for future real drone integration.

    Provides command validation and safety checks so that the calling code
    can be written against this interface today and connected to real
    hardware by swapping the implementations below.
    """

    def __init__(self):
        self._connected = False
        self._drone_state = {
            'mode': 'LOITER',
            'armed': False,
            'position': {'lat': 0.0, 'lon': 0.0, 'alt': 0.0},
            'battery': 100.0,
            'attitude': {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0},
        }

    def change_flight_mode(self, mode):
        """
        Send flight mode change command to flight controller.

        Args:
            mode: Target flight mode string (e.g. 'RTL', 'LAND', 'LOITER')

        Returns:
            dict with 'success', 'mode', and optional 'error'
        """
        mode = str(mode).upper()
        if mode not in VALID_FLIGHT_MODES:
            logger.error("[MAVLINK] Invalid flight mode requested: %s", mode)
            return {'success': False, 'error': f'Invalid mode: {mode}'}

        logger.warning("[MAVLINK SIM] Flight mode change → %s", mode)
        self._drone_state['mode'] = mode
        return {'success': True, 'mode': mode, 'timestamp': timezone.now().isoformat()}

    def send_position_setpoint(self, lat, lon, alt):
        """
        Send position setpoint command to flight controller.

        Args:
            lat: Target latitude (-90 to 90)
            lon: Target longitude (-180 to 180)
            alt: Target altitude in metres (≥ 0)

        Returns:
            dict with 'success' and optional 'error'
        """
        if not self._validate_position(lat, lon, alt):
            return {'success': False, 'error': 'Invalid position parameters'}

        logger.info("[MAVLINK SIM] Position setpoint → lat=%s lon=%s alt=%s", lat, lon, alt)
        self._drone_state['position'] = {'lat': float(lat), 'lon': float(lon), 'alt': float(alt)}
        return {
            'success': True,
            'position': {'lat': float(lat), 'lon': float(lon), 'alt': float(alt)},
            'timestamp': timezone.now().isoformat(),
        }

    def get_drone_state(self):
        """
        Read current drone state from flight controller.

        Returns:
            dict with mode, armed, position, battery, attitude, timestamp
        """
        logger.debug("[MAVLINK SIM] Reading drone state")
        return {**self._drone_state, 'timestamp': timezone.now().isoformat()}

    def trigger_failsafe(self):
        """
        Trigger drone failsafe (RTL).

        Returns:
            dict with 'success', 'action', 'mode', 'timestamp'
        """
        logger.critical("[MAVLINK SIM] FAILSAFE TRIGGERED – switching to RTL")
        self._drone_state['mode'] = 'RTL'
        return {
            'success': True,
            'action': 'failsafe',
            'mode': 'RTL',
            'timestamp': timezone.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_position(self, lat, lon, alt):
        """Validate position parameters before sending to flight controller."""
        try:
            return (
                -90.0 <= float(lat) <= 90.0
                and -180.0 <= float(lon) <= 180.0
                and float(alt) >= 0.0
            )
        except (TypeError, ValueError):
            return False


# Shared singleton instance
mavlink_interface = MAVLinkInterface()
