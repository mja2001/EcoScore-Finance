from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from config.database import DatabaseConfig
from models.loan import Loan
import tensorflow as tf
import numpy as np
from hedera import (
    AccountId,
    PrivateKey,
    Client,
    ContractExecuteTransaction,
    ContractFunctionParams,
)

# Load environment variables (from env.txt renamed to .env)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Hedera SDK Setup
network = os.getenv('HEDERA_NETWORK', 'testnet')
account_id = AccountId.fromString(os.getenv('HEDERA_ACCOUNT_ID'))
private_key = PrivateKey.fromString(os.getenv('HEDERA_PRIVATE_KEY'))
ECO_CONTRACT_ID = AccountId.fromString(os.getenv('ECO_CONTRACT_ID'))  # From deployment

client = Client.forName(network)
client.setOperator(account_id, private_key)

# Load ML Model (LSTM from Day 2)
model = tf.keras.models.load_model(os.getenv('MODEL_PATH'))

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
        loan = Loan.get_by_id(loan_id)
        
        if not loan:
            return jsonify({'error': 'Loan not found'}), 404
        
        # Prepare features for ML (customize based on model inputs; e.g., sequence for LSTM)
        # Example: 12-month projection from loan data
        features = [loan['loan_amount'], loan['predicted_carbon_reduction'] or 0,  # Add more
                    1 if loan['project_type'] == 'solar' else 0, ...]  # Encode categoricals
        seq_data = np.array([features] * 12).reshape(1, 12, len(features))
        eco_score = model.predict(seq_data)[0][0] * 100  # Assume regression output, scale to 0-100
        predicted_carbon_reduction = ...  # Compute or from model
        
        success = Loan.update_score(loan_id, eco_score, predicted_carbon_reduction)
        
        if not success:
            return jsonify({'error': 'Failed to update score'}), 500

        certified = False
        tx_id = None
        if eco_score > 80:
            try:
                borrower_addr = loan['borrower_address'] or '0x0000000000000000000000000000000000000000'
                params = ContractFunctionParams()
                params.addUInt256(int(loan_id))
                params.addUInt256(int(eco_score))
                params.addAddress(borrower_addr)
                
                tx = ContractExecuteTransaction().setContractId(ECO_CONTRACT_ID).setGas(200000).setFunction("certifyLoan", params)
                resp = tx.execute(client)
                receipt = resp.getReceipt(client)
                tx_id = resp.transactionId.toString()
                certified = True
                socketio.emit('loan_certified', {'loan_id': loan_id, 'eco_score': eco_score, 'tx_id': tx_id})
            except Exception as e:
                print(f"Blockchain certification failed: {e}")

        return jsonify({
            'loan_id': loan_id,
            'eco_score': eco_score,
            'predicted_carbon_reduction': predicted_carbon_reduction,
            'certified': certified,
            'tx_id': tx_id,
            'message': 'Score calculated successfully'
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
