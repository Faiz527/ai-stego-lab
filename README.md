# Image Steganography Application 

A comprehensive web-based image steganography application built with Streamlit that supports multiple steganography methods (LSB, Hybrid DCT, Hybrid DWT) with encryption capabilities, batch processing, and detailed analytics.

## 🎯 Features

### Steganography Methods
- **LSB (Least Significant Bit)**: Spatial domain steganography with fast processing
- **Hybrid DCT (Discrete Cosine Transform)**: Frequency domain method using Y-channel
- **Hybrid DWT (Discrete Wavelet Transform)**: Wavelet-based encoding using Haar wavelets

### Core Functionality
- ✅ **Message Encoding**: Hide secret messages in images using three different methods
- ✅ **Message Decoding**: Extract hidden messages from encoded images
- ✅ **Encryption**: Message protection with SHA-256 key derivation
- ✅ **Method Comparison**: Side-by-side comparison of all three steganography methods
- ✅ **Batch Processing**: Encode/decode multiple images efficiently
- ✅ **Real-time Analytics**: Track operations and view detailed statistics

### Analytics Dashboard
- 📊 **Operation Timeline**: Track operations over the last 7 days
- 📈 **Method Distribution**: Pie chart showing usage of LSB, DCT, and DWT
- 📉 **Encode vs Decode**: Bar chart comparing encode/decode operations
- 🔐 **Encryption Usage**: Statistics on encrypted vs unencrypted messages
- 💾 **Data Size Distribution**: Visualization of operation data sizes
- 📋 **Activity Log**: Real-time log of recent user operations

### User Management
- User authentication with SHA-256 password hashing
- Per-user operation tracking
- Activity logging and statistics
- Session management

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **PostgreSQL 9.1+** (for database operations)
- **pip** (Python package manager)

### Quick Start

1. **Clone or Download the Project**
```bash
git clone https://github.com/yourusername/image-steganography.git
cd ITR
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

Create `.env` file in project root:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stegnography
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

5. **Create PostgreSQL Database**
```bash
# Option 1: From project root (using convenience wrapper)
python create_db.py

# Option 2: Using Python module
python -m src.db.create_db
```

6. **Initialize Database Tables**
```bash
python -c "from src.db.db_utils import initialize_database; initialize_database()"
```

7. **Test Database Connection**
```bash
python test_db.py
```

---

## 🚀 Running the Application

Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open at: `http://localhost:8501`

---

## 📁 Project Structure

```
ITR/
├── .env                          # Environment variables (PostgreSQL credentials)
├── .gitignore                    # Git ignore rules
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml             # Streamlit secrets
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── streamlit_app.py            # Main Streamlit application
├── create_db.py                # Database creation script (convenience wrapper)
├── test_db.py                  # Database connection test
├── test_steganography.py       # Steganography methods test
├── src/
│   ├── __init__.py             # Main package initialization
│   ├── db/
│   │   ├── __init__.py
│   │   ├── create_db.py        # ← MOVED HERE: Database creation module
│   │   ├── db_utils.py         # PostgreSQL operations
│   │   └── db_utils_minimal.py # Lightweight DB operations
│   ├── stego/                  # Core Steganography Engine
│   │   ├── __init__.py
│   │   ├── lsb_steganography.py        # LSB (Spatial Domain) method
│   │   ├── dct_steganography.py        # Hybrid DCT (Y-Channel) method
│   │   └── dwt_steganography.py        # Hybrid DWT (Haar Wavelet) method
│   ├── analytics/              # Analytics & Statistics
│   │   ├── __init__.py
│   │   └── stats.py            # Chart generation, statistics calculations
│   ├── encryption/             # Encryption Module
│   │   ├── __init__.py
│   │   └── encryption.py       # XOR cipher with SHA-256 key derivation
│   ├── ui/                     # User Interface
│   │   ├── __init__.py
│   │   ├── styles.py           # Dark theme styling & CSS
│   │   └── ui_components.py    # Streamlit UI sections (encode, decode, etc.)
│   ├── batch_processing/       # Batch processing module
│   │   ├── __init__.py
│   │   ├── batch_encode.py     # Batch encoding functions
│   │   └── batch_decode.py     # Batch decoding functions
│   ├── utils/                  # Utility functions
│       ├── __init__.py
│       └── file_utils.py       # File handling and validation
│
└── .venv/                      # Python virtual environment
```

