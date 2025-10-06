import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import openai
from dotenv import load_dotenv
import logging
from sqlalchemy import func, extract, case, and_
from datetime import datetime, timedelta
from collections import defaultdict

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/skill_path_generator')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    skill_paths = relationship('SkillPath', back_populates='user', cascade='all, delete-orphan')

class SkillPath(db.Model):
    __tablename__ = 'skill_paths'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    career_goal = db.Column(db.String(200), nullable=False)
    current_level = db.Column(db.String(50), nullable=False)
    interests = db.Column(db.Text)
    weekly_hours = db.Column(db.Integer, nullable=False)
    timeline_weeks = db.Column(db.Integer, nullable=False)
    generated_content = db.Column(db.JSON)  # Store AI-generated JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='skill_paths')
    steps = relationship('PathStep', back_populates='skill_path', cascade='all, delete-orphan')

class PathStep(db.Model):
    __tablename__ = 'path_steps'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_path_id = db.Column(db.String(36), db.ForeignKey('skill_paths.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer)
    milestone = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skill_path = relationship('SkillPath', back_populates='steps')
    progress = relationship('Progress', back_populates='step', uselist=False, cascade='all, delete-orphan')
    step_resources = relationship('StepResource', back_populates='step', cascade='all, delete-orphan')

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500))
    type = db.Column(db.String(50))  # video, article, course, book, etc.
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    step_resources = relationship('StepResource', back_populates='resource', cascade='all, delete-orphan')

class StepResource(db.Model):
    __tablename__ = 'step_resources'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    step_id = db.Column(db.String(36), db.ForeignKey('path_steps.id'), nullable=False)
    resource_id = db.Column(db.String(36), db.ForeignKey('resources.id'), nullable=False)
    
    # Relationships
    step = relationship('PathStep', back_populates='step_resources')
    resource = relationship('Resource', back_populates='step_resources')

