# HouseWiseSolutions
Household Solution App

Overview: Developed a feature-rich web application designed to connect customers with service professionals for household solutions, focusing on secure access, efficient task management, and user-friendly interfaces.

=> Key Features:

>>Admin Dashboard: Facilitated admin management of service professionals, including approvals, rejections, and oversight of service statuses.
>>Customer Registration and Login: Implemented secure customer authentication using username-password workflows.
>>Service Professional Management:
Separate registration system for service professionals with approval-based access.
Dashboards tailored for managing service requests categorized as pending, accepted, or closed.
Restricted dashboard visibility for unapproved service professionals.
>>Document Handling: Designed a file upload system to store service-related PDFs in the static/pdfs directory.
>>Security Enhancements:
Implemented password hashing for service professional accounts to ensure secure storage.
Loaded Flask’s SECRET_KEY to manage secure user sessions and protect against common >>vulnerabilities.
User Experience: Integrated a responsive design using Bootstrap to ensure compatibility across devices.

=>Challenges and Solutions:

Resolved inconsistent password storage by implementing uniform hashing mechanisms across user types.
Optimized role-based access control for seamless navigation and functionality based on user roles (customer, service professional, admin).

=>Tech Stack:
Flask (Python)
HTML/CSS
Bootstrap
SQLite,
Jinja2 templates.

Responsibilities:

Designed and implemented core application workflows, including authentication, registration, and request management.
Developed robust backend logic to handle user roles and access control dynamically.
Collaborated on debugging and testing to ensure data security and usability.
Integrated structured file handling for organized document storage and retrieval.
