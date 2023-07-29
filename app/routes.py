from . import bp, db
from .models import Users, Backlog, Game
from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

@bp.route('/')
@bp.route('/home')
def home ():
    return render_template('home.html')

@bp.route('/credit_faq')
def credit_faq():
    return render_template('credit_faq.html')

@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        username_exists = Users.query.filter_by(username=username).first()
        email_exists = Users.query.filter_by(email=email).first()
        
        if username_exists:
            flash ('Username already exists!', category='error')
        elif email_exists:
            flash ('Email already exists!', category='error')
        elif password != confirm_password:
            flash ('Passwords do not match!', category='error')
        elif len(username) < 3:
            flash ('Username is too short!', category='error')
        elif len(password) < 6:
            flash ('Password is too short!', category='error')
        elif len(email) < 6:
            flash ('Invalid email address!', category='error')
        else:
            new_user = Users(username=username, email=email, password=generate_password_hash(password, method="pbkdf2"))
            db.session.add(new_user)
            db.session.commit()
            flash ('User created successfully!')
            return redirect(url_for('routes.login'))
    return render_template('register.html')

@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash ('Login successful!')
                return redirect(url_for('routes.dashboard'))
            else:
                flash ('Incorrect password!', category='error')
        else:
            flash ('Username does not exist!', category='error')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@bp.route('/dashboard')
@login_required
def dashboard():
    cleared_backlogs = Backlog.query.filter_by(user_id=current_user.id, is_cleared=True).count()
    
    total_games_query = db.session.execute(
        "SELECT COUNT(*) AS total_games "
        "FROM game "
        "WHERE backlog_id IN ("
        "  SELECT id "
        "  FROM backlog "
        "  WHERE user_id = :user_id"
        ")",
        {"user_id": current_user.id})
    total_games = total_games_query.fetchone()["total_games"]
    
    total_howlongtobeat_query = db.session.execute(
        "SELECT SUM(howlongtobeat) AS total_howlongtobeat "
        "FROM game "
        "WHERE backlog_id IN ("
        "  SELECT id "
        "  FROM backlog "
        "  WHERE user_id = :user_id"
        ")",
        {"user_id": current_user.id})
    howlongtobeat_total = total_howlongtobeat_query.fetchone()["total_howlongtobeat"]
    
    total_cash_spent_query = db.session.execute(
        "SELECT COALESCE(SUM(purchase_price), 0) AS total_purchase_price "
        "FROM game "
        "WHERE backlog_id IN ("
        "  SELECT id "
        "  FROM backlog "
        "  WHERE user_id = :user_id"
        ")",
        {"user_id": current_user.id})
    total_cash_spent = total_cash_spent_query.fetchone()["total_purchase_price"]      
    
    return render_template('dashboard.html', cleared_backlogs=cleared_backlogs, total_games=total_games, howlongtobeat_total=howlongtobeat_total,total_cash_spent=total_cash_spent)

@bp.route('/backlogs', methods=['GET'])
@login_required
def backlogs_main():
    backlogs = Backlog.query.filter_by(user_id=current_user.id, is_cleared=False).all()
    cleared_backlogs = Backlog.query.filter_by(user_id=current_user.id, is_cleared=True).all()
    
    return render_template('backlogs.html', backlogs=backlogs, cleared_backlogs=cleared_backlogs)

@bp.route('/backlogs/add', methods=['GET', 'POST'])
@login_required
def add_backlog():
    if request.method == 'POST':
        name = request.form.get('name')
        date_created = request.form.get('date_created')
        is_cleared = request.form.get('is_cleared') == 'yes'
        user_id = current_user.id

        new_backlog = Backlog(name=name, date_created=date_created, is_cleared=is_cleared, user_id=user_id)
        db.session.add(new_backlog)
        db.session.commit()

        return redirect(url_for('routes.backlogs_main'))

    return render_template('add_backlog.html')

@bp.route('/backlogs/view/<int:backlog_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def view_backlog(backlog_id):
    backlog = Backlog.query.get_or_404(backlog_id)
    games_in_progress = Game.query.filter_by(backlog_id=backlog_id, is_beat=False).all()
    completed_games = Game.query.filter_by(backlog_id=backlog_id, is_beat=True).all()

    if request.method == 'POST':
        if request.form.get('_method') == 'PUT':
            name = request.form.get('name')
            is_cleared = request.form.get('is_cleared') == 'yes'
            user_id = current_user.id

            backlog.name = name
            backlog.is_cleared = is_cleared

            db.session.commit()

            return redirect(url_for('routes.backlogs_main'))
        
        elif request.form.get('_method') == 'DELETE':
            db.session.delete(backlog)
            db.session.commit()
            
            return redirect(url_for('routes.backlogs_main'))
    
    if request.method == 'GET':
        games = Game.query.filter_by(backlog_id=backlog.id).all()
    
    return render_template('view_backlog.html', backlog=backlog, games_in_progress=games_in_progress, completed_games=completed_games)

@bp.route('/backlogs/view/<int:backlog_id>/addgames', methods=['POST', 'GET'])
@login_required
def add_games(backlog_id):
    backlog = Backlog.query.get_or_404(backlog_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        platform = request.form.get('platform')
        howlongtobeat = request.form.get('howlongtobeat')
        purchase_price = request.form.get('purchase_price')
        is_beat = request.form.get('is_beat') == 'yes'
        backlog_id = backlog.id 
        
        if not howlongtobeat.isdigit():
            flash('Please enter a whole number!')
        else:
            game_exists = Game.query.filter_by(title=title).first()
            
            if game_exists:
                flash ('Game is already in this backlog!')
            else:
                new_game = Game(title=title, platform=platform, howlongtobeat=howlongtobeat, 
                                purchase_price=purchase_price, is_beat=is_beat, backlog_id=backlog_id)
                db.session.add(new_game)
                db.session.commit()
                return redirect(url_for('routes.view_backlog', backlog_id=backlog_id))        
    
    return render_template('add_games.html', backlog=backlog, backlog_id=backlog_id)

@bp.route('/backlogs/view/<int:backlog_id>/<int:game_id>', methods=['POST', 'DELETE', 'GET'])
@login_required
def edit_games(backlog_id, game_id):
    game = Game.query.get_or_404(game_id)
    backlog = Backlog.query.get_or_404(backlog_id)
    
    if request.method == 'POST':
        if request.form.get('_method') == 'PUT':
            title = request.form.get('title')
            platform = request.form.get('platform')
            howlongtobeat = request.form.get('howlongtobeat')
            purchase_price = request.form.get('purchase_price')
            is_beat = request.form.get('is_beat') == 'yes'
            backlog_id = backlog.id
            
            game.title = title
            game.platform = platform
            game.howlongtobeat = howlongtobeat
            game.purchase_price = purchase_price
            game.is_beat = is_beat

            db.session.commit()

            return redirect(url_for('routes.view_backlog', backlog_id=backlog_id))
        
        elif request.form.get('_method') == 'DELETE':
            db.session.delete(game)
            db.session.commit()
            
            return redirect(url_for('routes.view_backlog', backlog_id=backlog_id))
    
    return render_template('edit_games.html', backlog_id=backlog_id, game_id=game_id, game=game)