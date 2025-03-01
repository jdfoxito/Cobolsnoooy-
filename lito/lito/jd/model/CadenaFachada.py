"""Fachada, patro de diseño
Funcionalidades:
- Facade es un patrón de diseño estructural que proporciona una interfaz
  simplificada (pero limitada) a un sistema complejo de clases, bibliotecas o
  _frameworks_.
- El patrón Facade disminuye la complejidad general de la aplicación, al mismo
tiempo que ayuda a mover dependencias no deseadas a un solo lugar

+------------+-------------+--------------------------------------------------+
| Fecha      | Modifier    | Descripcion                                      |
+------------+-------------+--------------------------------------------------+
| 15MAY2023  | jagonzaj    |   se crea la interfaz                            |
+------------+-------------+--------------------------------------------------+

ESTANDAR PEP8

"""

from datos import Estatisticas, Pleyades
from ayudante import Interacciones
from logicas import Listado, Providencias, Informe, Catastro, Cadena
from logicas import Declaraciones, Futuro, Elecciones, Tramites, Golden, Fotones
from datos import Consultas


class Patron:
    """
    Representa la parte principal de la Fachada para organizar.
    """
    def __init__(self, contri):
        self.uf = Interacciones.Recepcion(contri)
        self.db = Estatisticas.Analiticas(self.uf)
        self.xl = Listado.ArchivoExcel(self.db)
        self.pr = Providencias.Encontradas(self.db)
        self.pa = Informe.Revision(self.db)
        self.ca = Catastro.Tramites(self.db)
        self.m45 = Pleyades.Abayo(self.uf)
        self.iva = Cadena.Iva(self.db)
        self.decla = Declaraciones.Transpuesta(self.db)
        self.actual = Futuro.Pasado(self.db)
        self.legir = Elecciones.Periodo(self.db)
        self.opcion = Tramites.Diarios(self.db)
        self.ares = Golden.Puente(self.db)
        self.neutrones = Fotones.Reemplazantes(self.db)
        self.nupy = Consultas.Papel(self.db)
