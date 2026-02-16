"""
Global error handling middleware.
"""

from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Not found',
            'message': 'The requested endpoint does not exist'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle wrong HTTP method"""
        return jsonify({
            'error': 'Method not allowed',
            'message': 'This endpoint does not support this HTTP method'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors"""
        logger.error(f"Internal error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500