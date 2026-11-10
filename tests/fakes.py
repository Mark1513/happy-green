"""Double de teste; não é usado como armazenamento da aplicação."""

from happy_green.domain import Categoria, ContaFinanceira, OrcamentoMensal
from happy_green.errors import ConflictError, NotFoundError
from happy_green.ports import Carteira, RepositorioFinanceiro


class RepositorioEmMemoria(RepositorioFinanceiro):
    def __init__(self):
        self.contas = {}
        self.categorias = {}
        self.lancamentos = {}
        self.orcamentos = {}

    def carregar(self):
        contas = self.contas
        categorias = self.categorias
        lancamentos = tuple(type(x)(contas[x.conta.id], categorias[x.categoria.id],
                                    x.descricao, x.valor, x.data, x.id)
                            for x in self.lancamentos.values())
        orcamentos = tuple(OrcamentoMensal(categorias[x.categoria.id], x.mes, x.limite, x.id)
                           for x in self.orcamentos.values())
        return Carteira(tuple(contas.values()), tuple(categorias.values()), lancamentos, orcamentos)

    def salvar_conta(self, conta, *, atualizar=False):
        if atualizar and conta.id not in self.contas:
            raise NotFoundError("Conta inexistente.")
        if any(x.id != conta.id and x.nome.casefold() == conta.nome.casefold() for x in self.contas.values()):
            raise ConflictError("Nome duplicado.")
        self.contas[conta.id] = conta

    def salvar_categoria(self, categoria, *, atualizar=False):
        if atualizar and categoria.id not in self.categorias:
            raise NotFoundError("Categoria inexistente.")
        if any(x.id != categoria.id and x.nome.casefold() == categoria.nome.casefold()
               and x.tipo == categoria.tipo for x in self.categorias.values()):
            raise ConflictError("Categoria duplicada.")
        antiga = self.categorias.get(categoria.id)
        if antiga and antiga.tipo != categoria.tipo and (
            any(x.categoria.id == categoria.id for x in self.lancamentos.values())
            or any(x.categoria.id == categoria.id for x in self.orcamentos.values())
        ):
            raise ConflictError("Categoria vinculada.")
        self.categorias[categoria.id] = categoria

    def salvar_lancamento(self, item, *, atualizar=False):
        if atualizar and item.id not in self.lancamentos:
            raise NotFoundError("Lançamento inexistente.")
        self.lancamentos[item.id] = item

    def salvar_orcamento(self, item):
        existente = next((x for x in self.orcamentos.values()
                          if x.categoria.id == item.categoria.id and x.mes == item.mes), None)
        if existente:
            item = OrcamentoMensal(item.categoria, item.mes, item.limite, existente.id)
        self.orcamentos[item.id] = item

    def excluir(self, entidade, id):
        dados = getattr(self, entidade)
        if id not in dados:
            raise NotFoundError("Registro inexistente.")
        del dados[id]

    def carregar_demonstracao(self, carteira):
        if any((self.contas, self.categorias, self.lancamentos, self.orcamentos)):
            raise ConflictError("Demonstração já carregada.")
        self.contas.update((x.id, x) for x in carteira.contas)
        self.categorias.update((x.id, x) for x in carteira.categorias)
        self.lancamentos.update((x.id, x) for x in carteira.lancamentos)
        self.orcamentos.update((x.id, x) for x in carteira.orcamentos)
