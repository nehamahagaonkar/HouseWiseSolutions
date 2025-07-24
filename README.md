# HouseWiseSolutions

A comprehensive web application that connects customers with trusted service professionals, streamlining household service requests and management with a focus on security, usability, and efficiency.

---

## 🚀 Overview

**HouseWiseSolutions** is designed to bridge the gap between customers seeking household services and skilled professionals offering them. The platform ensures easy registration, robust role-based access, and a seamless user experience across all devices.

---

## ✨ Key Features

- **Admin Dashboard**
  - Manage, approve, or reject service professional applications.
  - Oversee and update the status of all service requests.

- **Customer Portal**
  - Secure registration and login using username-password authentication.
  - Submit and track service requests with real-time status updates.

- **Service Professional Portal**
  - Separate registration flow with admin approval.
  - Personalized dashboard to manage pending, accepted, or closed jobs.
  - Access restricted until approval for enhanced security.

- **Document Management**
  - Upload and store service-related documents (PDFs) securely in the `static/pdfs` directory.
  - Organized retrieval for both customers and professionals.

- **Security**
  - Password hashing ensures safe storage of credentials for all user types.
  - Flask’s `SECRET_KEY` safeguards sessions and protects against vulnerabilities.
  - Strict role-based access control for all dashboard and management features.

- **Responsive UI**
  - Built with Bootstrap for mobile-friendly and accessible design.
  - Jinja2 templates for dynamic and clean page rendering.

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 Templates
- **Database:** SQLite
- **File Storage:** Local directory (`static/pdfs`)

---

## 📝 Responsibilities & Contributions

- Architected and implemented authentication, registration, and user management workflows.
- Developed secure backend logic for dynamic role-based access and session handling.
- Designed robust document upload and retrieval systems.
- Collaborated on thorough testing to ensure data integrity and user experience.

---

## ⚡ Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/nehamahagaonkar/HouseWiseSolutions.git
   cd HouseWiseSolutions
   ```

2. **Set Up the Environment**
   - Install required Python packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Set your Flask `SECRET_KEY` in your environment or config file.

3. **Database Initialization**
   - The app uses SQLite. On first run, it will initialize the database automatically.

4. **Run the Application**
   ```bash
   flask run
   ```

5. **Access the App**
   - Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📂 Directory Structure

```
HouseWiseSolutions/
│
├── static/
│   └── pdfs/           # Service-related document storage
├── templates/          # Jinja2 HTML templates
├── app.py              # Main Flask application
├── requirements.txt    # Required Python libraries
└── README.md
```

---

## 🛡️ Security & Best Practices

- Passwords are always stored hashed.
- Session management uses securely loaded Flask `SECRET_KEY`.
- Access to dashboards and features is strictly role-based.
- Regular code reviews and testing ensure ongoing security and reliability.

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Please fork the repo and submit a PR for review.

---

## 📧 Contact

For questions or support, please open an issue in the repository.

---
