import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class EcoScoreLSTM(nn.Module):
    def __init__(self, input_size=5, hidden_size=50, num_layers=2, output_size=1):
        super(EcoScoreLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])  # Take the last time step's output
        return out

# Function to train the model (use synthetic data for hackathon demo)
def train_model():
    # Synthetic data: 100 samples, 12 "months" sequence, 5 features (e.g., energy_use, carbon_est, loan_amt, duration, green_factor)
    X = np.random.rand(100, 12, 5) * 100  # Random features
    y = np.mean(X, axis=(1,2)) * 0.5 + np.random.rand(100) * 10  # Simulated EcoScore (0-100)
    
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X.reshape(-1, 5)).reshape(100, 12, 5)
    
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y.reshape(-1, 1), dtype=torch.float32)
    
    model = EcoScoreLSTM()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(100):  # Train for 100 epochs
        model.train()
        optimizer.zero_grad()
        output = model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item()}")
    
    torch.save(model.state_dict(), 'ecoscore_model.pth')
    return model, scaler

# Function to predict EcoScore
def predict_ecoscore(model, scaler, input_data):
    # input_data: list of sequences, e.g., [[energy_use_month1, carbon_est1, ...], ...] for 12 months
    input_array = np.array(input_data).reshape(1, len(input_data), -1)
    input_scaled = scaler.transform(input_array.reshape(-1, input_array.shape[2])).reshape(input_array.shape)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        score = model(input_tensor).item()
    return min(max(score, 0), 100)  # Clamp to 0-100

# If using TensorFlow/Keras instead (as mentioned in README):
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense
# model = Sequential()
# model.add(LSTM(50, return_sequences=True, input_shape=(12, 5)))
# model.add(LSTM(50))
# model.add(Dense(1))
# model.compile(optimizer='adam', loss='mse')
# # Train similarly with model.fit(X, y, epochs=100)
# model.save('ecoscore_model.h5')
