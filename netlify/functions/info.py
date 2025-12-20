"""
Netlify Function: Get Project Info
Returns information about the UAV Security ML project.
"""
import json

def handler(event, context):
    """
    Get project information.
    
    Returns:
        dict: Response with project details
    """
    project_info = {
        'name': 'UAV Security ML',
        'description': 'Advanced Machine Learning for UAV Threat Detection',
        'version': '2.0.0',
        'features': [
            'Real-time threat detection',
            'Interactive analytics dashboard',
            'ML model training and comparison',
            'Smart alert system',
            'User management and authentication',
            'Performance metrics and reporting'
        ],
        'tech_stack': {
            'backend': ['Flask', 'SQLAlchemy', 'Flask-SocketIO'],
            'ml_libraries': ['scikit-learn', 'XGBoost', 'SHAP', 'pandas', 'numpy'],
            'database': ['PostgreSQL', 'SQLite'],
            'caching': ['Redis'],
            'security': ['Flask-Login', 'Flask-JWT-Extended', 'Flask-Bcrypt']
        },
        'deployment_options': [
            'Render (Recommended)',
            'Railway',
            'Heroku',
            'Docker',
            'AWS/GCP/Azure'
        ],
        'repository': 'https://github.com/shivansh-12315646/uav_security_ml',
        'documentation': 'See README.md and DEPLOYMENT.md in repository'
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': json.dumps(project_info, indent=2)
    }
