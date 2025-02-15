# Installation Guide

## System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **Python**: 3.8 or higher

## Installation Steps

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Johk3/AIR.git
cd AIR
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -e .[dev]
```
Alternatively:
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Copy the `.env.example` file and edit it:
```bash
cp .env.example .env
```

### 5️⃣ Run the Application
```bash
python main.py
```
For troubleshooting, see [User Guide](user-guide.md).
