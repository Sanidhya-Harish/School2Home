def select_child(page, child_name):
    print(f"\nSelecting child: {child_name}")

    page.goto("https://gis.pupilpod.net/modules/Dashboard/parentDashboard.php")
    page.wait_for_load_state("networkidle")

    page.wait_for_selector("#myDropDown", timeout=15000)

    options = page.locator("#myDropDown option").all_text_contents()
    print("Available children:", options)

    page.select_option("#myDropDown", label=child_name)

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    print(f"Selected: {child_name}")