from flask import Flask, jsonify, request # Import request to access incoming request data
from flask_cors import CORS # Import CORS to handle cross-origin requests

# Initialize the Flask application
app = Flask(__name__)

# Apply CORS to your app.
# This allows your frontend (e.g., running on a different port or domain)
# to make requests to this backend API.
CORS(app) # You can configure this more specifically if needed (e.g., origins=['http://localhost:3000'])

# Hardcoded list of blog posts
# This acts as our in-memory "database" for now
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Third Post", "content": "Another interesting post content."},
    {"id": 4, "title": "Fourth Post", "content": "Yet another piece of content for a blog."},
    {"id": 5, "title": "Fifth Post", "content": "Concluding thoughts on a topic."},
]

# Helper function to generate a new unique ID for posts
# It finds the maximum ID currently in the POSTS list and adds 1.
def get_next_id():
    """Generates a new unique integer ID for a new blog post."""
    if not POSTS:
        return 1 # If the list is empty, start with ID 1
    return max(post['id'] for post in POSTS) + 1

# Define the "List" endpoint (existing)
# This route will handle GET requests to '/posts'
@app.route('/posts', methods=['GET'])
def get_posts():
    """
    Returns a list of all blog posts.
    """
    return jsonify(POSTS) # jsonify converts the Python list of dictionaries into a JSON array

# Define the "Add" endpoint
# This route will handle POST requests to '/posts'
@app.route('/posts', methods=['POST'])
def add_post():
    """
    Adds a new blog post to the list.
    Expects JSON input with 'title' and 'content'.
    Returns the new post with a generated ID and 201 Created status on success.
    Returns 400 Bad Request if 'title' or 'content' are missing.
    """
    # Get JSON data from the request body
    data = request.json

    # Validate input: Check if 'title' and 'content' are provided
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    title = data.get('title')
    content = data.get('content')

    missing_fields = []
    if not title:
        missing_fields.append('title')
    if not content:
        missing_fields.append('content')

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}."}), 400

    # Generate a unique ID for the new post
    new_id = get_next_id()

    # Create the new post dictionary
    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    # Add the new post to our hardcoded list
    POSTS.append(new_post)

    # Return the newly created post with a 201 Created status code
    return jsonify(new_post), 201


# This block ensures the Flask development server runs only when
# the script is executed directly (not when imported as a module).
if __name__ == '__main__':
    # Run the Flask app in debug mode.
    # debug=True allows for automatic reloading on code changes
    # and provides a debugger for easier development.
    # Note: Flask's default port is 5000. If 5002 is required by your setup,
    # specify it: app.run(debug=True, port=5002)
    app.run(debug=True, port=5002) # Using port 5002 as per your previous interactions
