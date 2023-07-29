from app import app, bp

if __name__ == '__main__':
    app.register_blueprint(bp)
    app.run(debug=True)