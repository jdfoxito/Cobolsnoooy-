import os
import pandas as tired
from datetime import datetime
import sys,numpy
from pathlib import Path
# sys.path.append(str(Path(__file__).parent.parent))
from datos import Consultas
from model import CadenaFachada
from datos import Consultas

from werkzeug.security import generate_password_hash,check_password_hash

class Proteccionado():
    def __init__(self, db) -> None:
        self.db = db
        self.cn = Consultas.Papel(db)    
        self.usuario_resetear = ''
        self.usuarios_consultar = ''
        self.perfil_origen = ''
        self.tabla = 'dev_usuario_cad_iva_term'
        self.perfil_destino = ''

    def get_usuarios(self):
        df = self.db.get_vector(f"select *from public.{self.tabla}")        
        print(f"   {self.db.uf.GREEN} TABLA:  {self.db.uf.RESET}  {self.db.uf.MAGENTA} {self.tabla}  {self.db.uf.RESET}")        
        df["password"] = df["password"].apply(lambda x : generate_password_hash(x,method="scrypt"))
        print(df)
        #df.to_excel(r"D:\SRI\Soluciones\devoluciones\insumos\usuario_15sept_GC.xlsx")
        print(df["password"] )

    def get_usuario_unico_pass(self):
        print(f"   {self.db.uf.GREEN} USUARIO:  {self.db.uf.RESET}  {self.db.uf.MAGENTA} {self.usuario_resetear}  {self.db.uf.RESET}")                
        passnueva = generate_password_hash(self.usuario_resetear, method="scrypt") 
        
        self.db.get_actualizar(f"""UPDATE public.dev_usuario_cad_iva 
                                    set password = '{passnueva}'
                                  where username = '{self.usuario_resetear}'; """)
        
        return   passnueva

    def get_consultados(self):
        
        df = self.db.get_vector(f""" select *from public.dev_usuario_cad_iva  where username in ('{self.usuarios_consultar}');  """)
        
        return df


    def get_analista_de_supervisor(self):
        print("\n")
        df = self.db.get_vector(f""" select *from public.dev_usuario_cad_iva  where username in ('{self.usuarios_consultar}') and perfil = '{self.perfil_origen}';  """)
        print(f" {self.db.uf.GREEN} '{self.perfil_origen}' {df} {self.db.uf.RESET}")

        nuevo_id = self.db.get_scalar("select max(id)+1  from public.dev_usuario_cad_iva  ")     

        df_analista = df.copy()
        df_analista["id"] = nuevo_id
        match self.perfil_destino:
            case 'Analista':
                            df_analista.perfil = 'Analista'
                            df_analista.nombre = df_analista.nombre + '(A)' 
                            df_analista.username = df_analista.username + '_A'

            case 'Supervisor':
                            df_analista.perfil = 'Supervisor'
                            df_analista.nombre = df_analista.nombre + '(S)' 
                            df_analista.username = df_analista.username + '_S'
              
        
        print(f" {self.db.uf.BLUE} {self.perfil_destino} NUEVO \n {self.db.uf.RESET}  {self.db.uf.MAGENTA} {df_analista}  {self.db.uf.RESET}")
        
        self.db.guardar_dataframe_pg(df_analista, "dev_usuario_cad_iva", "public" )
        
        print(f"Guardado Perfil  {self.perfil_destino} ")
        return 1


        #return generate_password_hash(self.usuario_resetear, method="sha256")  
params =  {}
params["usuario"] = "testing"
#NARPI
params["param1"] = "0992247932001"  
params["param2"] = "2022-04-01" #"2022-04-01"
params["param3"] = "2022-12-31"

params["param4"] = "F"
params["param5"] =  "123"
estacion = CadenaFachada.Patron(params) 
nupy =  Proteccionado(estacion.db)    

opcion = ""

a="""
lista_usuarios = ['YCJM010306','KAMF311215', 'VESP230318','KAMF311215','MPIF200417']
nupy.usuarios_consultar = ','.join(lista_usuarios)
for ux in lista_usuarios:
    nupy.usuario_resetear = ux
    print(f" usuario {ux} nuevo password  {nupy.get_usuario_unico_pass()}")
    


lista_usuarios = 'JEEO060814'
nupy.perfil_origen ='Administrador'
nupy.usuarios_consultar = lista_usuarios

perfiles_nuevos = ['Analista','Supervisor']

for perfil_nuevo in perfiles_nuevos:
    nupy.perfil_destino = perfil_nuevo
    df_usuarios = nupy.get_analista_de_supervisor()    

"""
#print(df_usuarios)

#nupy.tabla = 'dev_usuario_cad_iva_term'
#nupy.get_usuarios()

nupy.usuario_resetear = 'AHGP060213'
nupy.get_usuario_unico_pass()
