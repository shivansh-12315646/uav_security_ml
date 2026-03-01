"""
Autonomous response module for UAV threat mitigation.

Executes graduated countermeasures based on threat level (0-4) as defined
in the patent's Autonomous Response and Fallback Strategies section.
"""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

RESPONSE_DESCRIPTIONS = {
    0: 'No action - normal operation',
    1: 'Increased monitoring, operator alerted, speed reduced',
    2: 'Backup navigation activated, return-to-home initiated',
    3: 'Emergency RTH or IMU hover, emergency comms activated',
    4: 'Immediate landing, IMU-only navigation, external links disabled',
}


class AutonomousResponse:
    """
    Executes automated countermeasures based on threat level.

    All hardware interaction methods log simulated commands so the module
    is ready to be wired to real MAVLink calls without logic changes.
    """

    def execute_response(self, threat_level, attack_context=None):
        """
        Execute the appropriate response for the given threat level.

        Args:
            threat_level: Integer (0 – 4)
            attack_context: dict with additional context (attack_types, scores, …)

        Returns:
            dict with 'threat_level', 'actions_taken', 'response_summary',
                      'timestamp', 'success', 'operator_notified'
        """
        attack_context = attack_context or {}
        actions_taken = []
        operator_notified = False

        logger.info("[AUTONOMOUS] Executing response for threat level %d", threat_level)

        if threat_level == 0:
            self._continue_normal_logging()
            actions_taken.append('normal_logging')

        elif threat_level == 1:
            actions_taken, operator_notified = self._level1_response(attack_context)

        elif threat_level == 2:
            actions_taken, operator_notified = self._level2_response(attack_context)

        elif threat_level == 3:
            actions_taken, operator_notified = self._level3_response(attack_context)

        else:  # level 4+
            actions_taken, operator_notified = self._level4_response(attack_context)

        self.log_incident({
            'threat_level': threat_level,
            'actions': actions_taken,
            'context': attack_context,
        })

        return {
            'threat_level': threat_level,
            'actions_taken': actions_taken,
            'response_summary': RESPONSE_DESCRIPTIONS.get(min(threat_level, 4), 'Unknown response'),
            'timestamp': timezone.now().isoformat(),
            'success': True,
            'operator_notified': operator_notified,
        }

    # ------------------------------------------------------------------
    # Per-level response handlers
    # ------------------------------------------------------------------

    def _level1_response(self, context):
        """Level 1 – Suspicious activity."""
        actions = []
        self._increase_monitoring_frequency()
        actions.append('increased_monitoring')
        self._log_detailed_telemetry(context)
        actions.append('detailed_telemetry_logged')
        self.send_operator_alert('low', f"Suspicious activity detected: {context.get('attack_types', [])}")
        actions.append('operator_alerted')
        self._reduce_speed(30)
        actions.append('speed_reduced_30pct')
        return actions, True

    def _level2_response(self, context):
        """Level 2 – Confirmed low-severity attack."""
        actions = []
        self.activate_backup_navigation()
        actions.append('backup_navigation_activated')
        self.trigger_return_to_home()
        actions.append('return_to_home_initiated')
        logger.warning("[AUTONOMOUS] Increasing logging verbosity")
        actions.append('logging_verbosity_increased')
        self.send_operator_alert('high', f"Confirmed attack detected: {context.get('attack_types', [])}")
        actions.append('emergency_alert_sent')
        return actions, True

    def _level3_response(self, context):
        """Level 3 – Confirmed high-severity attack."""
        actions = []
        attack_types = context.get('attack_types', [])
        gnss_trusted = 'GPS Spoofing' not in str(attack_types)
        if gnss_trusted:
            self.trigger_return_to_home()
            actions.append('emergency_rth_initiated')
        else:
            self._activate_imu_hover()
            actions.append('imu_hover_activated')
        self._activate_emergency_comms()
        actions.append('emergency_comms_activated')
        self._disable_vulnerable_sensors(attack_types)
        actions.append('vulnerable_sensors_disabled')
        self.send_operator_alert('critical', f"High-severity attack: {attack_types}")
        actions.append('critical_alert_sent')
        return actions, True

    def _level4_response(self, context):
        """Level 4 – Critical multi-vector attack."""
        actions = []
        self.trigger_emergency_landing()
        actions.append('emergency_landing_initiated')
        self.activate_backup_navigation()
        actions.append('imu_barometer_only')
        self._cut_external_links()
        actions.append('external_links_disabled')
        self._log_forensic_data(context)
        actions.append('forensic_data_logged')
        self.send_operator_alert(
            'critical',
            f"CRITICAL multi-vector attack: {context.get('attack_types', [])}"
        )
        actions.append('critical_alert_sent')
        return actions, True

    # ------------------------------------------------------------------
    # Public action primitives
    # ------------------------------------------------------------------

    def trigger_return_to_home(self):
        """Trigger Return-to-Home flight mode."""
        logger.warning("[AUTONOMOUS] Triggering Return-to-Home (RTH) mode")

    def trigger_emergency_landing(self):
        """Trigger immediate emergency landing at current position."""
        logger.critical("[AUTONOMOUS] Triggering EMERGENCY LANDING at current position")

    def activate_backup_navigation(self):
        """Activate backup navigation using IMU and barometer only."""
        logger.warning("[AUTONOMOUS] Activating backup navigation: IMU + Barometer")

    def send_operator_alert(self, severity, message):
        """Send alert notification to human operator."""
        logger.warning("[OPERATOR ALERT] severity=%s: %s", severity, message)

    def log_incident(self, threat_details):
        """Log full incident details for forensic analysis."""
        logger.info("[INCIDENT LOG] %s", threat_details)

    # ------------------------------------------------------------------
    # Private helpers (simulated hardware commands)
    # ------------------------------------------------------------------

    def _continue_normal_logging(self):
        logger.debug("[AUTONOMOUS] Normal operation – no action required")

    def _increase_monitoring_frequency(self):
        logger.info("[AUTONOMOUS] Increasing monitoring frequency")

    def _log_detailed_telemetry(self, context):
        logger.info("[AUTONOMOUS] Detailed telemetry: %s", context)

    def _reduce_speed(self, percent):
        logger.info("[AUTONOMOUS] Reducing maximum speed by %d%%", percent)

    def _activate_imu_hover(self):
        logger.warning("[AUTONOMOUS] Activating controlled hover using IMU")

    def _activate_emergency_comms(self):
        logger.warning("[AUTONOMOUS] Activating emergency communication fallback")

    def _disable_vulnerable_sensors(self, attack_types):
        logger.warning("[AUTONOMOUS] Disabling vulnerable sensors for: %s", attack_types)

    def _cut_external_links(self):
        logger.critical("[AUTONOMOUS] Cutting off external command links")

    def _log_forensic_data(self, context):
        logger.critical("[FORENSIC] %s", context)


# Shared singleton instance
autonomous_response = AutonomousResponse()
