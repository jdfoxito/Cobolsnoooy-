'''
+-------------------+--------------------------------------------+
| Sector Publico    |  Para desarrollo de sector public          |
|                   |                                            |
+-------------------+--------------------------------------------+
| Agosto 2023       |V1                                          |
+--------------------+--+----------------------------------------+
| jagonzaj  19_AB_24 |  se divide para mejor mantenimiento       |
|                    |                                           |
+--------------------+--+----------------------------------------+
'''

from flask import Blueprint, render_template
from flask_login import login_required, current_user

sector_publico_scope = Blueprint('sector',
                                 __name__,
                                 template_folder='templates',
                                 static_folder='static')


@sector_publico_scope.route('/papeles/publico')
@login_required
def sectorpublico():
    '''para sector publico'''
    from datetime import datetime, timedelta
    usuario = current_user.username
    formato_fecha = '%Y-%m'
    # 1 desde
    hace5 = str((datetime.now() - timedelta(days=30*12*6)).strftime(formato_fecha))   
    mesanterior = str((datetime.now() - timedelta(days=60)).strftime(formato_fecha))
    # 2 hasta
    mesactual = str((datetime.now()).strftime(formato_fecha))
    intervalos = {"usuario": usuario,
                  "hace5": hace5,
                  "mesanterior": mesanterior,
                  "mesactual": mesactual}
    return render_template('papeles/sector-publico.html',
                           intervalos=intervalos)
