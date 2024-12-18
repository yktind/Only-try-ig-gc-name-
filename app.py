from flask import Flask, render_template, request
from instagrapi import Client

app = Flask(__name__)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Name Changer</title>
</head>
<body>
    <h1>Change Instagram Group Chat Name</h1>
    <form action="/change_name" method="POST">
        <label for="username">Instagram Username:</label><br>
        <input type="text" id="username" name="username" required><br><br>

        <label for="password">Instagram Password:</label><br>
        <input type="password" id="password" name="password" required><br><br>

        <label for="thread_name">Current Group Name:</label><br>
        <input type="text" id="thread_name" name="thread_name" required><br><br>

        <label for="new_name">New Group Name:</label><br>
        <input type="text" id="new_name" name="new_name" required><br><br>

        <button type="submit">Change Name</button>
    </form>
</body>
</html>
"

# Flask Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/change_name", methods=["POST"])
def change_name():
    username = request.form.get("username")
    password = request.form.get("password")
    thread_name = request.form.get("thread_name")
    new_name = request.form.get("new_name")

    cl = Client()
    try:
        # Login to Instagram
        cl.login(username, password)

        # Fetch all threads
        threads = cl.direct_threads()
        thread_id = None

        # Find the thread by name
        for thread in threads:
            if thread.title == thread_name:
                thread_id = thread.id
                break

        if not thread_id:
            return "Group chat not found!"

        # Change group chat name
        response = cl.direct_thread_update_title(thread_id, new_name)
        if response:
            return f"Group chat name changed to: {new_name}"
        else:
            return "Failed to change group chat name."
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
    
