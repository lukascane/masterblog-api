from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import datetime # Import datetime module for date handling

# Initialize the Flask application
app = Flask(__name__)

# Apply CORS to your app.
CORS(app)

# Helper to convert a post (which might have datetime objects) to a JSON-serializable dict
def serialize_post(post):
    """
    Converts a post dictionary to a JSON-serializable format.
    Ensures 'date' is formatted as 'YYYY-MM-DD' string.
    """
    serialized = post.copy()
    if 'date' in serialized and isinstance(serialized['date'], datetime.date):
        serialized['date'] = serialized['date'].strftime('%Y-%m-%d')
    return serialized

# Helper to parse date string to datetime.date object
def parse_date_string(date_str):
    """
    Parses a date string in 'YYYY-MM-DD' format into a datetime.date object.
    Returns None if the format is invalid.
    """
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

# Hardcoded list of blog posts
# Updated to include 'author' and 'date' fields, with 'date' stored as datetime.date objects internally
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post.", "author": "John Doe", "date": datetime.date(2023, 6, 7)},
    {"id": 2, "title": "Second Post", "content": "This is the second post.", "author": "Jane Smith", "date": datetime.date(2023, 6, 8)},
    {"id": 3, "title": "Third Post", "content": "Another interesting post content.", "author": "John Doe", "date": datetime.date(2023, 6, 9)},
    {"id": 4, "title": "Fourth Post", "content": "Yet another piece of content for a blog.", "author": "Alice Brown", "date": datetime.date(2023, 6, 10)},
    {"id": 5, "title": "Fifth Post", "content": "Concluding thoughts on a topic.", "author": "Jane Smith", "date": datetime.date(2023, 6, 11)},
]

# Helper function to generate a new unique ID for posts
def get_next_id():
    """Generates a new unique integer ID for a new blog post."""
    if not POSTS:
        return 1
    return max(post['id'] for post in POSTS) + 1

# Define the "List" endpoint
@app.route('/posts', methods=['GET'])
def get_posts():
    """
    Returns a list of all blog posts, with optional sorting.
    Sorting can be applied using 'sort' (title, content, author, date)
    and 'direction' (asc, desc) query parameters.
    Returns 400 Bad Request for invalid sort fields or directions.
    """
    sort_by = request.args.get('sort')
    direction = request.args.get('direction')

    current_posts = list(POSTS) # Create a copy to sort, keeping original POSTS list unchanged for default order

    if sort_by:
        # Validate sort_by field
        if sort_by not in ['title', 'content', 'author', 'date']:
            return jsonify({"error": "Invalid sort field. 'sort' must be 'title', 'content', 'author', or 'date'."}), 400

        # Validate direction
        if direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid sort direction. 'direction' must be 'asc' or 'desc'."}), 400

        reverse_sort = (direction == 'desc')

        # Sort based on the specified field
        if sort_by == 'date':
            # Sort by actual date objects for chronological order
            current_posts.sort(key=lambda post: post['date'], reverse=reverse_sort)
        else:
            # Sort by other fields (title, content, author)
            current_posts.sort(key=lambda post: post[sort_by], reverse=reverse_sort)

    # Serialize posts before jsonify to ensure date is in YYYY-MM-DD string format
    return jsonify([serialize_post(post) for post in current_posts])

# Define the "Add" endpoint
@app.route('/posts', methods=['POST'])
def add_post():
    """
    Adds a new blog post to the list.
    Expects JSON input with 'title', 'content', 'author', and 'date'.
    Returns the new post with a generated ID and 201 Created status on success.
    Returns 400 Bad Request if any required fields are missing or date format is invalid.
    """
    data = request.json

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    title = data.get('title')
    content = data.get('content')
    author = data.get('author') # New required field
    date_str = data.get('date') # New required field (string format)

    missing_fields = []
    if not title:
        missing_fields.append('title')
    if not content:
        missing_fields.append('content')
    if not author:
        missing_fields.append('author')
    if not date_str:
        missing_fields.append('date')

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}."}), 400

    # Parse date string into datetime.date object
    parsed_date = parse_date_string(date_str)
    if not parsed_date:
        return jsonify({"error": "Invalid 'date' format. Use YYYY-MM-DD."}), 400

    # Generate a unique ID for the new post
    new_id = get_next_id()

    # Create the new post dictionary, storing date as a datetime.date object
    new_post = {
        "id": new_id,
        "title": title,
        "content": content,
        "author": author,
        "date": parsed_date
    }

    # Add the new post to our hardcoded list
    POSTS.append(new_post)

    # Return the newly created post, ensuring date is serialized to string
    return jsonify(serialize_post(new_post)), 201

# Define the "Delete" endpoint
@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Deletes a blog post by its ID.
    Returns a success message with 200 OK status if found and deleted.
    Returns a 404 Not Found status if the post does not exist.
    """
    global POSTS
    original_len = len(POSTS)

    POSTS = [post for post in POSTS if post['id'] != post_id]

    if len(POSTS) < original_len:
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200
    else:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

# Define the "Update" endpoint
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates an existing blog post by its ID.
    Expects JSON input with optional 'title', 'content', 'author', and 'date'.
    Returns the updated post with 200 OK status if found and updated.
    Returns 404 Not Found status if the post does not exist.
    Returns 400 Bad Request if 'date' format is invalid.
    """
    global POSTS
    data = request.json

    post_found = None
    for post in POSTS:
        if post['id'] == post_id:
            post_found = post
            break

    if not post_found:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    # Update title if provided
    if 'title' in data:
        post_found['title'] = data['title']

    # Update content if provided
    if 'content' in data:
        post_found['content'] = data['content']

    # Update author if provided
    if 'author' in data:
        post_found['author'] = data['author']

    # Update date if provided, including format validation
    if 'date' in data:
        parsed_date = parse_date_string(data['date'])
        if not parsed_date:
            return jsonify({"error": "Invalid 'date' format. Use YYYY-MM-DD."}), 400
        post_found['date'] = parsed_date

    # Return the updated post, ensuring date is serialized to string
    return jsonify(serialize_post(post_found)), 200

# Define the "Search" endpoint
@app.route('/posts/search', methods=['GET'])
def search_posts():
    """
    Searches for blog posts by title, content, author, or date based on query parameters.
    Returns a list of matching posts. Returns an empty list if no matches.
    """
    search_title = request.args.get('title', '').lower()
    search_content = request.args.get('content', '').lower()
    search_author = request.args.get('author', '').lower() # New search parameter
    search_date_str = request.args.get('date', '') # New search parameter (string format)

    results = []
    for post in POSTS:
        post_title_lower = post['title'].lower()
        post_content_lower = post['content'].lower()
        post_author_lower = post['author'].lower() # New field to search
        post_date_str_formatted = post['date'].strftime('%Y-%m-%d') # Get string representation for comparison

        title_matches = search_title and search_title in post_title_lower
        content_matches = search_content and search_content in post_content_lower
        author_matches = search_author and search_author in post_author_lower
        # Exact match for date string
        date_matches = search_date_str and search_date_str == post_date_str_formatted

        if title_matches or content_matches or author_matches or date_matches:
            results.append(post)

    # Serialize results before jsonify
    return jsonify([serialize_post(post) for post in results])

# --- Swagger UI Configuration ---
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# This block ensures the Flask development server runs only when
# the script is executed directly (not when imported as a module).
if __name__ == '__main__':
    app.run(debug=True, port=5002)