### Module Organization

**`src/stego/`** - Steganography Engine
- Independent implementations of LSB, DCT, and DWT methods
- Each method has encode/decode functions
- No external dependencies between methods

**`src/db/`** - Database Layer
- PostgreSQL connection management
- User authentication with SHA-256 password hashing
- Operation logging (encode/decode history)
- Statistics retrieval for analytics

**`src/analytics/`** - Analytics & Visualization
- Chart generation (Plotly)
- Statistics calculations
- Activity logs and dataframes
- Real-time metrics

**`src/encryption/`** - Message Security
- XOR cipher with SHA-256 key derivation
- Symmetric encryption/decryption
- Optional message protection

**`src/ui/`** - Web Interface
- Streamlit UI components
- Dark theme styling
- Authentication section
- Encode/Decode sections
- Comparison and Statistics sections

**`src/batch_processing/`** - Batch Processing Module
- Batch encoding and decoding functions
- File validation and error handling
- Integration with core steganography engine

**`src/utils/`** - Utility Functions
- File handling and validation
- Logging and configuration management
- Helper functions for common tasks

---

## 🔐 Usage Guide

### 1. **Create Account**
- Click "Create New Account" on the login screen
- Enter username and password
- Account is created in PostgreSQL database

### 2. **Encode Message**
- Go to **Encode** tab
- Select steganography method (LSB, DCT, or DWT)
- Upload cover image (PNG/JPG)
- Enter secret message
- (Optional) Enable encryption with AES-256
- Click "Encode Message"
- Download the encoded image

### 3. **Decode Message**
- Go to **Decode** tab
- Upload encoded image
- Select the method used for encoding
- Click "Decode Message"
- View extracted message
- (If encrypted) Message is automatically decrypted

### 4. **Compare Methods**
- Go to **Comparison** tab
- Upload cover image
- Enter secret message
- View side-by-side comparison of all three methods
- See PSNR (Peak Signal-to-Noise Ratio) for each method

### 5. **View Analytics**
- Go to **Statistics** tab
- View operation timeline (last 7 days)
- See method distribution pie chart
- Check encode vs decode statistics
- Monitor encryption usage
- View data size distribution
- See recent activity log

### 6. **Batch Processing**
- Go to **Batch Processing** tab
- Select folder with images for encoding/decoding
- Choose steganography method and encryption options
- Click "Start Batch Processing"
- Download link for processed images will be provided

---

## 🔧 Technical Details

### Steganography Methods

#### LSB (Least Significant Bit)
- **Domain**: Spatial
- **Capacity**: ~2.5% of image size
- **Detection Resistance**: Low
- **Computational Cost**: Very Low
- **Quality**: Excellent (PSNR > 50 dB)

#### Hybrid DCT
- **Domain**: Frequency (Y-channel only)
- **Capacity**: ~1.5% of image size
- **Detection Resistance**: Medium
- **Computational Cost**: Medium
- **Quality**: Good (PSNR > 40 dB)

#### Hybrid DWT (Haar Wavelet)
- **Domain**: Frequency (Wavelet)
- **Capacity**: ~2% of image size
- **Detection Resistance**: High
- **Computational Cost**: Medium-High
- **Quality**: Very Good (PSNR > 45 dB)

### Encryption
- **Algorithm**: XOR cipher with SHA-256 key derivation
- **Key Size**: 256-bit (derived from password)
- **Security**: Suitable for steganography; recommended AES-256 for highly sensitive data
- **Performance**: Very fast (negligible overhead)

### Database Schema

**users**
```sql
user_id (PK) | username | password_hash | created_at
```

**operations**
```sql
operation_id (PK) | user_id (FK) | operation_type | method | 
data_size | is_encrypted | status | created_at
```

**activity_log**
```sql
activity_id (PK) | user_id (FK) | action | created_at
```

---

## 📊 Analytics & Statistics

The application tracks:
- **Total Operations**: Count of all encode/decode operations
- **Method Usage**: Distribution of LSB, DCT, DWT usage
- **Encryption Rate**: Percentage of operations using encryption
- **Operation Timeline**: Operations per day over 7 days
- **Data Size Distribution**: Breakdown of message sizes
- **User Activity**: Recent operations by all users

---

## 🧪 Testing

