from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint # Import for Swagger UI

# Initialize the Flask application
app = Flask(__name__)

# Apply CORS to your app.
CORS(app)

# Hardcoded list of blog posts
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Third Post", "content": "Another interesting post content."},
    {"id": 4, "title": "Fourth Post", "content": "Yet another piece of content for a blog."},
    {"id": 5, "title": "Fifth Post", "content": "Concluding thoughts on a topic."},
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
    Sorting can be applied using 'sort' (title, content) and 'direction' (asc, desc) query parameters.
    Returns 400 Bad Request for invalid sort fields or directions.
    """
    sort_by = request.args.get('sort')
    direction = request.args.get('direction')

    current_posts = list(POSTS)

    if sort_by:
        if sort_by not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field. 'sort' must be 'title' or 'content'."}), 400

        if direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid sort direction. 'direction' must be 'asc' or 'desc'."}), 400

        reverse_sort = (direction == 'desc')
        current_posts.sort(key=lambda post: post[sort_by], reverse=reverse_sort)

    return jsonify(current_posts)

# Define the "Add" endpoint
@app.route('/posts', methods=['POST'])
def add_post():
    """
    Adds a new blog post to the list.
    Expects JSON input with 'title' and 'content'.
    Returns the new post with a generated ID and 201 Created status on success.
    Returns 400 Bad Request if 'title' or 'content' are missing.
    """
    data = request.json

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

    new_id = get_next_id()

    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201

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
    Expects JSON input with optional 'title' and 'content'.
    Returns the updated post with 200 OK status if found and updated.
    Returns 404 Not Found status if the post does not exist.
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

    if 'title' in data:
        post_found['title'] = data['title']

    if 'content' in data:
        post_found['content'] = data['content']

    return jsonify(post_found), 200

# Define the "Search" endpoint
@app.route('/posts/search', methods=['GET'])
def search_posts():
    """
    Searches for blog posts by title or content based on query parameters.
    Returns a list of matching posts. Returns an empty list if no matches.
    """
    search_title = request.args.get('title', '').lower()
    search_content = request.args.get('content', '').lower()

    results = []
    for post in POSTS:
        post_title_lower = post['title'].lower()
        post_content_lower = post['content'].lower()

        title_matches = search_title and search_title in post_title_lower
        content_matches = search_content and search_content in post_content_lower

        if title_matches or content_matches:
            results.append(post)

    return jsonify(results)

# --- Swagger UI Configuration ---
SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (e.g., http://localhost:5002/api/docs)
# API_URL should point to the JSON file that describes your API
# This file needs to be placed in a 'static' folder accessible by Flask.
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
