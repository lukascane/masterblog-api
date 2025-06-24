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

# Define the "Delete" endpoint
# This route will handle DELETE requests to '/posts/<id>'
@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Deletes a blog post by its ID.
    Returns a success message with 200 OK status if found and deleted.
    Returns a 404 Not Found status if the post does not exist.
    """
    global POSTS # Declare POSTS as global to modify it within the function
    original_len = len(POSTS) # Store original length to check if a post was removed

    # Filter out the post with the given ID
    # This creates a new list excluding the post to be deleted
    POSTS = [post for post in POSTS if post['id'] != post_id]

    # Check if a post was actually removed
    if len(POSTS) < original_len:
        # Post was found and deleted
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200
    else:
        # Post with the given ID was not found
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

# Define the "Update" endpoint
# This route will handle PUT requests to '/posts/<id>'
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates an existing blog post by its ID.
    Expects JSON input with optional 'title' and 'content'.
    Returns the updated post with 200 OK status if found and updated.
    Returns 404 Not Found status if the post does not exist.
    """
    global POSTS # Declare POSTS as global to modify it within the function
    data = request.json # Get JSON data from the request body

    # Find the post by its ID
    post_found = None
    for post in POSTS:
        if post['id'] == post_id:
            post_found = post
            break

    if not post_found:
        # Post with the given ID was not found
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    # Update title if provided in the request body
    if 'title' in data:
        post_found['title'] = data['title']

    # Update content if provided in the request body
    if 'content' in data:
        post_found['content'] = data['content']

    # Return the updated post
    return jsonify(post_found), 200

# Define the "Search" endpoint
# This route handles GET requests to '/posts/search' with query parameters
@app.route('/posts/search', methods=['GET'])
def search_posts():
    """
    Searches for blog posts by title or content based on query parameters.
    Returns a list of matching posts. Returns an empty list if no matches.
    """
    search_title = request.args.get('title', '').lower() # Get 'title' query param, default to empty string, convert to lowercase
    search_content = request.args.get('content', '').lower() # Get 'content' query param, default to empty string, convert to lowercase

    results = []
    for post in POSTS:
        # Convert post title and content to lowercase for case-insensitive search
        post_title_lower = post['title'].lower()
        post_content_lower = post['content'].lower()

        # Check if title matches (if search_title is provided)
        title_matches = search_title and search_title in post_title_lower
        # Check if content matches (if search_content is provided)
        content_matches = search_content and search_content in post_content_lower

        # Add post to results if either title or content matches
        if title_matches or content_matches:
            results.append(post)

    return jsonify(results) # Return the list of matching posts


# This block ensures the Flask development server runs only when
# the script is executed directly (not when imported as a module).
if __name__ == '__main__':
    # Run the Flask app in debug mode.
    # debug=True allows for automatic reloading on code changes
    # and provides a debugger for easier development.
    # Note: Flask's default port is 5000. If 5002 is required by your setup,
    # specify it: app.run(debug=True, port=5002)
    app.run(debug=True, port=5002) # Using port 5002 as per your previous interactions
