# %%
import os
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
import time

# %%
# Define the dataset class


class NumberDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_name = os.path.join(self.img_dir, self.data.iloc[idx, 0])
        image = Image.open(img_name).convert('L')  # Convert to grayscale
        label = self.data.iloc[idx, 1]

        if self.transform:
            image = self.transform(image)

        # Convert label to tensor of individual digits
        label = torch.tensor([int(d)
                             for d in str(label).zfill(6)], dtype=torch.long)

        return image, label

# %%
# Define the larger CNN model


class LargerNumberCNN(nn.Module):
    def __init__(self):
        super(LargerNumberCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(256 * 13 * 4, 512)
        # 10 classes for each of the 6 digits
        self.fc2 = nn.Linear(512, 10 * 6)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(-1, 256 * 13 * 4)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x.view(-1, 6, 10)  # Reshape to (batch_size, 6, 10)

# %%


# Set up data transformations
transform = transforms.Compose([
    transforms.Resize((104, 32)),
    transforms.ToTensor(),
])

# Create dataset
dataset = NumberDataset(csv_file=os.path.join('generate_data', 'images', 'data.csv'),
                        img_dir=os.path.join('generate_data', 'images'), transform=transform)

# Split dataset into train and test sets
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

# Create dataloaders
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# %%
# Initialize the model, loss function, and optimizer
model = LargerNumberCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training and evaluation loop
num_epochs = 500
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
model.to(device)

# %%

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)

        # 計算組合損失
        loss = 0
        for i in range(6):
            digit_loss = criterion(outputs[:, i, :], labels[:, i])
            loss += digit_loss

        # 添加正則化項
        l2_lambda = 0.001
        l2_reg = torch.tensor(0.).to(device)
        for param in model.parameters():
            l2_reg += torch.norm(param)
        loss += l2_lambda * l2_reg

        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    # Evaluation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 2)
            total += labels.size(0) * labels.size(1)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {running_loss/len(train_loader):.4f}, Test Accuracy: {accuracy:.2f}%")

print("Training completed!")

# %%

# Save the trained model
torch.save(model.state_dict(), os.path.join(
    "model", f"larger_model_{time.time()}.pth"))
print(f"Model saved as 'larger_model_{time.time()}.pth'")
