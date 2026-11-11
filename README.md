# 🛒 Meu E-commerce Flask — Projeto Final CS50

Este repositório contém o desenvolvimento do meu projeto final para a certificação do **CS50 (Harvard)**. Trata-se de uma aplicação de e-commerce completa construída em Python com o framework Flask, utilizando SQLite como banco de dados.

## 🎯 Objetivo do Repositório (Foco em Portfólio)
Mais do que apenas entregar os requisitos acadêmicos do curso, utilizei este projeto para demonstrar minha evolução técnica em **Engenharia de Software**. O histórico de commits deste repositório documenta a transição de uma arquitetura monolítica tradicional e acoplada para um design limpo, seguro e modular, aplicando padrões de mercado.

---

## 🧠 Decisões Técnicas e Evolução da Arquitetura

### ✅ Arquitetura Atual: Monólito Funcional (Entrega Oficial CS50x)
Para a entrega inicial, optei por uma arquitetura monolítica bem estruturada, priorizando a entrega de valor ponta a ponta e a integridade relacional:
- **Centralização e Fluxo:** Gerenciamento de rotas HTTP, autenticação com hashing de senhas (`Werkzeug`) e controle de sessões no servidor (`Flask-Session`) concentrados no `app.py`.
- **Persistência Relacional:** Modelagem normalizada em **SQLite** (`schema.sql`), garantindo o relacionamento correto entre usuários, catálogo, itens do carrinho e histórico de pedidos, com baixa dinâmica de estoque no checkout.
- **Reutilização (DRY):** Criação de decoradores e funções utilitárias isoladas em `helpers.py` para proteção de rotas (`@login_required`).

### 🚧 Próximas Decisões: Refatoração SOLID (Em andamento)
Com o sistema validado, o próximo ciclo de commits foca em reduzir o acoplamento e aumentar a testabilidade do código:
- [ ] **S (Single Responsibility Principle):** Extrair as regras de negócio de estoque, carrinho e checkout do `app.py` para uma camada especialista (`services.py`), deixando o arquivo principal responsável estritamente pelo roteamento HTTP.
- [ ] **D (Dependency Inversion Principle):** Injetar a conexão do banco de dados dinamicamente nas classes de serviço (`__init__`), desacoplando a regra de negócio do SQLite.

### 🚧 Próximas Decisões: Resiliência e Idempotência (Planejada)
Para blindar o fluxo financeiro contra falhas de rede ou cliques duplos acidentais no botão de finalização de compra:
- [ ] Implementar geração de tokens exclusivos universais (**UUID v4**) para cada intenção de checkout.
- [ ] Interceptar requisições duplicadas com o mesmo token na camada de serviço, garantindo consistência transacional.

---

## 📁 Estrutura do Projeto

```text
├── project/           # Diretório principal da aplicação
│   ├── app.py         # Camada de Apresentação (Rotas Flask)
│   ├── services.py    # Camada de Negócio (Serviços e regras)
│   ├── templates/     # Páginas HTML (Renderizadas via Jinja2)
│   ├── static/        # Arquivos estáticos (CSS, JS, Imagens)
│   └── ecommerce.db   # Banco de dados relacional SQLite
├── .gitattributes     # Configurações de atributos do Git
├── .gitignore         # Arquivos e pastas ignorados no versionamento
├── LICENSE            # Termos da Licença MIT
└── README.md          # Documentação do sistema
```

---

## 🛣️ Rotas da Aplicação

### Autenticação

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET/POST` | `/register` | Criação de novas contas de usuários. |
| `GET/POST` | `/login` | Autenticação de usuários com criação de sessão segura. |
| `GET` | `/logout` | Encerramento da sessão ativa do usuário. |

### Catálogo e Compras

| Método | Rota | Descrição | Regra Especial |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Vitrine principal com listagem de produtos. | Acesso público |
| `GET` | `/produto/<int:id>` | Detalhes de um produto específico e verificação de estoque. | Acesso público |
| `GET/POST` | `/carrinho` | Adicionar, remover ou atualizar a quantidade de itens. | Requer login |

### Checkout e Resiliência

| Método | Rota | Descrição | Regra Especial |
| :--- | :--- | :--- | :--- |
| `GET` | `/checkout` | Exibição do resumo do pedido antes do fechamento. | Requer login |
| `POST` | `/checkout/process` | Processamento final do pagamento e baixa definitiva de estoque. | **Requer Token UUID (Idempotência)** |
| `GET` | `/pedidos` | Histórico de compras concluídas pelo usuário logado. | Requer login |

---

## 🚀 Tecnologias Utilizadas
- **Python** (Lógica do backend)
- **Flask** (Framework Web e gerenciamento de sessões)
- **CS50 SQL Library** (Interface de comunicação com o banco de dados)
- **SQLite** (Persistência de dados local)
- **HTML5 / CSS3 / JavaScript** (Interface do usuário)
- **UUID** (Geração de tokens de idempotência aleatórios)

---

## 🛠️ Como Executar o Projeto

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
   flask --app project/app run
   ```

Abra o seu navegador e acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚖️ Licença
Este projeto está licenciado sob a **MIT License** — sinta-se à vontade para estudar, clonar e utilizar o código conforme as diretrizes da licença.
