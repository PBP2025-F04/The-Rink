# TODO: Fix AttributeError in events/urls.py

- [x] Remove the URL pattern for `packages/<int:package_id>/book/` pointing to non-existent `views.book_package_view`
- [x] Update the event list URL pattern to use `views.event_list` and remove the duplicate `views.event_list_view` entry
- [x] Clean up duplicate URL patterns (e.g., duplicate `get-modal` path)
- [x] Fix template syntax error in templates/main.html (unclosed {% if %} tag)
- [x] Test the Django server to ensure the error is resolved