class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    step_id = db.Column(db.String(36), db.ForeignKey('path_steps.id'), nullable=False)
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, done
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    step = relationship('PathStep', back_populates='progress')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skill_path_id = db.Column(db.String(36), db.ForeignKey('skill_paths.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# AI Integration Functions
def generate_skill_path_prompt(career_goal, current_level, interests, weekly_hours, timeline_weeks):
    """Generate the prompt for OpenAI to create a learning path"""
    
    prompt = f"""
    Create a detailed, personalized learning roadmap for someone who wants to become a {career_goal}.
    
    USER PROFILE:
    - Current Skill Level: {current_level}
    - Interests: {interests}
    - Weekly Study Hours: {weekly_hours}
    - Timeline: {timeline_weeks} weeks
    
    REQUIREMENTS:
    Generate a structured learning path with 6-12 steps that progressively build skills.
    Include milestones to mark significant achievements.
    For each step, suggest 2-3 learning resources (courses, books, tutorials, projects).
    
    OUTPUT FORMAT (JSON):
    {{
        "title": "Comprehensive Learning Path for [Career Goal]",
        "description": "Detailed description of the learning journey",
        "steps": [
            {{
                "step_number": 1,
                "title": "Step title",
                "description": "Detailed learning objectives and outcomes",
                "duration_weeks": 2,
                "milestone": false,
                "resources": [
                    {{
                        "title": "Resource title",
                        "url": "https://example.com",
                        "type": "course/video/article/book",
                        "description": "Why this resource is valuable"
                    }}
                ]
            }}
        ],
        "milestones": [
            "List of major achievements throughout the path"
        ]
    }}
    
    Make the path realistic for the given timeline and weekly hours. Focus on practical, hands-on learning.
    """
    
    return prompt

def validate_ai_json_schema(data):
    """Validate the AI-generated JSON against our expected schema"""
    try:
        if not isinstance(data, dict):
            return False, "Root must be an object"
        
        required_fields = ['title', 'description', 'steps']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        if not isinstance(data['steps'], list):
            return False, "Steps must be an array"
        
        for step in data['steps']:
            if not all(key in step for key in ['step_number', 'title', 'description', 'duration_weeks']):
                return False, "Step missing required fields"
            
            if 'resources' in step and not isinstance(step['resources'], list):
                return False, "Step resources must be an array"
        
        return True, "Valid schema"
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def call_openai_api(prompt):
    """Call OpenAI API to generate the learning path with better error handling"""
    try:
        # Check if API key is available
        if not openai.api_key:
            logging.error("OpenAI API key is not set")
            return None
        
        # Use a more available model and better error handling
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # More available than gpt-4
            messages=[
                {"role": "system", "content": "You are an expert career coach and learning path designer. Create structured, practical learning roadmaps. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000  # Reduced for cost and reliability
        )
        
        content = response.choices[0].message.content.strip()
        
        # More robust JSON extraction
        if '```json' in content:
            content = content[content.find('```json') + 7:content.rfind('```')]
        elif '```' in content:
            content = content[content.find('```') + 3:content.rfind('```')]
        
        # Clean the content
        content = content.strip()
        
        return json.loads(content)
    
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        logging.error(f"Response content: {content}")
        return None
    except openai.error.AuthenticationError as e:
        logging.error(f"OpenAI Authentication Error: {str(e)}")
        return None
    except openai.error.RateLimitError as e:
        logging.error(f"OpenAI Rate Limit Error: {str(e)}")
        return None
    except openai.error.APIError as e:
        logging.error(f"OpenAI API Error: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in call_openai_api: {str(e)}")
        return None
    
def generate_mock_learning_path(career_goal, current_level, interests, weekly_hours, timeline_weeks):
    """Generate mock learning path data for testing when OpenAI API fails"""
    
    mock_path = {
        "title": f"Learning Path for {career_goal}",
        "description": f"A comprehensive learning journey from {current_level} to professional level in {career_goal}. Focuses on {interests} with {weekly_hours} hours per week over {timeline_weeks} weeks.",
        "steps": [
            {
                "step_number": 1,
                "title": "Foundation and Basics",
                "description": f"Learn the fundamental concepts and principles of {career_goal}. Build a strong foundation for advanced topics.",
                "duration_weeks": max(2, timeline_weeks // 6),
                "milestone": False,
                "resources": [
                    {
                        "title": "Introduction to Fundamentals",
                        "url": "https://example.com/fundamentals",
                        "type": "course",
                        "description": "Comprehensive course covering basic concepts"
                    }
                ]
            },
            {
                "step_number": 2,
                "title": "Core Skills Development",
                "description": "Develop essential skills and techniques through hands-on practice and projects.",
                "duration_weeks": max(3, timeline_weeks // 4),
                "milestone": True,
                "resources": [
                    {
                        "title": "Core Skills Workshop",
                        "url": "https://example.com/core-skills",
                        "type": "tutorial",
                        "description": "Interactive workshop for skill development"
                    }
                ]
            },
            {
                "step_number": 3,
                "title": "Advanced Techniques",
                "description": "Master advanced concepts and specialized techniques in your chosen field.",
                "duration_weeks": max(3, timeline_weeks // 4),
                "milestone": False,
                "resources": [
                    {
                        "title": "Advanced Concepts Guide",
                        "url": "https://example.com/advanced",
                        "type": "book",
                        "description": "In-depth guide to advanced topics"
                    }
                ]
            },
            {
                "step_number": 4,
                "title": "Real-world Projects",
                "description": "Apply your skills to real-world projects and build a portfolio.",
                "duration_weeks": max(2, timeline_weeks // 6),
                "milestone": True,
                "resources": [
                    {
                        "title": "Project Ideas Repository",
                        "url": "https://example.com/projects",
                        "type": "project",
                        "description": "Collection of project ideas and templates"
                    }
                ]
            },
            {
                "step_number": 5,
                "title": "Professional Development",
                "description": "Prepare for professional opportunities and career advancement.",
                "duration_weeks": max(2, timeline_weeks // 6),
                "milestone": True,
                "resources": [
                    {
                        "title": "Career Preparation Guide",
                        "url": "https://example.com/career",
                        "type": "article",
                        "description": "Guide to professional development and job search"
                    }
                ]
            }
        ],
        "milestones": [
            "Complete foundation understanding",
            "Develop core practical skills", 
            "Build portfolio projects",
            "Prepare for professional opportunities"
        ]
    }
    
    return mock_path

# Authentication Decorators
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('signup.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_paths = SkillPath.query.filter_by(user_id=session['user_id']).order_by(SkillPath.created_at.desc()).all()
    
    # Calculate progress for each path
    paths_with_progress = []
    for path in user_paths:
        total_steps = len(path.steps)
        if total_steps == 0:
            completion_percentage = 0
        else:
            completed_steps = sum(1 for step in path.steps if step.progress and step.progress.status == 'done')
            completion_percentage = int((completed_steps / total_steps) * 100)
        
        paths_with_progress.append({
            'path': path,
            'completion_percentage': completion_percentage
        })
    
    return render_template('dashboard.html', paths=paths_with_progress)

@app.route('/generate_path', methods=['GET', 'POST'])
@login_required
def generate_path():
    if request.method == 'POST':
        career_goal = request.form.get('career_goal')
        current_level = request.form.get('current_level')
        interests = request.form.get('interests')
        weekly_hours = int(request.form.get('weekly_hours', 0))
        timeline_weeks = int(request.form.get('timeline_weeks', 0))
        
        if not all([career_goal, current_level, interests, weekly_hours, timeline_weeks]):
            flash('All fields are required.', 'error')
            return render_template('generate_path.html')
        
        # Generate AI learning path
        prompt = generate_skill_path_prompt(career_goal, current_level, interests, weekly_hours, timeline_weeks)
        ai_response = call_openai_api(prompt)
        
        # If OpenAI fails, use mock data
        if not ai_response:
            logging.info("OpenAI API failed, using mock data")
            ai_response = generate_mock_learning_path(career_goal, current_level, interests, weekly_hours, timeline_weeks)
            flash('AI service is temporarily unavailable. Showing sample learning path.', 'warning')
        
        # Validate JSON schema
        is_valid, validation_msg = validate_ai_json_schema(ai_response)
        if not is_valid:
            flash(f'Invalid path format: {validation_msg}', 'error')
            return render_template('generate_path.html')
        
        # Create skill path
        skill_path = SkillPath(
            user_id=session['user_id'],
            title=ai_response['title'],
            description=ai_response['description'],
            career_goal=career_goal,
            current_level=current_level,
            interests=interests,
            weekly_hours=weekly_hours,
            timeline_weeks=timeline_weeks,
            generated_content=ai_response
        )
        
        db.session.add(skill_path)
        db.session.flush()
        
        # Create steps and resources
        for step_data in ai_response['steps']:
            step = PathStep(
                skill_path_id=skill_path.id,
                step_number=step_data['step_number'],
                title=step_data['title'],
                description=step_data['description'],
                duration_weeks=step_data.get('duration_weeks', 1),
                milestone=step_data.get('milestone', False)
            )
            
            db.session.add(step)
            db.session.flush()
            
            # Create progress entry for this step
            progress = Progress(step_id=step.id)
            db.session.add(progress)
            
            # Create resources for this step
            for resource_data in step_data.get('resources', []):
                # Check if resource already exists
                resource = Resource.query.filter_by(url=resource_data.get('url')).first()
                if not resource and resource_data.get('url'):
                    resource = Resource(
                        title=resource_data['title'],
                        url=resource_data.get('url', ''),
                        type=resource_data.get('type', 'article'),
                        description=resource_data.get('description', ''),
                        category=career_goal
                    )
                    db.session.add(resource)
                    db.session.flush()
                
                if resource:
                    step_resource = StepResource(step_id=step.id, resource_id=resource.id)
                    db.session.add(step_resource)
        
        db.session.commit()
        flash('Learning path generated successfully!', 'success')
        return redirect(url_for('path_detail', id=skill_path.id))
    
    return render_template('generate_path.html')

# Add this function to app.py (anywhere before the routes)
def get_resource_icon(resource_type):
    """Get Font Awesome icon for resource type"""
    icons = {
        'course': 'graduation-cap',
        'video': 'video',
        'article': 'newspaper',
        'book': 'book',
        'tutorial': 'laptop-code',
        'project': 'project-diagram',
        'documentation': 'file-alt'
    }
    return icons.get(resource_type, 'link')

# Add this context processor to make the function available in all templates
# Add this context processor to make the function available in all templates
@app.context_processor
def utility_processor():
    def get_resource_icon(resource_type):
        """Get Font Awesome icon for resource type"""
        icons = {
            'course': 'graduation-cap',
            'video': 'video',
            'article': 'newspaper',
            'book': 'book',
            'tutorial': 'laptop-code',
            'project': 'project-diagram',
            'documentation': 'file-alt'
        }
        return icons.get(resource_type, 'link')
    
    return {
        'get_resource_icon': get_resource_icon,
        'now': datetime.utcnow
    }

@app.route('/path/<id>')
@login_required
def path_detail(id):
    skill_path = SkillPath.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    
    # Calculate overall progress
    total_steps = len(skill_path.steps)
    completed_steps = sum(1 for step in skill_path.steps if step.progress and step.progress.status == 'done')
    completion_percentage = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
    
    # Group steps by milestone
    steps_by_milestone = []
    current_milestone = None
    milestone_steps = []
    
    for step in sorted(skill_path.steps, key=lambda x: x.step_number):
        if step.milestone and milestone_steps:
            steps_by_milestone.append({
                'milestone': current_milestone,
                'steps': milestone_steps
            })
            milestone_steps = []
        
        if step.milestone:
            current_milestone = step
        
        milestone_steps.append(step)
    
    if milestone_steps:
        steps_by_milestone.append({
            'milestone': current_milestone,
            'steps': milestone_steps
        })
    
    return render_template('path_detail.html', 
                         path=skill_path, 
                         completion_percentage=completion_percentage,
                         steps_by_milestone=steps_by_milestone)

@app.route('/progress/<step_id>', methods=['POST'])
@login_required
def update_progress(step_id):
    step = PathStep.query.join(SkillPath).filter(
        PathStep.id == step_id,
        SkillPath.user_id == session['user_id']
    ).first_or_404()
    
    status = request.json.get('status')
    if status not in ['todo', 'in_progress', 'done']:
        return jsonify({'error': 'Invalid status'}), 400
    
    if not step.progress:
        progress = Progress(step_id=step_id, status=status)
        db.session.add(progress)
    else:
        step.progress.status = status
        if status == 'done':
            step.progress.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Calculate new completion percentage
    total_steps = len(step.skill_path.steps)
    completed_steps = sum(1 for s in step.skill_path.steps if s.progress and s.progress.status == 'done')
    completion_percentage = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
    
    return jsonify({
        'success': True,
        'completion_percentage': completion_percentage
    })

# Admin Routes
@app.route('/admin/resources')
@admin_required
def admin_resources():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    return render_template('admin/resources.html', resources=resources)

# Add these imports at the top
from flask import request
import json

# Resource Management Routes
@app.route('/admin/resources/add', methods=['POST'])
@admin_required
def add_resource():
    """Add a new resource"""
    try:
        data = request.get_json()
        
        resource = Resource(
            title=data['title'],
            type=data['type'],
            category=data.get('category', ''),
            url=data.get('url', ''),
            description=data.get('description', '')
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resource added successfully!',
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'type': resource.type,
                'category': resource.category,
                'url': resource.url,
                'description': resource.description,
                'created_at': resource.created_at.isoformat()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding resource: {str(e)}'
        }), 500

@app.route('/admin/resources/<resource_id>', methods=['GET'])
@admin_required
def get_resource(resource_id):
    """Get a specific resource"""
    try:
        resource = Resource.query.get_or_404(resource_id)
        
        return jsonify({
            'success': True,
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'type': resource.type,
                'category': resource.category,
                'url': resource.url,
                'description': resource.description,
                'created_at': resource.created_at.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching resource: {str(e)}'
        }), 404

@app.route('/admin/resources/<resource_id>', methods=['PUT'])
@admin_required
def update_resource(resource_id):
    """Update a resource"""
    try:
        resource = Resource.query.get_or_404(resource_id)
        data = request.get_json()
        
        resource.title = data['title']
        resource.type = data['type']
        resource.category = data.get('category', '')
        resource.url = data.get('url', '')
        resource.description = data.get('description', '')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resource updated successfully!',
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'type': resource.type,
                'category': resource.category,
                'url': resource.url,
                'description': resource.description
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating resource: {str(e)}'
        }), 500

@app.route('/admin/resources/<resource_id>', methods=['DELETE'])
@admin_required
def delete_resource(resource_id):
    """Delete a resource"""
    try:
        resource = Resource.query.get_or_404(resource_id)
        
        # Delete associated step_resources first
        StepResource.query.filter_by(resource_id=resource_id).delete()
        
        db.session.delete(resource)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resource deleted successfully!'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting resource: {str(e)}'
        }), 500

@app.route('/admin/resources/bulk_delete', methods=['POST'])
@admin_required
def bulk_delete_resources():
    """Bulk delete resources"""
    try:
        data = request.get_json()
        resource_ids = data.get('resource_ids', [])
        
        if not resource_ids:
            return jsonify({
                'success': False,
                'message': 'No resources selected for deletion'
            }), 400
        
        # Delete associated step_resources first
        StepResource.query.filter(StepResource.resource_id.in_(resource_ids)).delete()
        
        # Delete resources
        Resource.query.filter(Resource.id.in_(resource_ids)).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(resource_ids)} resources deleted successfully!'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting resources: {str(e)}'
        }), 500

# Update the admin_analytics route in app.py
# Update the admin_analytics route in app.py
@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    # Basic analytics data
    total_users = User.query.count()
    total_paths = SkillPath.query.count()
    total_feedback = Feedback.query.count()
    
    # Calculate overall completion rate
    total_steps = db.session.query(PathStep).count()
    completed_steps = db.session.query(Progress).filter_by(status='done').count()
    overall_completion_rate = round((completed_steps / total_steps * 100) if total_steps > 0 else 0, 1)
    
    # Top career goals
    top_goals = db.session.query(
        SkillPath.career_goal,
        func.count(SkillPath.id).label('count')
    ).group_by(SkillPath.career_goal).order_by(func.count(SkillPath.id).desc()).limit(10).all()
    
    # Completion rates by goal
    completion_data = []
    for goal in top_goals[:5]:
        goal_paths = SkillPath.query.filter_by(career_goal=goal[0]).all()
        goal_steps = 0
        goal_completed = 0
        
        for path in goal_paths:
            for step in path.steps:
                goal_steps += 1
                if step.progress and step.progress.status == 'done':
                    goal_completed += 1
        
        completion_rate = round((goal_completed / goal_steps * 100) if goal_steps > 0 else 0, 1)
        completion_data.append({
            'goal': goal[0],
            'completion_rate': completion_rate,
            'total_paths': len(goal_paths),
            'total_users': len(set([path.user_id for path in goal_paths]))
        })
    
    # User growth data (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    user_growth = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= thirty_days_ago).group_by(
        func.date(User.created_at)
    ).order_by('date').all()
    
    # Path creation data (last 30 days)
    path_growth = db.session.query(
        func.date(SkillPath.created_at).label('date'),
        func.count(SkillPath.id).label('count')
    ).filter(SkillPath.created_at >= thirty_days_ago).group_by(
        func.date(SkillPath.created_at)
    ).order_by('date').all()
    
    # Resource usage statistics
    total_resources = Resource.query.count()
    resources_by_type = db.session.query(
        Resource.type,
        func.count(Resource.id).label('count')
    ).group_by(Resource.type).all()
    
    # User engagement metrics - FIXED QUERY
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users_query = db.session.query(
        func.count(func.distinct(SkillPath.user_id))
    ).join(PathStep).join(Progress).filter(
        Progress.updated_at >= seven_days_ago
    )
    active_users_count = active_users_query.scalar() or 0
    
    # Alternative simpler approach for active users (users with any activity in last 7 days)
    # This counts users who have created paths or updated progress in the last 7 days
    recent_path_users = db.session.query(
        func.count(func.distinct(SkillPath.user_id))
    ).filter(SkillPath.created_at >= seven_days_ago).scalar() or 0
    
    recent_progress_users = db.session.query(
        func.count(func.distinct(SkillPath.user_id))
    ).join(PathStep).join(Progress).filter(
        Progress.updated_at >= seven_days_ago
    ).scalar() or 0
    
    active_users = recent_path_users + recent_progress_users
    
    # Recent activity data
    recent_paths = SkillPath.query.order_by(SkillPath.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Platform insights - Fixed queries using Python calculations
    # Calculate average steps per path in Python
    all_paths = SkillPath.query.all()
    total_steps_all_paths = sum(len(path.steps) for path in all_paths)
    avg_steps_per_path = total_steps_all_paths / len(all_paths) if all_paths else 0
    
    # Calculate average resources per step in Python
    all_steps = PathStep.query.all()
    total_resources_all_steps = sum(len(step.step_resources) for step in all_steps)
    avg_resources_per_step = total_resources_all_steps / len(all_steps) if all_steps else 0
    
    # Trending skills (based on recent path creation)
    trending_skills = db.session.query(
        SkillPath.career_goal,
        func.count(SkillPath.id).label('count')
    ).filter(
        SkillPath.created_at >= datetime.utcnow() - timedelta(days=30)
    ).group_by(SkillPath.career_goal).order_by(
        func.count(SkillPath.id).desc()
    ).limit(5).all()
    
    # Calculate completion rates for trending skills
    trending_skills_with_completion = []
    for skill in trending_skills:
        skill_paths = SkillPath.query.filter_by(career_goal=skill.career_goal).all()
        total_skill_steps = 0
        completed_skill_steps = 0
        
        for path in skill_paths:
            for step in path.steps:
                total_skill_steps += 1
                if step.progress and step.progress.status == 'done':
                    completed_skill_steps += 1
        
        completion_rate = round((completed_skill_steps / total_skill_steps * 100) if total_skill_steps > 0 else 0, 1)
        
        trending_skills_with_completion.append({
            'career_goal': skill.career_goal,
            'count': skill.count,
            'completion_rate': completion_rate
        })
    
    # Get current timestamp for the template
    now = datetime.utcnow()
    
    return render_template('admin/analytics.html',
                         total_users=total_users,
                         total_paths=total_paths,
                         total_feedback=total_feedback,
                         overall_completion_rate=overall_completion_rate,
                         top_goals=top_goals,
                         completion_data=completion_data,
                         user_growth=user_growth,
                         path_growth=path_growth,
                         total_resources=total_resources,
                         resources_by_type=resources_by_type,
                         active_users=active_users,
                         recent_paths=recent_paths,
                         recent_users=recent_users,
                         avg_steps_per_path=round(avg_steps_per_path, 1),
                         avg_resources_per_step=round(avg_resources_per_step, 1),
                         trending_skills=trending_skills_with_completion,
                         now=now)

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@skillpath.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
