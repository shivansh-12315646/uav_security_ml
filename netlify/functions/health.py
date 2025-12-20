"""
Netlify Function: Health Check
A simple serverless function to demonstrate Netlify Functions integration.
"""
import json

def handler(event, context):
    """
    Health check endpoint for Netlify deployment.
    
    Returns:
        dict: Response with status code and body
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'UAV Security ML - Netlify Static Site',
            'message': 'This is the static landing page. For full backend functionality, deploy the Flask app to Render/Railway.',
            'version': '1.0.0',
            'deployment': 'netlify-static'
        })
    }
