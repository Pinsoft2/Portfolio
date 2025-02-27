# Interactive Valentine's Day Calendar
#### Video Demo: <[cs50x final project Pinsoft](https://www.youtube.com/watch?v=3U20bq5LGUY)>
#### Description:

This project is an interactive web-based Valentine's Day Calendar, inspired by advent calendars but designed specifically for sharing romantic messages and images. The application features a heart-shaped grid of interactive boxes that can be customized with personal images and messages, making it a unique digital gift for Valentine's Day.

## Features

### User Authentication System
- Multi-level authentication system with user accounts and calendar-specific passwords
- Secure password hashing using Werkzeug's security features
- Session management for persistent user sessions
- Admin panel access control

### Interactive Calendar Interface
- Heart-shaped layout with 27 interactive boxes
- Animated box openings with 360-degree flip animation
- Sparkle effects when boxes are opened
- Default heart emoji display for unopened boxes
- Star message feature with special password protection

### Admin Panel
- User-friendly interface for calendar customization
- Image URL upload capability for each box
- Custom password management for both main calendar access and star message
- Real-time preview of changes
- Ability to reset configurations


#### Authentication Flow
I implemented a two-tier authentication system:
1. User account authentication
2. Calendar-specific password

This design choice allows for:
- Multiple users to have their own calendars
- Sharing calendars with specific people who know the unlock password
- Additional security layer with the star message feature

#### Technical Implementation

##### Frontend
- Pure JavaScript for DOM manipulation and animations
- CSS3 for smooth transitions and animations
- Responsive design that works across different screen sizes
- Error handling with user-friendly notifications

##### Backend
- Flask framework for robust routing and template rendering
- SQLite database for data persistence
- RESTful API endpoints for seamless frontend-backend communication
- Secure session management

## Initialize:

- Instead of using the SQLite command line, run the Python initialization script:
- `python init_db.py`

- To verify the database was created correctly, you can use SQLite command line:

- `sqlite3 project.db`

### File Structure

- `app.py`: Main application file containing routes and application logic
- `init_db.py`: Database initialization and schema creation
- `static/`
  - `home.css`: Styles for the main calendar interface
  - `admin.css`: Styles for the admin panel
  - `js/home.js`: Calendar interaction and animation logic
- `templates/`
  - `home.html`: Main calendar view template
  - `admin.html`: Admin panel template
  - `login.html`: User authentication template
  - `register.html`: User registration template

### Database Design
The application uses SQLite with three main tables:
1. `users`: Stores user account information
2. `user_settings`: Stores calendar-specific passwords
3. `calendar_boxes`: Stores image URLs and box configurations

### Future Improvements
- Support for video content in boxes
- Multiple calendar themes
- Social sharing capabilities
- Custom animation options
- Mobile app version

### Security Considerations
- All passwords are hashed before storage
- Session-based authentication
- CSRF protection
- Input validation and sanitization
- Secure password reset functionality

### Installation and Setup
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Initialize database: `python init_db.py`
4. Run the application: `flask run`

### Contributing
Feel free to submit issues and enhancement requests. For substantial changes:
1. Fork the repository
2. Create a new branch
3. Submit a pull request
