from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import json
import threading
import paho.mqtt.client as mqtt
import tensorflow as tf
import numpy as np
from config.database import DatabaseConfig
from models.loan import Loan
from hedera import (
    AccountId,
    PrivateKey,
    Client,
    ContractExecuteTransaction,
    ContractFunctionParams,
)

# Load environment variables
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
ECO_CONTRACT_ID = AccountId.fromString(os.getenv('ECO_CONTRACT_ID'))

client = Client.forName(network)
client.setOperator(account_id, private_key)

# Load ML Model
model = tf.keras.models.load_model(os.getenv('MODEL_PATH'))

# --- MQTT Setup & Threading ---

def on_message(client_mqtt, userdata, msg):
    """Handle incoming IoT data updates via MQTT"""
    try:
        data = json.loads(msg.payload)
        loan_id = data.get('loan_id')
        new_carbon_val = data.get('predicted_carbon_reduction', 0)
        
        loan = Loan.get_by_id(loan_id)
        if loan:
            # Prepare features for ML re-prediction
            # Using current loan amount and new carbon data from IoT
            features = [loan['loan_amount'], new_carbon_val, 
                        1 if loan['project_type'] == 'solar' else 0]
            # Reshape for LSTM (1 sample, 12 time steps, N features)
            seq_data = np.array([features] * 12).reshape(1, 12, len(features))
            
            # Re-calculate score
            eco_score = float(model.predict(seq_data)[0][0] * 100)
            
            # Update Database
            Loan.update_score(loan_id, eco_score, new_carbon_val)
            
            # Real-time Blockchain Certification if score crosses threshold
            tx_id = None
            if eco_score > 80:
                try:
                    borrower_addr = loan.get('borrower_address') or '0x0000000000000000000000000000000000000000'
                    params = ContractFunctionParams()
                    params.addUInt256(int(loan_id))
                    params.addUInt256(int(eco_score))
                    params.addAddress(borrower_addr)
                    
                    tx = ContractExecuteTransaction().setContractId(ECO_CONTRACT_ID).setGas(200000).setFunction("certifyLoan", params)
                    resp = tx.execute(client)
                    tx_id = resp.transactionId.toString()
                    
                    socketio.emit('loan_certified', {'loan_id': loan_id, 'eco_score': eco_score, 'tx_id': tx_id})
                except Exception as b_err:
                    print(f"Blockchain auto-certification failed: {b_err}")

            # Notify frontend of IoT update
            socketio.emit('iot_update', {
                'loan_id': loan_id, 
                'eco_score': eco_score, 
                'carbon_reduction': new_carbon_val,
                'tx_id': tx_id
            })
            print(f"✅ IoT Update processed for Loan {loan_id}: New Score {eco_score:.2f}")

    except Exception as e:
        print(f"Error in MQTT callback: {e}")

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(os.getenv('MQTT_BROKER', 'localhost'), int(os.getenv('MQTT_PORT', 1883)))
    mqtt_client.subscribe('ecoscore/iot/updates')
    # Start MQTT loop in a background thread to prevent blocking Flask
    mqtt_thread = threading.Thread(target=mqtt_client.loop_forever, daemon=True)
    mqtt_thread.start()
    print("📡 MQTT Thread started and subscribed to ecoscore/iot/updates")
except Exception as e:
    print(f"❌ Failed to connect to MQTT Broker: {e}")

# --- End MQTT Setup ---

# Initialize database tables
print("Initializing database...")
DatabaseConfig.init_postgres_tables()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'EcoScore Finance Backend',
        'mqtt_active': mqtt_thread.is_alive(),
        'version': '1.0.0'
    }), 200

@app.route('/api/loans', methods=['POST'])
def create_loan():
    try:
        data = request.get_json()
        required_fields = ['loan_id', 'borrower_name', 'loan_amount', 'project_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        loan_id = Loan.create(data)
        if loan_id:
            return jsonify({'message': 'Loan created successfully', 'loan_id': data['loan_id']}), 201
        return jsonify({'error': 'Failed to create loan'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    try:
        loans = Loan.get_all()
        return jsonify({'loans': loans, 'count': len(loans)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/loans/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    try:
        loan = Loan.get_by_id(loan_id)
        if loan:
            return jsonify(loan), 200
        return jsonify({'error': 'Loan not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/loans/<loan_id>/score', methods=['POST'])
def calculate_score(loan_id):
    """Manually trigger calculation for a loan"""
    try:
        loan = Loan.get_by_id(loan_id)
        if not loan:
            return jsonify({'error': 'Loan not found'}), 404
        
        # Prepare features for ML
        carbon_val = loan.get('predicted_carbon_reduction') or 0
        features = [loan['loan_amount'], carbon_val, 1 if loan['project_type'] == 'solar' else 0]
        seq_data = np.array([features] * 12).reshape(1, 12, len(features))
        
        eco_score = float(model.predict(seq_data)[0][0] * 100)
        
        success = Loan.update_score(loan_id, eco_score, carbon_val)
        if not success:
            return jsonify({'error': 'Failed to update score'}), 500

        certified = False
        tx_id = None
        if eco_score > 80:
            try:
                borrower_addr = loan.get('borrower_address') or '0x0000000000000000000000000000000000000000'
                params = ContractFunctionParams()
                params.addUInt256(int(loan_id))
                params.addUInt256(int(eco_score))
                params.addAddress(borrower_addr)
                
                tx = ContractExecuteTransaction().setContractId(ECO_CONTRACT_ID).setGas(200000).setFunction("certifyLoan", params)
                resp = tx.execute(client)
                tx_id = resp.transactionId.toString()
                certified = True
                socketio.emit('loan_certified', {'loan_id': loan_id, 'eco_score': eco_score, 'tx_id': tx_id})
            except Exception as e:
                print(f"Blockchain certification failed: {e}")

        return jsonify({
            'loan_id': loan_id,
            'eco_score': eco_score,
            'certified': certified,
            'tx_id': tx_id,
            'message': 'Score calculated successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"🚀 EcoScore Finance Backend starting on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
