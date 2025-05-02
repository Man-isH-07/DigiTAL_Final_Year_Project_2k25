# DigiTAL: AI-Driven Hospital Management System
![DigiTAL Logo](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/logo.png)  
*Revolutionizing Healthcare with AI and Blockchain*

Welcome to **DigiTAL**, a cutting-edge Digital Hospital Management System (HMS) designed to enhance hospital efficiency, patient care, and data security. Developed as a Bachelor of Engineering project at Sipna College of Engineering and Technology, Amravati, this system integrates **Artificial Intelligence (AI)** and **Blockchain Technology** to address challenges like long waiting times, insecure data management, and inefficient workflows.  

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [PPT Presentation](#ppt-presentation)
- [Future Scope](#future-scope)
- [Contributors](#contributors)
- [License](#license)

---

## Project Overview
DigiTAL is a modular, patient-centric HMS that automates hospital operations and secures medical data. It tackles inefficiencies in traditional healthcare systems through three main pillars:
1. **Virtual Waiting Room**: Reduces wait times with real-time queue management.
2. **AI-based Chatbot**: Automates appointment scheduling and doctor recommendations.
3. **Blockchain Security**: Ensures data integrity for prescriptions and lab reports.

The system was tested during the 2024-2025 academic year, achieving:
- **90%** workflow automation
- **100%** data integrity across 20 blockchain transactions
- **95%** reduction in paper-based workflows

---

## Key Features
- **Real-time Queue Management**: Uses WebSockets for live updates, reducing crowding with FIFO and Priority Queue algorithms.
- **AI-driven Chatbot**: Powered by SpaCy NER, it analyzes symptoms, recommends doctors (85% accuracy), and books appointments.
- **Blockchain-backed Security**: Secures medical records with SHA-256 hashing and Ganache-based Ethereum blockchain.
- **Modular Design**: Includes Patient, Desk, Doctor, Lab, and Pharmacy modules for seamless interdepartmental workflows.
- **Sustainability**: Eliminates paper use by 95% through digitized prescriptions and reports.

---

## System Architecture
DigiTAL follows a multi-layered, modular architecture:
- **Frontend**: HTML5, CSS3, JavaScript, and BotUI for responsive, user-friendly interfaces.
- **Backend**: Django with SQLite for robust logic and data management.
- **AI Module**: SpaCy NER for symptom analysis and doctor matching.
- **Blockchain Module**: Ganache and Solidity for secure data storage.
- **Real-time Features**: WebSockets for queue updates and notifications via Twilio/SendGrid.

![System Overview](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Flowcharts/sysOverview.png)

---

## Technologies Used
Below are the core technologies powering DigiTAL, along with their logos:

| Technology | Purpose | Logo |
|------------|---------|------|
| **Python** | Backend logic and AI implementation | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) |
| **Django** | Web framework for backend | ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) |
| **SQLite** | Database management | ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white) |
| **SpaCy** | NLP for AI chatbot | ![SpaCy](https://img.shields.io/badge/spacy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white) |
| **Ganache** | Simulated Ethereum blockchain | ![Ganache](https://img.shields.io/badge/ganache-000000?style=for-the-badge&logo=ethereum&logoColor=white) |
| **Solidity** | Smart contracts for blockchain | ![Solidity](https://img.shields.io/badge/solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white) |
| **WebSockets** | Real-time queue updates | ![WebSockets](https://img.shields.io/badge/websockets-000000?style=for-the-badge&logo=websocket&logoColor=white) |
| **HTML/CSS/JS** | Frontend development | ![HTML](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white) ![CSS](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white) ![JS](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) |
| **Git/GitHub** | Version control | ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) |

---

## Screenshots
Below are key screenshots from the DigiTAL system, showcasing its user interfaces:

|**Landing Page** | **Login Page** | **User Dashboard** | **AI Chatbot** |
|----------------|---------------------|----------------|----------------|
| ![Landing Page](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/landing_page.png) | ![Login Page](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/login.png) | ![User Dashboard](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/user_dashboard.png) | ![AI Chatbot](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/ai_chatbot.png) |

| **Virtual Waiting Room** | **Doctor Dashboard** | **Blockchain Dashboard** | **Lab Dashboard** |
|---------------------------|-----------------------|---------------------------|---------------------------|
| ![Virtual Waiting Room](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/virtual_waiting_room.png) | ![Doctor Dashboard](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/docotr_dashboard.png) | ![Blockchain Dashboard](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/blockchain_dashboard.png) | ![Lab Dashboard](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/Screenshots/lab_dashboard.png) |

---

## Installation
Follow these steps to set up DigiTAL locally:

### Prerequisites
- **Python 3.12+** ![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
- **Node.js** (for Ganache) ![Node.js](https://img.shields.io/badge/node.js-6DA55F?style=flat&logo=node.js&logoColor=white)
- **Git** ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=flat&logo=git&logoColor=white)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/digital-hms.git
   cd digital-hms
   ```

2. **Set Up Python Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Ganache CLI**:
   ```bash
   npm install -g ganache-cli
   ```

4. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start Ganache CLI**:
   ```bash
   ganache-cli -p 8545 -m "candy cream honey rich smooth crumble sweet treat"
   ```

6. **Run the Django Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:
   Open `http://localhost:8000` in your browser.

---

## Usage
- **Patients**: Register, book appointments via the AI chatbot or manually, and monitor queue status in the Virtual Waiting Room.
- **Doctors**: Access dashboards to view appointments, write prescriptions, and review lab reports.
- **Lab Technicians**: Manage test requests and upload reports, secured by blockchain.
- **Admins**: Oversee staff, patient records, and system operations via the Desk module.

---

## PPT Presentation
The project's PowerPoint presentation is available on GitHub:  
📎 [DigiTAL Presentation](https://github.com/Man-isH-07/DHMS_Final_Year_Project_2k25/blob/master/Research%20Paper%20%26%20Thesis/DigiTAL%20-%20fyp_PPT.pptx)  
![PowerPoint](https://img.shields.io/badge/PowerPoint-B7472A?style=flat&logo=microsoft-powerpoint&logoColor=white)

**PPT Highlights**:
- Introduction to DigiTAL and its problem statement
- Objectives: Automate scheduling, reduce wait times, secure data
- System overview with modules and technologies
- Detailed explanation of pillars: Virtual Waiting Room, AI Chatbot, Blockchain Security
- Advantages, challenges, and future scope
- Conclusion and references

---

## Future Scope
DigiTAL has immense potential for further enhancements:
- **IoT Integration**: Add wearable devices and smart beds for real-time health monitoring.
- **Advanced NLP**: Support multilingual chatbots and voice assistance.
- **Code Scanners**: Enhance lab sample verification with barcode scanners.
- **Predictive Analytics**: Implement AI for patient inflow prediction and resource allocation.
- **Cloud Deployment**: Scale with AWS for handling larger user bases.

---

## Contributors
- **Manish P. Dhaye**  
- **Prachi P. Ghatole**
- **Anushka P. Tayade**
- **Mandar G. Chatur**
- **Pravesh C. Mhaiskar**
- ***Guided by*: **Prof. Neha G. Rathi****

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
*Developed with 💻 and ❤️ at Sipna College of Engineering and Technology, Amravati*