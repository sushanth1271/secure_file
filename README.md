# Secure File Storage Using Hybrid Cryptography

## Project Overview

This project is a secure file storage system built using **Flask** and **Python**, employing **hybrid cryptography** (RSA + AES) to encrypt and decrypt files. Users can upload files, encrypt them, download their private key, and decrypt files securely.

## Features

* Upload files and encrypt them using AES + RSA hybrid encryption.
* Download private key for decryption.
* Upload private key to decrypt files.
* Automatic cleanup of old files when new files are uploaded.
* Dashboard interface to manage all operations.

## Folder Structure

```
secure_file/
│
├── app.py                # Main Flask application
├── tools.py              # Helper functions (empty_folder, list_dir)
├── templates/            # HTML templates
│   ├── index.html        # Landing page
│   └── download.html     # Dashboard page
├── uploads/              # Temporary folder for uploaded files
├── key/                  # Folder to store private keys
├── encrypted/            # Folder to store encrypted files
├── restored_file/        # Folder to store decrypted files
└── README.md             # Project documentation
```

## Installation

1. **Clone the repository** (or extract provided zip file).
2. **Navigate to project directory:**

   ```bash
   cd secure_file
   ```
3. **Create virtual environment (optional but recommended):**

   ```bash
   python -m venv .venv
   ```
4. **Activate virtual environment:**

   * Windows: `.\.venv\Scripts\activate`
   * Linux/Mac: `source .venv/bin/activate`
5. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *(Requirements: Flask, pycryptodome, Werkzeug)*
    ## Requirements include:
    * Flask==2.2.5
    * pycryptodome==3.20.0
    * cryptography>=42.0.0
    * Werkzeug
    * Jinja2==3.1.2
## Running the Project

1. Start the Flask server:

   ```bash
   python app.py
   ```
2. Open browser and navigate to:

   ```
   http://127.0.0.1:8000
   ```

## Usage

1. **Landing Page:**

   * Click **Go to Dashboard** to access the main file management interface.

2. **Step 1: Upload & Encrypt**

   * Upload a file you want to encrypt.
   * The system automatically clears old files in `uploads/`, `encrypted/`, and `restored_file/`.
   * Click **Upload & Encrypt**.

3. **Step 2: Download Private Key**

   * After encryption, download the private key `.pem` file.
   * Keep it safe; it is required for decryption.

4. **Step 3: Upload Key & Decrypt**

   * Upload your private key file.
   * Click **Upload Key & Decrypt**.

5. **Step 4: Download Restored File**

   * Once decrypted, click **Download Restored File**.

## Notes

* Ensure to keep your private key safe; losing it means you cannot decrypt your files.
* The system clears old files when new files are uploaded to prevent clutter.
* AES encryption is used for fast file encryption; RSA encrypts the AES session key securely.


## Dependencies

* Python 3.8+
* Flask
* pycryptodome
* Werkzeug


## Credits

* Project developed by **Sagar R S**
* MCA, Dept of CS\&E
* USN: 4VZ23MC094

## License

* This project is for educational purposes and personal use.
