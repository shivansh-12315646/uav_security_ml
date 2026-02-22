from django.urls import path
from django.views.generic import RedirectView
from core.views.auth import login_view, register_view, logout_view
from core.views.main import index, dashboard, dashboard_overview, algorithms
from core.views.detection import detect, history, batch_detect
from core.views.analytics import analytics, detection_timeline
from core.views.alerts import alerts_list, acknowledge_alert, resolve_alert
from core.views.admin_views import admin_dashboard, users_list, toggle_user_active
from core.views.api import api_detect, api_history, api_alerts, health_check
from core.views.settings_views import settings_view
from core.views.training import (
    training_dashboard, upload_dataset, start_training, list_models,
    activate_model, delete_model, compare_models_page, dataset_analyzer
)

urlpatterns = [
    # Root
    path('', RedirectView.as_view(pattern_name='dashboard_overview'), name='index'),

    # Auth
    path('auth/login/', login_view, name='auth_login'),
    path('auth/register/', register_view, name='auth_register'),
    path('auth/logout/', logout_view, name='auth_logout'),

    # Dashboard
    path('dashboard/', RedirectView.as_view(pattern_name='dashboard_overview'), name='dashboard'),
    path('dashboard/overview/', dashboard_overview, name='dashboard_overview'),
    path('algorithms/', algorithms, name='algorithms'),

    # Detection
    path('detection/detect/', detect, name='detect'),
    path('detection/history/', history, name='detection_history'),
    path('detection/batch/', batch_detect, name='batch_detect'),

    # Analytics
    path('analytics/', analytics, name='analytics'),
    path('analytics/api/detection-timeline/', detection_timeline, name='detection_timeline'),

    # Alerts
    path('alerts/', alerts_list, name='alerts_list'),
    path('alerts/<int:alert_id>/acknowledge/', acknowledge_alert, name='acknowledge_alert'),
    path('alerts/<int:alert_id>/resolve/', resolve_alert, name='resolve_alert'),

    # Admin panel
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', users_list, name='admin_users'),
    path('admin-panel/users/<int:user_id>/toggle-active/', toggle_user_active, name='toggle_user_active'),

    # Settings
    path('settings/', settings_view, name='settings'),

    # Training
    path('training/dashboard/', training_dashboard, name='training_dashboard'),
    path('training/upload-dataset/', upload_dataset, name='upload_dataset'),
    path('training/start-training/', start_training, name='start_training'),
    path('training/models/', list_models, name='list_models'),
    path('training/models/<int:model_id>/activate/', activate_model, name='activate_model'),
    path('training/models/<int:model_id>/', delete_model, name='delete_model'),
    path('training/compare/', compare_models_page, name='compare_models_page'),
    path('training/dataset-analyzer/', dataset_analyzer, name='dataset_analyzer'),

    # API
    path('api/v1/detect/', api_detect, name='api_detect'),
    path('api/v1/history/', api_history, name='api_history'),
    path('api/v1/alerts/', api_alerts, name='api_alerts'),
    path('api/v1/health/', health_check, name='health_check'),
]
