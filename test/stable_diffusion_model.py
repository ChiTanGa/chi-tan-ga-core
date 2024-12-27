import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Hyperparameters
seq_length = 5  # 5 seconds of past data (each second one datapoint)
time_steps = 10  # Number of diffusion steps
epochs = 10
batch_size = 64
learning_rate = 0.001
noise_std = 0.1  # Amount of noise to add


# Create a synthetic dataset (replace this with real stock data)
def generate_synthetic_data(num_samples=10000):
    X = np.random.randn(num_samples, seq_length)  # Random stock price changes
    Y = np.array([1 if x[-1] > x[0] else 0 for x in X])  # 1 if final price is greater than initial price
    return X, Y


# Dataset class
class StockDataset(torch.utils.data.Dataset):
    def __init__(self, X, Y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.Y = torch.tensor(Y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]


# Define a simple neural network model for prediction
class DiffusionStockPredictor(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(DiffusionStockPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)  # Binary output (up or down)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))  # Sigmoid for binary classification
        return x


# Diffusion process (forward: add noise, reverse: remove noise)
def add_noise(data, timesteps, noise_std):
    noise = torch.randn_like(data) * noise_std
    return data + noise / timesteps  # Add a fraction of the noise over time


def remove_noise(noisy_data, model):
    # Inference step: pass the noisy data through the model
    return model(noisy_data)


# Training loop
def train(model, dataloader, criterion, optimizer, timesteps, noise_std):
    model.train()
    for epoch in range(epochs):
        for batch_X, batch_Y in dataloader:
            # Add noise to the data
            noisy_X = add_noise(batch_X, timesteps, noise_std)

            # Forward pass: predict based on noisy data
            output = remove_noise(noisy_X, model)
            loss = criterion(output.squeeze(), batch_Y)

            # Backpropagation and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}")


# Evaluation
def evaluate(model, dataloader):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch_X, batch_Y in dataloader:
            output = model(batch_X).squeeze()
            predicted = (output > 0.5).float()  # Threshold at 0.5 for binary classification
            total += batch_Y.size(0)
            correct += (predicted == batch_Y).sum().item()

    accuracy = correct / total
    print(f"Accuracy: {accuracy:.4f}")


# Prepare dataset
X, Y = generate_synthetic_data()
dataset = StockDataset(X, Y)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Initialize model, loss, and optimizer
model = DiffusionStockPredictor(input_size=seq_length, hidden_size=128)
criterion = nn.BCELoss()  # Binary cross-entropy loss
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Train the model
train(model, dataloader, criterion, optimizer, time_steps, noise_std)

# Evaluate the model
evaluate(model, dataloader)
