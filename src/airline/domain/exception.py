class CpfJaCadastradoException(Exception):
    pass

class CpfInvalidoException(Exception):
    pass

class TipoCpfInvalidoException(Exception):
    pass

class PassageiroNaoEncontrado(Exception):
    pass

class ReservaNaoEncontrada(Exception):
    pass

class DespachoNaoEncontrado(Exception):
    pass

# erros dos casos de uso do Voo
class VooJaExiste(Exception):
    pass

class VooNaoEncontrado(Exception):
    pass

class AeronaveNaoEncontrada(Exception):
    pass

class AeronaveIndisponivel(Exception):
    pass

class AeronaveJaExiste(Exception):
    pass