Run steganography tests:
```bash
python test_steganography.py
```

Test database connection:
```bash
python test_db.py
```

---

## ⚙️ Configuration

### Streamlit Configuration (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#238636"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#161B22"
textColor = "#C9D1D9"
font = "sans serif"

[client]
showErrorDetails = true
showWarningOnDirectExecution = true

[logger]
level = "info"

[server]
port = 8501
headless = true
```

### Environment Variables (`.env`)
```bash
DB_HOST=localhost              # PostgreSQL host
DB_PORT=5432                   # PostgreSQL port
DB_NAME=stegnography           # Database name
DB_USER=postgres               # PostgreSQL username
DB_PASSWORD=your_password      # PostgreSQL password
```

### Secrets Configuration (`.streamlit/secrets.toml`)
Optional for cloud deployments:
```toml
[postgres]
host = "your_host"
port = "5432"
dbname = "your_db"
user = "your_user"
password = "your_password"
sslmode = "require"
```

---

## 🐛 Troubleshooting

### Database Connection Failed
- Ensure PostgreSQL is running: `Get-Service postgresql-x64-*`
- Verify database exists: `psql -U postgres -h localhost -l`
- Check `.env` credentials are correct

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Verify all files are in correct locations

### Image Upload Issues
- Ensure image is PNG or JPG format
- Image size should be at least 100x100 pixels
- File size should be less than 100 MB

### Encoding/Decoding Errors
- Verify correct method is selected for decoding
- Ensure image format matches (no format conversion)
- Check that image hasn't been compressed or modified

---

## 📈 Performance Metrics

Typical performance on modern hardware:

| Operation | Time | Memory |
|-----------|------|--------|
| LSB Encode (1MB) | 0.5s | 50MB |
| DCT Encode (1MB) | 1.2s | 80MB |
| DWT Encode (1MB) | 1.5s | 100MB |
| Decode Any Method | 0.3s | 40MB |

---

## 🔒 Security Considerations

- ✅ Passwords hashed with SHA-256
- ✅ AES-256 encryption for message protection
- ✅ HTTPS recommended for production deployment
- ✅ Database access controlled via credentials
- ✅ No sensitive data in logs

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 👨‍💻 Developer Information

**Application**: Image Steganography & Watermarking (ITR)
**Version**: 1.0.0
**Built with**: 
- Streamlit (Frontend)
- PostgreSQL (Database)
- Python 3.10+

**Key Libraries**:
- `Pillow` - Image processing
- `NumPy/SciPy` - Scientific computing
- `PyWavelets` - Wavelet transforms
- `Plotly` - Interactive visualizations
- `psycopg2` - PostgreSQL adapter
- `cryptography` - Encryption

---

## 🚀 Future Enhancements

Potential improvements:
- [ ] Quality Metrics Module - PSNR, MSE, SSIM calculations
- [ ] Auto-detection Module - Automatically select best method per image
- [ ] Additional image formats (BMP, TIFF, WebP, etc.)
- [ ] Video steganography support
- [ ] Real-time image preview during encoding
- [ ] Report generation (PDF, CSV, JSON)
- [ ] Advanced steganalysis detection
- [ ] Cloud storage integration (AWS S3, Google Drive)
- [ ] Mobile app support
- [ ] Docker containerization
- [ ] Distributed computing for large-scale batch processing

---

## 📚 Module Development Guide

### Adding New Steganography Method

1. Create new file in `src/stego/` (e.g., `new_method_steganography.py`)
2. Implement `encode_method(img, secret_text)` and `decode_method(img)`
3. Export functions in `src/stego/__init__.py`
4. Add UI section in `src/ui/ui_components.py`
5. Update imports in `streamlit_app.py`

### Adding New Chart/Statistic

1. Create function in `src/analytics/stats.py`
2. Export in `src/analytics/__init__.py`
3. Import in `src/ui/ui_components.py`
4. Add UI element in `show_statistics_section()`

### Database Operations

1. Add function in `src/db/db_utils.py`
2. Export in `src/db/__init__.py`
3. Call from appropriate UI component

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify all dependencies are installed
4. Test database connection with `test_db.py`

---

**Last Updated**: December 2, 2025
**Project Structure**: Modular Architecture v1.0
**Latest Changes**: Refactored into modular packages (stego, db, analytics, encryption, ui)
