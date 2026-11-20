# Meu E-commerce Flask — Projeto Final CS50

Este repositório contém o desenvolvimento do meu projeto final para a certificação do **CS50 (Harvard)**. Trata-se de uma aplicação de e-commerce completa construída em Python com o framework Flask, utilizando SQLite como banco de dados.

## Objetivo do Repositório (Foco em Portfólio)
Mais do que apenas entregar os requisitos acadêmicos do curso, utilizei este projeto para demonstrar minha evolução técnica em **Engenharia de Software**. O histórico de commits deste repositório documenta a transição de uma arquitetura monolítica tradicional para uma **Arquitetura em Camadas (Controllers, Services e Repositories)** limpa, segura e modular, aplicando padrões de mercado.

## Decisões Técnicas e Evolução da Arquitetura

### ✅ Etapa 1: Monólito Funcional (Entrega Oficial CS50x)
Para a entrega inicial, construí uma base monolítica funcional priorizando a entrega de valor ponta a ponta e a integridade relacional:
- **Centralização e Fluxo:** Gerenciamento de rotas HTTP, autenticação com hashing de senhas (`Werkzeug`) e controle de sessões no servidor (`Flask-Session`).
- **Persistência Relacional:** Modelagem normalizada em **SQLite** (`ecommerce.db`), garantindo o relacionamento correto entre usuários, catálogo, itens do carrinho e histórico de pedidos, com baixa dinâmica de estoque.
- **Reutilização (DRY) e Componentização (Jinja2):** Criação de decoradores isolados (`@login_required` em `helpers.py`) e herança de templates (`layout.html`) com Bootstrap 5, rodapé responsivo e contador dinâmico de itens no carrinho via `context_processor`.

### ✅ Etapa 2: Arquitetura em Camadas & Princípios SOLID (Concluída)
O código foi totalmente refatorado para eliminar consultas SQL das rotas e separar responsabilidades:
- [x] **S (Single Responsibility Principle):** Separação estrita entre apresentação (`app.py`), regras de negócio (`services.py`) e acesso a dados (`repositories.py`).
- [x] **D (Dependency Inversion Principle):** Injeção de dependências (`db` nos repositórios e repositórios nos serviços via `__init__`), desacoplando a regra de negócio da tecnologia de banco de dados.
- [x] **Repository Pattern:** Isolamento de todas as queries SQL em `ProductRepository`, `CartRepository`, `OrderRepository` e `UserRepository`.

### ✅ Etapa 3: Resiliência e Idempotência no Checkout (Concluída)
Para blindar o fluxo financeiro contra falhas de rede ou cliques duplos acidentais no botão de finalização de compra:
- [x] Geração de tokens exclusivos universais (**UUID v4**) a cada sessão de checkout (`GET /checkout`).
- [x] Interceptação de requisições duplicadas com o mesmo `idempotency_token` na camada `CheckoutService` com restrição `UNIQUE` no banco de dados, impedindo pedidos duplicados.

### 🚧 Próximas Decisões: Novas Funcionalidades de Negócio e IA (Planejada)
Para expandir o ecossistema da loja e automatizar a gestão do catálogo:
- [ ] **Migração para PostgreSQL:** Adaptação da camada de persistência para banco de dados em produção.
- [ ] **Painel Administrativo (RBAC):** Criação de área restrita para administradores gerenciarem produtos, preços e reposição de estoque.
- [ ] **Busca Dinâmica:** Implementação de barra de pesquisa com filtros otimizados no catálogo.
- [ ] **Categorização Inteligente com IA:** Integração com API de Inteligência Artificial para sugerir e atribuir categorias automaticamente no cadastro de novos produtos.

## 📁 Estrutura do Projeto

```text
├── project/             # Diretório principal da aplicação
│   ├── app.py           # Camada de Apresentação (Rotas Flask e Context Processors)
│   ├── services.py      # Camada de Negócio (Regras, validações e idempotência)
│   ├── repositories.py  # Camada de Dados (Consultas SQL isoladas)
│   ├── helpers.py       # Decoradores e funções auxiliares (@login_required)
│   ├── templates/       # Páginas HTML (Renderizadas via Jinja2)
│   ├── static/          # Arquivos estáticos (CSS, JS, Imagens)
│   └── ecommerce.db     # Banco de dados relacional SQLite
├── .gitattributes       # Configurações de atributos do Git
├── .gitignore           # Arquivos e pastas ignorados no versionamento
├── LICENSE              # Termos da Licença MIT
├── requirements.txt     # Dependências do projeto Python
└── README.md            # Documentação do sistema
```

## Rotas da Aplicação

### Autenticação

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET/POST` | `/register` | Criação de novas contas de usuários. |
| `GET/POST` | `/login` | Autenticação de usuários com criação de sessão segura. |
| `GET` | `/logout` | Encerramento da sessão ativa do usuário. |

### Catálogo e Carrinho

| Método | Rota | Descrição | Regra Especial |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Vitrine principal com produtos em destaque. | Acesso público |
| `GET` | `/products` | Listagem completa do catálogo de produtos. | Acesso público |
| `GET` | `/product?id=<id>` | Detalhes de um produto específico e estoque disponível. | Acesso público |
| `GET` | `/cart` | Visualização dos itens adicionados ao carrinho. | Requer login |
| `POST` | `/add_to_cart` | Adiciona itens ao carrinho e reserva estoque. | Requer login |
| `POST` | `/remove_from_cart` | Remove unidades do carrinho e devolve ao estoque. | Requer login |

### Checkout e Resiliência

| Método | Rota | Descrição | Regra Especial |
| :--- | :--- | :--- | :--- |
| `GET` | `/checkout` | Exibição do resumo do pedido e geração do Token UUID. | Requer login |
| `POST` | `/checkout` | Processamento do pedido, criação de itens e limpeza do carrinho. | **Requer Token UUID (Idempotência)** |
| `GET` | `/orders` | Histórico de compras concluídas pelo usuário logado. | Requer login |


## Tecnologias Utilizadas
- **Python 3** (Lógica do backend e arquitetura em camadas)
- **Flask** (Framework Web, gerenciamento de sessões e context processors)
- **CS50 SQL Library** (Interface de comunicação parametrizada com o banco)
- **SQLite** (Persistência de dados relacional local)
- **Jinja2 / HTML5 / CSS3 / Bootstrap 5 & JavaScript** (Interface responsiva)
- **UUID (v4)** (Geração de tokens de idempotência no checkout)


## Como Executar o Projeto

### Pré-requisitos
* Python 3.10 ou superior instalado.
* Gerenciador de pacotes `pip`.

### Passo a Passo para Configuração Local

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/lucianoalencastro/meu_ecommerce_flask.git
   cd meu_ecommerce_flask
   ```

2. **Crie e ative um ambiente virtual (venv):**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências necessárias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor a partir do diretório do projeto:**
   ```bash
   cd project
   flask run
   ```

Abra o seu navegador e acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)


## ⚖️ Licença
Este projeto está licenciado sob a **MIT License** — sinta-se à vontade para estudar, clonar e utilizar o código conforme as diretrizes da licença.