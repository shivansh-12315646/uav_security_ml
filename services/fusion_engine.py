"""
Multi-sensor fusion engine for UAV threat assessment.

Combines RF anomaly scores, GNSS spoofing scores, and other indicators
into a unified threat score and threat level (0-4).
"""
import logging

logger = logging.getLogger(__name__)

THREAT_LEVEL_DESCRIPTIONS = {
    0: 'Normal operation',
    1: 'Suspicious activity',
    2: 'Confirmed low-severity attack',
    3: 'Confirmed high-severity attack',
    4: 'Critical multi-vector attack',
}

THREAT_LEVEL_RESPONSES = {
    0: ['continue_normal_logging'],
    1: ['increase_monitoring', 'log_detailed_telemetry', 'alert_operator', 'reduce_speed_30pct'],
    2: ['activate_backup_navigation', 'return_to_home', 'increase_logging_verbosity', 'send_emergency_alert'],
    3: ['emergency_rth_or_imu_hover', 'activate_emergency_comms', 'disable_vulnerable_sensors'],
    4: ['immediate_landing', 'imu_barometer_only', 'cut_external_links', 'log_forensic_data'],
}


class FusionEngine:
    """
    Combines multiple threat indicators into a unified threat assessment.

    Implements the weighted fusion algorithm from the patent:
        S_combined = w_RF × S_RF + w_GNSS × S_GNSS + w_other × S_other
    where w_RF + w_GNSS + w_other = 1
    """

    DEFAULT_WEIGHTS = {
        'rf': 0.6,
        'gnss': 0.4,
        'other': 0.0,
    }

    THRESHOLDS = {
        'suspicious': 0.3,
        'low_attack': 0.5,
        'high_attack': 0.7,
        'critical': 0.85,
    }

    def calculate_combined_threat_score(self, rf_score, gnss_score, other_indicators=None, weights=None):
        """
        Calculate weighted combined threat score (0.0 – 1.0).

        Args:
            rf_score: RF anomaly score (0.0 – 1.0)
            gnss_score: GNSS spoofing score (0.0 – 1.0)
            other_indicators: Additional score (float) or dict of {indicator: score}
            weights: Optional dict with keys 'rf', 'gnss', 'other' (auto-normalised)

        Returns:
            float: Combined threat score in [0.0, 1.0]
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        w_rf = float(weights.get('rf', self.DEFAULT_WEIGHTS['rf']))
        w_gnss = float(weights.get('gnss', self.DEFAULT_WEIGHTS['gnss']))
        w_other = float(weights.get('other', self.DEFAULT_WEIGHTS['other']))

        total = w_rf + w_gnss + w_other
        if total > 0:
            w_rf /= total
            w_gnss /= total
            w_other /= total

        other_score = 0.0
        if other_indicators is not None:
            if isinstance(other_indicators, dict):
                # Simple average across all indicators; all are assumed equally weighted.
                # Pass a pre-computed float if you need custom per-indicator weights.
                other_score = (
                    sum(other_indicators.values()) / len(other_indicators)
                    if other_indicators else 0.0
                )
            else:
                other_score = float(other_indicators)

        combined = w_rf * float(rf_score) + w_gnss * float(gnss_score) + w_other * other_score
        return round(min(max(combined, 0.0), 1.0), 4)

    def determine_threat_level(self, combined_score):
        """
        Map a combined score (0.0 – 1.0) to a threat level (0 – 4).

        Returns:
            int: Threat level in range [0, 4]
        """
        if combined_score >= self.THRESHOLDS['critical']:
            return 4
        if combined_score >= self.THRESHOLDS['high_attack']:
            return 3
        if combined_score >= self.THRESHOLDS['low_attack']:
            return 2
        if combined_score >= self.THRESHOLDS['suspicious']:
            return 1
        return 0

    def get_recommended_response(self, threat_level, attack_types=None):
        """
        Return recommended response actions for the given threat level.

        Args:
            threat_level: Integer threat level (0 – 4)
            attack_types: Optional list of active attack type labels

        Returns:
            dict with 'threat_level', 'threat_description', 'actions', 'attack_types'
        """
        actions = THREAT_LEVEL_RESPONSES.get(threat_level, THREAT_LEVEL_RESPONSES[0])
        return {
            'threat_level': threat_level,
            'threat_description': THREAT_LEVEL_DESCRIPTIONS.get(threat_level, 'Unknown'),
            'actions': list(actions),
            'attack_types': list(attack_types) if attack_types else [],
        }

    def calculate_combined_threat(self, rf_score, gnss_score, attack_type=None, other_indicators=None):
        """
        Full pipeline: score → threat level → recommended response.

        Args:
            rf_score: RF anomaly confidence (0.0 – 1.0)
            gnss_score: GNSS spoofing confidence (0.0 – 1.0)
            attack_type: Predicted attack label (string)
            other_indicators: Additional indicators (float or dict)

        Returns:
            dict with 'combined_score', 'threat_level', 'threat_description',
                      'recommended_actions', 'attack_types'
        """
        combined_score = self.calculate_combined_threat_score(rf_score, gnss_score, other_indicators)
        threat_level = self.determine_threat_level(combined_score)
        attack_types = (
            [attack_type] if attack_type and str(attack_type).lower() != 'normal' else []
        )
        response = self.get_recommended_response(threat_level, attack_types)

        logger.info(
            "Fusion result: rf=%.3f gnss=%.3f combined=%.4f level=%d (%s)",
            rf_score, gnss_score, combined_score, threat_level,
            THREAT_LEVEL_DESCRIPTIONS.get(threat_level, 'Unknown')
        )

        return {
            'combined_score': combined_score,
            'threat_level': threat_level,
            'threat_description': THREAT_LEVEL_DESCRIPTIONS.get(threat_level, 'Unknown'),
            'recommended_actions': response['actions'],
            'attack_types': attack_types,
        }


# Shared singleton instance
fusion_engine = FusionEngine()
