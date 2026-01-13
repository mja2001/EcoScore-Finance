from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from models import db, Loan
from ml_model import EcoScoreLSTM, predict_ecoscore, train_model  # Or load pre-trained

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/ecoscore_db'
db.init_app(app)
socketio = SocketIO(app)

# Load or train model (do this once on startup)
model, scaler = train_model()  # Or load: model = EcoScoreLSTM(); model.load_state_dict(torch.load('ecoscore_model.pth'))

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.json
    # Extract features; generate dummy sequence for prediction (customize based on real logic)
    seq_data = [[data['energy_usage_est'], data['carbon_est'], data['amount'], data['duration'], 1 if data['project_type'] == 'green' else 0]] * 12  # Repeat for 12 months; refine with projections
    eco_score = predict_ecoscore(model, scaler, seq_data)
    
    loan = Loan(amount=data['amount'], duration=data['duration'], project_type=data['project_type'],
                location=data['location'], energy_usage_est=data['energy_usage_est'], carbon_est=data['carbon_est'],
                eco_score=eco_score)
    db.session.add(loan)
    db.session.commit()
    
    # Broadcast real-time update via WebSocket
    socketio.emit('loan_updated', {'id': loan.id, 'eco_score': eco_score})
    
    return jsonify({'id': loan.id, 'eco_score': eco_score}), 201

# Other CRUD routes (GET, PUT, DELETE) similar; add score update in PUT if inputs change

# WebSocket example for real-time (e.g., IoT updates triggering re-score)
@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected to EcoScore real-time updates'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
