from config import USERNAME, PASSWORD

def login_if_required(page, context):
    login_button = page.locator("button:has-text('Login')")

    if login_button.count() > 0 and login_button.first.is_visible():
        print("Logging in...")

        login_button.first.click()
        page.wait_for_selector("#username", timeout=10000)

        page.fill("#username", USERNAME)
        page.fill("#password", PASSWORD)

        page.locator("button:has-text('Sign In')").click()
        page.wait_for_load_state("networkidle")

        print("Login successful")

        context.storage_state(path="state.json")
    else:
        print("Already logged in (session reused)")