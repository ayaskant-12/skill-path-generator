
## SRS.md

  ```markdown
  # Software Requirements Specification (SRS)
  # Skill Path Generator - AI Learning Companion
  ```
## 1. Introduction

### 1.1 Purpose
The Skill Path Generator is a web-based application that uses artificial intelligence to create personalized learning roadmaps for users seeking to develop new skills or advance their careers. This document outlines the functional and non-functional requirements for the system.

### 1.2 Scope
The system will provide AI-generated personalized learning paths, progress tracking, resource management, and administrative analytics. It will serve individual learners, career changers, and educational institutions.

### 1.3 Definitions
- **Skill Path**: A structured learning roadmap for a specific career or skill goal
- **Path Step**: Individual learning milestone within a skill path
- **Resource**: Learning material (course, video, article, book)
- **Progress Tracking**: Monitoring user completion of path steps

## 2. Overall Description

### 2.1 Product Perspective
The system is a standalone web application with modern architecture, integrating with OpenAI API for AI capabilities and PostgreSQL for data persistence.

### 2.2 Product Functions
- User registration and authentication
- AI-powered learning path generation
- Progress tracking and management
- Resource curation and management
- Administrative analytics and reporting
- Responsive web interface

### 2.3 User Characteristics
- **End Users**: Individuals seeking skill development (beginner to advanced)
- **Administrators**: Platform managers overseeing resources and analytics
- **Technical Level**: Users require basic web browsing skills

### 2.4 Constraints
- Requires OpenAI API access
- PostgreSQL database required
- Modern web browser support
- Internet connectivity for AI features

### 2.5 Assumptions and Dependencies
- Users have clear career/skill goals
- OpenAI API remains accessible and affordable
- Users can dedicate time weekly to learning

## 3. System Features

### 3.1 User Authentication
#### 3.1.1 Description
Secure user registration, login, and session management.

#### 3.1.2 Functional Requirements
- **FR1**: Users can register with username, email, and password
- **FR2**: Users can log in with credentials
- **FR3**: Passwords are securely hashed
- **FR4**: Sessions maintain user state
- **FR5**: Users can log out securely

### 3.2 AI Path Generation
#### 3.2.1 Description
Generate personalized learning paths using OpenAI GPT-4 based on user inputs.

#### 3.2.2 Functional Requirements
- **FR6**: Users can input career goals, current level, interests, time commitment
- **FR7**: System calls OpenAI API with structured prompts
- **FR8**: AI response is validated against JSON schema
- **FR9**: Generated paths are saved to user account
- **FR10**: Fallback path generation if AI service unavailable

### 3.3 Progress Tracking
#### 3.3.1 Description
Track and visualize user progress through learning paths.

#### 3.3.2 Functional Requirements
- **FR11**: Users can update step status (todo, in-progress, done)
- **FR12**: Progress is visually represented with percentage completion
- **FR13**: Progress data is persisted and retrievable
- **FR14**: Overall path completion is calculated automatically

### 3.4 Resource Management
#### 3.4.1 Description
Manage learning resources associated with path steps.

#### 3.4.2 Functional Requirements
- **FR15**: Resources can be courses, videos, articles, or books
- **FR16**: Resources are linked to specific path steps
- **FR17**: Admin can manage resource database
- **FR18**: Users can access resources via provided URLs

### 3.5 Administrative Features
#### 3.5.1 Description
Platform management and analytics for administrators.

#### 3.5.2 Functional Requirements
- **FR19**: Admin can view platform usage statistics
- **FR20**: Admin can manage all learning resources
- **FR21**: Analytics on popular goals and completion rates
- **FR22**: Admin dashboard with visual metrics

### 3.6 User Interface
#### 3.6.1 Description
Modern, responsive web interface with glassmorphism design.

#### 3.6.2 Functional Requirements
- **FR23**: Responsive design for mobile and desktop
- **FR24**: Glassmorphism UI with modern aesthetics
- **FR25**: Interactive progress management
- **FR26**: Intuitive navigation and user flows

