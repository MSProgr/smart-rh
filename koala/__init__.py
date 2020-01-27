from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from flask_babelex import Babel
from flask_mail import Mail

app = Flask(__name__)
app.config["SECRET_KEY"] = 'ec469fe94afede3381e93e36bb4e432c'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/demande_drh"
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



from koala.models import User,Parc,Offre,DemandeMobileTemp,DemandeMobilePerm
from koala.config import UserView, DemandeMobileTempView,DemandeMobilePermView,ParcView,OffreView,MyAdminIndexView

admin = Admin(app, name="Lgne d'exploitation",index_view=MyAdminIndexView())



admin.add_view(UserView(User, db.session))
admin.add_view(ParcView(Parc, db.session))
admin.add_view(OffreView(Offre, db.session))
admin.add_view(DemandeMobileTempView(DemandeMobileTemp, db.session))
admin.add_view(DemandeMobilePermView(DemandeMobilePerm, db.session))

login_manager.login_view = 'login'
login_manager.login_message_category = "warning"

from koala import routes
