"""Novedades, desde Enero 2023
Funcionalidades:
  - Novedades a la base para postgres.

ESTANDAR PEP8

"""


class Novedades:
    '''clase para los mensajes de error'''
    def __init__(self, detener) -> None:
        '''constructor principal'''
        self.detener = detener
        self.razones = []

    def agregar_razones(self, razon) -> None:
        '''agregar razones'''
        if len(razon["mensaje"].strip()) > 0:
            self.razones.append(razon)