## 4. External Interface Requirements

### 4.1 User Interfaces
- **Web Interface**: HTML5, CSS3, JavaScript
- **Design System**: Glassmorphism with neon accents
- **Responsive Breakpoints**: Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)

### 4.2 Hardware Interfaces
- Standard web server hardware requirements
- Client devices with modern web browsers

### 4.3 Software Interfaces
- **OpenAI API**: GPT-4 for path generation
- **PostgreSQL**: Database management
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM

### 4.4 Communications Interfaces
- HTTP/HTTPS protocols
- RESTful API design
- WebSocket for real-time updates (future)

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **PR1**: Page load times under 3 seconds
- **PR2**: AI path generation under 10 seconds
- **PR3**: Support 1000+ concurrent users
- **PR4**: Database queries under 100ms

### 5.2 Security Requirements
- **SR1**: Password hashing with industry standards
- **SR2**: SQL injection prevention
- **SR3**: XSS protection
- **SR4**: CSRF protection
- **SR5**: Session management security

### 5.3 Software Quality Attributes
- **Availability**: 99.5% uptime
- **Reliability**: Error rate < 1%
- **Maintainability**: Modular code structure
- **Portability**: Cross-browser compatibility
- **Usability**: Intuitive user interface

### 5.4 Business Rules
- **BR1**: Free user registration
- **BR2**: Unlimited path generation per user
- **BR3**: Admin approval for resource changes
- **BR4**: Data retention for analytics

## 6. System Architecture

### 6.1 High-Level Architecture
  ```
  Client Layer (Web Browser)
              ↓
  Presentation Layer (Flask Templates)
              ↓
  Application Layer (Flask Routes & Business Logic)
              ↓
  Data Layer (SQLAlchemy + PostgreSQL)
              ↓
  External Services (OpenAI API)
  ```

### 6.2 Database Schema
#### User Table
- id, username, email, password_hash, is_admin, created_at

#### SkillPath Table
- id, title, description, career_goal, current_level, interests, weekly_hours, timeline_weeks, user_id, created_at

#### PathStep Table
- id, skill_path_id, step_number, title, description, duration_weeks

#### Resource Table
- id, title, url, type, description, created_by_admin

#### Progress Table
- id, skill_path_id, step_id, user_id, status, completed_at, created_at

## 7. Data Requirements

### 7.1 Data Persistence
- User accounts and profiles
- Generated learning paths and steps
- Progress tracking data
- Learning resources
- Administrative analytics

### 7.2 Data Validation
- Input sanitization for all user inputs
- JSON schema validation for AI responses
- Database constraint enforcement
- Type checking for API parameters

## 8. Appendices

### 8.1 AI Prompt Schema
  ```json
  {
    "career_goal": "string",
    "current_level": "beginner|intermediate|advanced",
    "interests": "string",
    "weekly_hours": "integer",
    "timeline_weeks": "integer"
  }
  ```

### 8.2 AI Response Schema
  ```json
  {
    "title": "string",
    "description": "string",
    "steps": [
      {
        "step_number": "integer",
        "title": "string",
        "description": "string",
        "duration_weeks": "integer",
        "resources": [
          {
            "title": "string",
            "url": "string",
            "type": "course|video|article|book",
            "description": "string"
          }
        ]
      }
    ]
  }
  ```
### 8.3 Error Handling
- **AI service unavailable** → Fallback path generation

- **Database connection issues** → Graceful error messages

- **Invalid user input** → Form validation feedback

- **Authentication failures** → Redirect to login

## 9. Glossary
- **Glassmorphism**: UI design style with transparency and blur effects

- **GPT-4**: OpenAI's generative pre-trained transformer model

- **ORM**: Object-Relational Mapping for database operations

- **RESTful**: Architectural style for web services

- **SQLAlchemy**: Python SQL toolkit and ORM

