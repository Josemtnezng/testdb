import os
from flask_admin import Admin
from models import db, User, UserProfile, PlaylistVideo, FavoriteTheme, Unlockable
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'sandstone'
    admin = Admin(app, name='Administracion Aura', template_mode='bootstrap3')

    # Añade todos tus modelos a la interfaz de administración
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(UserProfile, db.session))
    admin.add_view(ModelView(PlaylistVideo, db.session))
    admin.add_view(ModelView(FavoriteTheme, db.session))
    admin.add_view(ModelView(Unlockable, db.session))