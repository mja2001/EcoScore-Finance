from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from config.database import DatabaseConfig
from models.loan import Loan

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database tables
print("Initializing database...")
DatabaseConfig.init_postgres_tables()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'EcoScore Finance Backend',
        'version': '1.0.0'
    }), 200

# Loan endpoints
@app.route('/api/loans', methods=['POST'])
def create_loan():
    """Create a new loan application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['loan_id', 'borrower_name', 'loan_amount', 
                          'project_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create loan
        loan_id = Loan.create(data)
        
        if loan_id:
            return jsonify({
                'message': 'Loan created successfully',
                'loan_id': data['loan_id']
            }), 201
        else:
            return jsonify({
                'error': 'Failed to create loan'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    """Get all loans"""
    try:
        loans = Loan.get_all()
        return jsonify({
            'loans': loans,
            'count': len(loans)
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/loans/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Get specific loan by ID"""
    try:
        loan = Loan.get_by_id(loan_id)
        
        if loan:
            return jsonify(loan), 200
        else:
            return jsonify({
                'error': 'Loan not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/loans/<loan_id>/score', methods=['POST'])
def calculate_score(loan_id):
    """Calculate environmental score for a loan"""
    try:
        # Get loan data
        loan = Loan.get_by_id(loan_id)
        
        if not loan:
            return jsonify({
                'error': 'Loan not found'
            }), 404
        
        # TODO: Call ML model for prediction (we'll implement this in Day 2)
        # For now, return mock score
        eco_score = 75.5
        predicted_carbon_reduction = 1250.0
        
        # Update loan with score
        success = Loan.update_score(loan_id, eco_score, predicted_carbon_reduction)
        
        if success:
            return jsonify({
                'loan_id': loan_id,
                'eco_score': eco_score,
                'predicted_carbon_reduction': predicted_carbon_reduction,
                'message': 'Score calculated successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to update score'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"🚀 EcoScore Finance Backend starting on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
