from flask import render_template, request, jsonify

from app.main import main

# @main.app_errorhandler(403)
# # def forbidden(e):
# #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
# #         response = jsonify({'error': 'forbidden'})
# #         response.status_code = 403
# #         return response
# #     return render_template("main/404.html"), 403

@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Not Found Page'})
        response.status_code = 404
        return response
    return render_template("main/404.html"), 404

@main.app_errorhandler(500)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Internal Server Error'})
        response.status_code = 500
        return response
    return render_template("main/500.html"), 500
