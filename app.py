import os
import time
from flask import Flask, request, redirect, url_for, flash, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.secret_key = "your_secret_key"

# Ensure upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def instagram_login(username, password):
    """Logs into Instagram using Selenium"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without opening a browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    try:
        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        user_input.send_keys(username)
        pass_input.send_keys(password)
        login_button.click()
        time.sleep(5)

        if "challenge" in driver.current_url:
            flash("Instagram login requires verification. Please log in manually first.", "danger")
            driver.quit()
            return None

        return driver
    except Exception as e:
        flash(f"Login error: {e}", "danger")
        driver.quit()
        return None


def send_message(driver, thread_id, message, delay):
    """Sends a message to a specific Instagram thread"""
    try:
        driver.get(f"https://www.instagram.com/direct/t/{thread_id}/")
        time.sleep(5)

        message_box = driver.find_element(By.XPATH, "//textarea[contains(@placeholder, 'Message...')]")
        message_box.send_keys(message)
        time.sleep(delay)
        message_box.send_keys(Keys.RETURN)
        flash("Message sent successfully!", "success")
    except Exception as e:
        flash(f"Error sending message: {e}", "danger")
    finally:
        driver.quit()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        thread_id = request.form["thread_id"]
        delay = int(request.form["delay"])

        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            flash("No file selected!", "danger")
            return redirect(url_for("index"))

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
        uploaded_file.save(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            message = f.read().strip()

        driver = instagram_login(username, password)
        if driver:
            send_message(driver, thread_id, message, delay)

        return redirect(url_for("index"))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Auto Messenger</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h2 class="text-center">Instagram Auto Messenger</h2>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="mt-3">
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <form action="/" method="POST" enctype="multipart/form-data">
                <div class="mb-3">
                    <label class="form-label">Instagram Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Instagram Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Target Thread ID</label>
                    <input type="text" name="thread_id" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Message File (TXT)</label>
                    <input type="file" name="file" class="form-control" accept=".txt" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Delay (seconds)</label>
                    <input type="number" name="delay" class="form-control" min="1" value="3" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Send Message</button>
            </form>
        </div>
    </body>
    </html>
    """)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
    
