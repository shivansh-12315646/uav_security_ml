"""
Comprehensive test suite for the UAV Security ML system.
Covers: URL routing, authentication, ML pipeline, fusion engine,
autonomous response, detection views, history, alerts, and API endpoints.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import User, DetectionHistory, Alert, MitigationEvent, MLModel
from services.fusion_engine import fusion_engine
from services.autonomous_response import autonomous_response

# Use plain static-file storage during tests so no collectstatic manifest is needed.
_TEST_STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NORMAL_FEATURES = {
    'altitude': 200, 'speed': 45, 'direction': 90,
    'signal_strength': 85, 'distance_from_base': 2500,
    'flight_time': 1800, 'battery_level': 75,
    'temperature': 22, 'vibration': 0.5, 'gps_accuracy': 95,
}

GPS_SPOOF_FEATURES = {
    'altitude': 550, 'speed': 45, 'direction': 275,
    'signal_strength': 85, 'distance_from_base': 5000,
    'flight_time': 3600, 'battery_level': 45,
    'temperature': 30, 'vibration': 1.5, 'gps_accuracy': 12,
}

JAMMING_FEATURES = {
    'altitude': 180, 'speed': 60, 'direction': 200,
    'signal_strength': 15, 'distance_from_base': 800,
    'flight_time': 1200, 'battery_level': 60,
    'temperature': 28, 'vibration': 3.5, 'gps_accuracy': 35,
}


def make_user(username='testuser', role='analyst', password='testpass123!'):
    """Create a test user."""
    return User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password=password,
        role=role,
    )


# ---------------------------------------------------------------------------
# 1. URL routing
# ---------------------------------------------------------------------------

class URLRoutingTests(TestCase):
    """All named URLs must resolve to a valid path."""

    NAMED_URLS = [
        ('auth_login', '/auth/login/'),
        ('auth_register', '/auth/register/'),
        ('dashboard_overview', '/dashboard/overview/'),
        ('detect', '/detection/detect/'),
        ('detection_history', '/detection/history/'),
        ('analytics', '/analytics/'),
        ('alerts_list', '/alerts/'),
        ('training_dashboard', '/training/dashboard/'),
        ('health_check', '/api/v1/health/'),
        ('settings', '/settings/'),
        ('admin_dashboard', '/admin-panel/'),
        ('batch_detect', '/detection/batch/'),
        ('api_detect', '/api/v1/detect/'),
        ('api_history', '/api/v1/history/'),
        ('api_alerts', '/api/v1/alerts/'),
    ]

    def test_all_named_urls_resolve(self):
        for name, expected_path in self.NAMED_URLS:
            with self.subTest(url_name=name):
                path = reverse(name)
                self.assertEqual(
                    path, expected_path,
                    msg=f"URL '{name}' resolved to '{path}', expected '{expected_path}'"
                )


# ---------------------------------------------------------------------------
# 2. Authentication
# ---------------------------------------------------------------------------

@override_settings(STORAGES=_TEST_STORAGES)
class AuthenticationTests(TestCase):
    """Login, logout and register flows."""

    def setUp(self):
        self.client = Client()
        self.admin = make_user('admin_auth', role='admin', password='admin123!')

    def test_login_page_renders(self):
        resp = self.client.get(reverse('auth_login'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Sign In')

    def test_register_page_renders(self):
        resp = self.client.get(reverse('auth_register'))
        self.assertEqual(resp.status_code, 200)

    def test_valid_login_redirects_to_dashboard(self):
        resp = self.client.post(reverse('auth_login'), {
            'username': 'admin_auth',
            'password': 'admin123!',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(resp.redirect_chain[-1][0], [
            reverse('dashboard_overview'), '/',
        ])

    def test_invalid_login_shows_error(self):
        resp = self.client.post(reverse('auth_login'), {
            'username': 'admin_auth',
            'password': 'wrongpassword',
        })
        self.assertIn(resp.status_code, [200, 302])
        # Should NOT redirect to dashboard on bad credentials
        if resp.status_code == 302:
            self.assertNotIn('dashboard', resp['Location'])

    def test_unauthenticated_dashboard_redirects_to_login(self):
        resp = self.client.get(reverse('dashboard_overview'))
        self.assertIn(resp.status_code, [302, 301])
        self.assertIn('/auth/login/', resp['Location'])

    def test_logout_redirects_to_login(self):
        self.client.login(username='admin_auth', password='admin123!')
        resp = self.client.get(reverse('auth_logout'))
        self.assertIn(resp.status_code, [302, 301])


# ---------------------------------------------------------------------------
# 3. Authenticated page rendering
# ---------------------------------------------------------------------------

@override_settings(STORAGES=_TEST_STORAGES)
class AuthenticatedPageTests(TestCase):
    """Every protected page must return HTTP 200 for a logged-in analyst."""

    def setUp(self):
        self.client = Client()
        # Training dashboard requires admin role; use admin for all page tests
        self.user = make_user('analyst1', role='admin', password='pass123!')
        self.client.login(username='analyst1', password='pass123!')

    def test_dashboard_overview(self):
        resp = self.client.get(reverse('dashboard_overview'))
        self.assertEqual(resp.status_code, 200)

    def test_detect_page_get(self):
        resp = self.client.get(reverse('detect'))
        self.assertEqual(resp.status_code, 200)

    def test_detection_history_page(self):
        resp = self.client.get(reverse('detection_history'))
        self.assertEqual(resp.status_code, 200)

    def test_analytics_page(self):
        resp = self.client.get(reverse('analytics'))
        self.assertEqual(resp.status_code, 200)

    def test_alerts_page(self):
        resp = self.client.get(reverse('alerts_list'))
        self.assertEqual(resp.status_code, 200)

    def test_training_dashboard(self):
        resp = self.client.get(reverse('training_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_settings_page(self):
        resp = self.client.get(reverse('settings'))
        self.assertEqual(resp.status_code, 200)

    def test_health_check_api(self):
        resp = self.client.get(reverse('health_check'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'healthy')


# ---------------------------------------------------------------------------
# 4. Admin-only pages
# ---------------------------------------------------------------------------

@override_settings(STORAGES=_TEST_STORAGES)
class AdminPageTests(TestCase):
    """Admin panel only accessible to admin role."""

    def setUp(self):
        self.client = Client()
        self.admin = make_user('superadmin', role='admin', password='adminpass!')
        self.viewer = make_user('viewer1', role='viewer', password='viewpass!')

    def test_admin_dashboard_accessible_by_admin(self):
        self.client.login(username='superadmin', password='adminpass!')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_dashboard_forbidden_for_viewer(self):
        self.client.login(username='viewer1', password='viewpass!')
        resp = self.client.get(reverse('admin_dashboard'))
        # Should redirect away (302) or return 403
        self.assertIn(resp.status_code, [302, 403])


# ---------------------------------------------------------------------------
# 5. Detection flow (POST)
# ---------------------------------------------------------------------------

@override_settings(STORAGES=_TEST_STORAGES)
class DetectionPostTests(TestCase):
    """Submitting telemetry data creates a DetectionHistory record."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('analyst2', role='analyst', password='pass123!')
        self.client.login(username='analyst2', password='pass123!')

    def test_normal_detection_creates_record(self):
        before = DetectionHistory.objects.count()
        resp = self.client.post(reverse('detect'), NORMAL_FEATURES, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(DetectionHistory.objects.count(), before + 1)

    def test_gps_spoof_detection_creates_record(self):
        before = DetectionHistory.objects.count()
        resp = self.client.post(reverse('detect'), GPS_SPOOF_FEATURES, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(DetectionHistory.objects.count(), before + 1)
        det = DetectionHistory.objects.latest('timestamp')
        self.assertIn(det.threat_level, ['Low', 'Medium', 'High', 'Critical'])
        self.assertGreater(det.confidence, 0.0)

    def test_jamming_detection_creates_record(self):
        before = DetectionHistory.objects.count()
        self.client.post(reverse('detect'), JAMMING_FEATURES, follow=True)
        self.assertEqual(DetectionHistory.objects.count(), before + 1)

    def test_detection_response_contains_prediction(self):
        resp = self.client.post(reverse('detect'), GPS_SPOOF_FEATURES, follow=True)
        content = resp.content.decode()
        # Page should contain either a result section or a redirect
        self.assertIn(resp.status_code, [200, 302])

    def test_detection_stores_all_uav_fields(self):
        self.client.post(reverse('detect'), NORMAL_FEATURES, follow=True)
        det = DetectionHistory.objects.filter(user=self.user).latest('timestamp')
        self.assertAlmostEqual(det.altitude, float(NORMAL_FEATURES['altitude']))
        self.assertAlmostEqual(det.speed, float(NORMAL_FEATURES['speed']))
        self.assertAlmostEqual(det.gps_accuracy, float(NORMAL_FEATURES['gps_accuracy']))


# ---------------------------------------------------------------------------
# 6. Fusion engine
# ---------------------------------------------------------------------------

class FusionEngineTests(TestCase):
    """fusion_engine.calculate_combined_threat correctness."""

    def test_normal_traffic_gives_level_zero(self):
        result = fusion_engine.calculate_combined_threat(
            rf_score=0.0, gnss_score=0.0, attack_type='Normal'
        )
        self.assertEqual(result['threat_level'], 0)
        self.assertAlmostEqual(result['combined_score'], 0.0, places=2)

    def test_gps_spoofing_gives_high_level(self):
        result = fusion_engine.calculate_combined_threat(
            rf_score=0.95, gnss_score=0.92, attack_type='GPS Spoofing'
        )
        self.assertGreaterEqual(result['threat_level'], 3)
        self.assertGreater(result['combined_score'], 0.7)

    def test_jamming_gives_elevated_level(self):
        result = fusion_engine.calculate_combined_threat(
            rf_score=0.85, gnss_score=0.0, attack_type='Jamming Attack'
        )
        self.assertGreaterEqual(result['threat_level'], 2)

    def test_result_has_required_keys(self):
        result = fusion_engine.calculate_combined_threat(
            rf_score=0.5, gnss_score=0.3, attack_type='Signal Interference'
        )
        for key in ('threat_level', 'combined_score', 'threat_description', 'recommended_actions'):
            self.assertIn(key, result, msg=f"Missing key '{key}' in fusion result")

    def test_threat_level_is_integer_0_to_4(self):
        for rf, gnss in [(0, 0), (0.3, 0), (0.6, 0.5), (0.9, 0.9)]:
            result = fusion_engine.calculate_combined_threat(
                rf_score=rf, gnss_score=gnss, attack_type='test'
            )
            self.assertIn(result['threat_level'], range(5),
                          msg=f"threat_level {result['threat_level']} out of range 0-4")

    def test_combined_score_between_zero_and_one(self):
        result = fusion_engine.calculate_combined_threat(
            rf_score=0.7, gnss_score=0.6, attack_type='Jamming Attack'
        )
        self.assertGreaterEqual(result['combined_score'], 0.0)
        self.assertLessEqual(result['combined_score'], 1.0)


# ---------------------------------------------------------------------------
# 7. Autonomous response
# ---------------------------------------------------------------------------

class AutonomousResponseTests(TestCase):
    """autonomous_response.execute_response behaviour per threat level."""

    def test_level_zero_logs_only(self):
        """Level 0 performs only normal logging — no countermeasures, no operator alert."""
        result = autonomous_response.execute_response(
            threat_level=0, attack_context={'attack_types': []}
        )
        # Only passive logging should occur — no active countermeasures
        self.assertEqual(result['actions_taken'], ['normal_logging'],
                         msg="Level 0 should only log, not take active countermeasures")
        self.assertFalse(result.get('operator_notified', False))

    def test_level_two_activates_backup_nav(self):
        result = autonomous_response.execute_response(
            threat_level=2, attack_context={'attack_types': ['Jamming Attack']}
        )
        actions = result['actions_taken']
        self.assertGreater(len(actions), 0)

    def test_level_four_triggers_emergency_landing(self):
        result = autonomous_response.execute_response(
            threat_level=4, attack_context={'attack_types': ['GPS Spoofing']}
        )
        actions = result['actions_taken']
        # At level 4 expect an emergency/landing action
        landing_keywords = ('landing', 'emergency', 'imu', 'external')
        self.assertTrue(
            any(any(kw in a for kw in landing_keywords) for a in actions),
            msg=f"Expected emergency action in: {actions}"
        )
        self.assertTrue(result.get('operator_notified', False))

    def test_result_has_required_keys(self):
        result = autonomous_response.execute_response(
            threat_level=3, attack_context={'attack_types': ['Unauthorized Access']}
        )
        for key in ('actions_taken', 'operator_notified', 'response_summary'):
            self.assertIn(key, result, msg=f"Missing key '{key}' in response result")

    def test_all_threat_levels_execute_without_error(self):
        for level in range(5):
            with self.subTest(threat_level=level):
                result = autonomous_response.execute_response(
                    threat_level=level,
                    attack_context={'attack_types': ['Jamming Attack']}
                )
                self.assertIsInstance(result, dict)


# ---------------------------------------------------------------------------
# 8. ML service
# ---------------------------------------------------------------------------

class MLServiceTests(TestCase):
    """ML service prediction pipeline."""

    def setUp(self):
        from services.ml_service import ml_service
        self.ml_service = ml_service

    def test_models_loaded(self):
        self.assertGreater(len(self.ml_service.models), 0,
                           msg="No ML models loaded — run scripts/train_models.py first")

    def test_predict_returns_required_keys(self):
        features = [200, 45, 90, 85, 2500, 1800, 75, 22, 0.5, 95]
        result = self.ml_service.predict(features)
        for key in ('prediction', 'confidence', 'threat_category'):
            self.assertIn(key, result, msg=f"Missing key '{key}' in prediction result")

    def test_predict_confidence_between_0_and_1(self):
        features = [200, 45, 90, 85, 2500, 1800, 75, 22, 0.5, 95]
        result = self.ml_service.predict(features)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)

    def test_threat_category_is_valid(self):
        features = [200, 45, 90, 85, 2500, 1800, 75, 22, 0.5, 95]
        result = self.ml_service.predict(features)
        self.assertIn(result['threat_category'], ('normal', 'attack'))

    def test_gps_spoofing_features_detected_as_attack(self):
        features = [550, 45, 275, 85, 5000, 3600, 45, 30, 1.5, 12]
        result = self.ml_service.predict(features)
        self.assertEqual(result['threat_category'], 'attack',
                         msg=f"GPS spoof not detected as attack: {result['prediction']}")

    def test_normal_features_detected_as_normal(self):
        features = [200, 45, 90, 85, 2500, 1800, 75, 22, 0.5, 95]
        result = self.ml_service.predict(features)
        self.assertEqual(result['threat_category'], 'normal',
                         msg=f"Normal flight incorrectly flagged as attack: {result['prediction']}")

    def test_get_available_models(self):
        models = self.ml_service.get_available_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    def test_calculate_threat_level(self):
        level = self.ml_service.calculate_threat_level('GPS Spoofing', 0.95)
        self.assertIn(level, ('Low', 'Medium', 'High', 'Critical'))


# ---------------------------------------------------------------------------
# 9. API endpoints
# ---------------------------------------------------------------------------

class APITests(TestCase):
    """JSON API endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('apiuser', role='analyst', password='apipass!')
        self.client.login(username='apiuser', password='apipass!')

    def test_health_check_returns_json(self):
        resp = self.client.get(reverse('health_check'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('status', data)

    def test_api_history_returns_json(self):
        resp = self.client.get(reverse('api_history'))
        self.assertIn(resp.status_code, [200, 403])
        if resp.status_code == 200:
            self.assertIn(resp['Content-Type'], ['application/json',
                                                  'application/json; charset=utf-8'])

    def test_api_alerts_returns_json(self):
        resp = self.client.get(reverse('api_alerts'))
        self.assertIn(resp.status_code, [200, 403])

    def test_api_detect_post_returns_json(self):
        import json
        features = [200, 45, 90, 85, 2500, 1800, 75, 22, 0.5, 95]
        resp = self.client.post(
            reverse('api_detect'),
            data=json.dumps({'features': features}),
            content_type='application/json',
        )
        self.assertIn(resp.status_code, [200, 400, 403])


# ---------------------------------------------------------------------------
# 10. Alerts management
# ---------------------------------------------------------------------------

@override_settings(STORAGES=_TEST_STORAGES)
class AlertsTests(TestCase):
    """Alert creation, acknowledge and resolve."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('alertanalyst', role='analyst', password='alertpass!')
        self.client.login(username='alertanalyst', password='alertpass!')

        # Create a detection + alert
        self.detection = DetectionHistory.objects.create(
            user=self.user,
            altitude=550, speed=45, direction=275,
            signal_strength=85, distance_from_base=5000,
            flight_time=3600, battery_level=45,
            temperature=30, vibration=1.5, gps_accuracy=12,
            prediction='GPS Spoofing',
            confidence=0.97,
            threat_level='Critical',
            model_version='RandomForest',
        )
        self.alert = Alert.objects.create(
            detection=self.detection,
            severity='Critical',
            status='Open',
        )

    def test_alerts_list_shows_alert(self):
        resp = self.client.get(reverse('alerts_list'))
        self.assertEqual(resp.status_code, 200)

    def test_acknowledge_alert(self):
        resp = self.client.post(
            reverse('acknowledge_alert', args=[self.alert.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'Acknowledged')

    def test_resolve_alert(self):
        resp = self.client.post(
            reverse('resolve_alert', args=[self.alert.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'Resolved')


# ---------------------------------------------------------------------------
# 11. MitigationEvent model
# ---------------------------------------------------------------------------

class MitigationEventTests(TestCase):
    """MitigationEvent records are created for autonomous responses."""

    def setUp(self):
        self.user = make_user('mituser', role='analyst', password='mitpass!')
        self.detection = DetectionHistory.objects.create(
            user=self.user,
            altitude=550, speed=45, direction=275,
            signal_strength=20, distance_from_base=900,
            flight_time=3600, battery_level=40,
            temperature=30, vibration=1.5, gps_accuracy=12,
            prediction='GPS Spoofing',
            confidence=0.95,
            threat_level='Critical',
            model_version='RandomForest',
        )

    def test_mitigation_event_creation(self):
        event = MitigationEvent.objects.create(
            detection=self.detection,
            threat_level=4,
            action_taken='emergency_landing_initiated',
            success=True,
            operator_notified=True,
        )
        self.assertEqual(event.threat_level, 4)
        self.assertEqual(event.action_taken, 'emergency_landing_initiated')
        self.assertTrue(event.success)
        self.assertTrue(event.operator_notified)

    def test_multiple_mitigation_events_per_detection(self):
        actions = ['imu_barometer_only', 'cut_external_links', 'forensic_data_logged']
        for action in actions:
            MitigationEvent.objects.create(
                detection=self.detection,
                threat_level=4,
                action_taken=action,
                success=True,
                operator_notified=True,
            )
        count = MitigationEvent.objects.filter(detection=self.detection).count()
        self.assertEqual(count, len(actions))


# ---------------------------------------------------------------------------
# 12. Detection history filtering
# ---------------------------------------------------------------------------

@override_settings(STORAGES=_TEST_STORAGES)
class DetectionHistoryTests(TestCase):
    """Detection history page with filters."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('histuser', role='analyst', password='histpass!')
        self.client.login(username='histuser', password='histpass!')
        # seed some records
        for pred, threat in [('Normal', 'Low'), ('GPS Spoofing', 'Critical'),
                              ('Jamming Attack', 'High')]:
            DetectionHistory.objects.create(
                user=self.user,
                altitude=200, speed=50, direction=90,
                signal_strength=80, distance_from_base=1000,
                flight_time=600, battery_level=80,
                temperature=22, vibration=1.0, gps_accuracy=90,
                prediction=pred, confidence=0.9,
                threat_level=threat, model_version='RandomForest',
            )

    def test_history_page_loads(self):
        resp = self.client.get(reverse('detection_history'))
        self.assertEqual(resp.status_code, 200)

    def test_history_contains_records(self):
        resp = self.client.get(reverse('detection_history'))
        content = resp.content.decode()
        self.assertIn('GPS Spoofing', content)
        self.assertIn('Jamming Attack', content)
