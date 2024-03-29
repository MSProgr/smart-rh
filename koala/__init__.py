from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_babelex import Babel
from flask_mail import Mail

import os

app = Flask(__name__)
app.config["SECRET_KEY"] = 'ec469fe94afede3381e93e36bb4e432c'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/demande_drh"
#app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://ousseynou:1994@localhost/sonatel_db"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'diengdieng941@gmail.com'
app.config['MAIL_PASSWORD'] = 'yybrulemjxrfdsiz'


db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
babel = Babel(app)
mail = Mail(app)



from koala.models import User,Parc,Offre,DemandeMobileTemp,DemandeMobilePerm,Agence,FacturationMobile
from koala.config import UserView, DemandeMobileTempView,DemandeMobilePermView,ParcView,OffreView,MyAdminIndexView,AgenceView,\
	FacturationMobileView

admin = Admin(app, name="DRH",index_view=MyAdminIndexView())


admin.add_view(UserView(User, db.session))
admin.add_view(ParcView(Parc, db.session))
admin.add_view(OffreView(Offre, db.session))
admin.add_view(DemandeMobileTempView(DemandeMobileTemp, db.session))
admin.add_view(DemandeMobilePermView(DemandeMobilePerm, db.session))
admin.add_view(FacturationMobileView(FacturationMobile, db.session))
admin.add_view(AgenceView(Agence, db.session))

path = os.path.join(os.path.dirname(__file__), 'static/fichiers/')
admin.add_view(FileAdmin(path, '/static/fichiers/', name='Fichiers'))

login_manager.login_view = 'login'
login_manager.login_message_category = "warning"

from koala import routes