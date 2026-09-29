class CpfJaCadastradoException(Exception):
    pass

class PassageiroNaoEncontrado(Exception):
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