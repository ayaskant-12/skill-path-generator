# Skill Path Generator - AI Learning Companion

![Skill Path Generator](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue.svg)

A comprehensive AI-powered learning path generator that creates personalized skill development roadmaps using OpenAI's GPT-4. This application helps users achieve their career goals through structured, adaptive learning journeys.

## 🚀 Features

### Core Functionality
- **AI-Powered Path Generation**: Generate personalized learning paths using OpenAI GPT-4
- **Progress Tracking**: Visual progress indicators with todo, in-progress, and done statuses
- **Resource Management**: Curated learning resources (courses, videos, articles, books)
- **Multi-step Roadmaps**: Detailed step-by-step learning journeys
- **User Analytics**: Track completion rates and learning patterns

### User Experience
- **Futuristic Glassmorphism UI**: Modern, visually appealing interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Interactive Progress Management**: Easy progress updates with visual feedback
- **Personalized Dashboards**: Individual learning path overviews

### Admin Features
- **Resource Management**: Add, edit, and delete learning resources
- **Analytics Dashboard**: View platform usage and completion metrics
- **User Management**: Monitor user activity and learning patterns

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **PostgreSQL**: Database with SQLAlchemy ORM
- **OpenAI API**: AI-powered path generation
- **Jinja2**: Template engine

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Glassmorphism design with custom properties
- **JavaScript**: Interactive features and API calls
- **Font Awesome**: Icons

### DevOps
- **Python-dotenv**: Environment configuration
- **PostgreSQL**: Database management
- **Responsive Design**: Mobile-first approach

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- OpenAI API key

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/skill-path-generator.git
   cd skill-path-generator
   ```
2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   Environment Configuration
   ```
4. **Create a .env file in the root directory:**

   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@localhost/skill_path_generator
   OPENAI_API_KEY=your-openai-api-key-here
   ```
5. **Database Setup**

   ```bash
   # Create PostgreSQL database
   createdb skill_path_generator

   # The application will automatically create tables on first run
   ```
6. **Run the Application**

   ```bash
   python app.py
   ```
7. **Access the Application**
Open your browser and navigate to http://localhost:5000
#### Default Admin Account
Username: admin

Password: admin123

## 🗄️ Database Schema
The application uses the following main models:

**User**: User accounts and authentication

**SkillPath**: Main learning path containers

**PathStep**: Individual steps within learning paths

**Resource**: Learning resources (courses, videos, articles)

**StepResource**: Many-to-many relationship between steps and resources

**Progress**: User progress tracking

**Feedback**: User feedback and ratings

## 🔧 API Endpoints
### User Routes
**GET /** - Landing page

**GET/POST /login** - User authentication

**GET/POST /signup** - User registration

**GET /logout** - User logout

**GET /dashboard** - User dashboard

**GET/POST /generate_path** - AI path generation

**GET /path/<id>** - Path detail view

**POST /progress/<step_id>** - Progress updates

### Admin Routes
**GET /admin/resources** - Resource management

**GET /admin/analytics** - Analytics dashboard

## 🎨 UI/UX Features
### Design System
**Glassmorphism**: Semi-transparent cards with backdrop blur

**Neon Accents**: Vibrant color highlights

**Smooth Animations**: CSS transitions and transforms

**Progress Visualization**: Circular and linear progress indicators

### Responsive Breakpoints
**Mobile**: < 768px

**Tablet**: 768px - 1024px

**Desktop**: > 1024px

## 🤖 AI Integration
### OpenAI API Usage
The application uses GPT-4 to generate personalized learning paths based on:

**Career/skill goals**

**Current skill level**

**User interests**

**Available weekly hours**

**Desired timeline**

## 📊 Admin Analytics
**Available Metrics**
- **User Statistics**: Total users, active paths

- **Goal Popularity**: Most common career goals

- **Completion Rates**: Success rates by goal type

- **Trending Skills**: Popular learning categories

## 🔒 Security Features
- Password hashing with Werkzeug

- Session-based authentication

- CSRF protection

- SQL injection prevention with SQLAlchemy

- Input validation and sanitization

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
