# JJNoFish: Personalized Content Filter

## Distinctiveness and Complexity

JJNoFish stands out as a unique and complex web application that addresses a critical need in digital content consumption - helping users manage and modify content that may trigger negative emotional responses. Unlike traditional content filters that focus on profanity or explicit content, JJNoFish takes a personalized approach by allowing users to define their own trigger words and replacement terms.

The project's distinctiveness is evident in several aspects:

1. **Unique Problem Space**: While CS50's other projects focus on social networks, e-commerce, or information management, JJNoFish addresses the psychological aspect of content consumption. It's designed to help users overcome personal triggers and phobias, making it fundamentally different from typical web applications.

2. **Customization Focus**: Unlike standard content filters with predefined rules, JJNoFish empowers users with unlimited customization options. Each user can create their own dictionary of replacement terms, making the application highly personal and adaptable.

3. **Document Processing**: The project goes beyond simple web-based text manipulation by handling actual document files. It processes .docx files while maintaining their structure and formatting, which is significantly more complex than handling plain text.

The complexity of the project is demonstrated through:

1. **Technical Implementation**:
   - Complex document processing using python-docx library
   - Asynchronous file uploads and previews using AJAX
   - Real-time document preview functionality
   - Dynamic word pair management system
   - Secure file handling and storage

2. **Data Management**:
   - Sophisticated database schema for managing user data, documents, and word pairs
   - Efficient storage and retrieval of both original and modified documents
   - JSON serialization of word pairs for flexible storage

3. **User Interface**:
   - Dynamic addition and removal of word replacement pairs
   - Split-screen preview showing original and modified content
   - Responsive design for different screen sizes
   - Real-time feedback and error handling

## File Structure and Contents

### Backend Files
- `project.py`: Core functionality implementation
  - Document processing logic
  - Word replacement algorithms
  - File handling and storage management
  - Export functionality

- `views.py`: Django views implementation
  - User authentication views
  - Main application views
  - Document upload and processing handlers
  - History view implementation

- `models.py`: Database models
  - User model with authentication
  - UploadedDocument model for file management
  - Relationship handling between users and documents

### Frontend Files
- `templates/capstone/jj_no_fish.html`: Main application interface
  - Document upload interface
  - Word replacement form
  - Preview panels
  - Export controls

- `static/capstone/index.js`: Frontend functionality
  - Dynamic form handling
  - AJAX requests
  - Preview updates
  - User interface interactions

- `static/capstone/styles.css`: Application styling

### Storage Directories
- `Documents/`: Temporary storage for uploaded files
- `modified_documents/`: Storage for processed documents

## Installation and Setup

1. Clone the repository to your local machine
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```
6. Access the application at `http://localhost:8000`

## Additional Notes

- The application requires Python 3.8 or higher
- Document processing is currently limited to .docx files
- The application uses local storage for documents; in a production environment, cloud storage would be recommended
- Users should have appropriate file permissions in the Documents and modified_documents directories

## Future Enhancements

- Support for additional file formats (PDF, TXT, etc.)
- Cloud storage integration
- Browser extension for real-time web content filtering
- Batch processing of multiple documents
- Advanced preview options with formatting preservation
- Collaborative filtering rules sharing

## Acknowledgements

This project was created as part of the CS50 Web Programming with Python and JavaScript course. Special thanks to the CS50 team for providing the knowledge and infrastructure necessary to build this application.
