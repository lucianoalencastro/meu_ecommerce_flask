# 🛒 Meu E-commerce Flask — Projeto Final CS50

Este repositório contém o desenvolvimento do meu projeto final para a certificação do **CS50 (Harvard)**. Trata-se de uma aplicação de e-commerce completa construída em Python com o framework Flask, utilizando SQLite como banco de dados.

## 🎯 Objetivo do Repositório (Foco em Portfólio)
Mais do que apenas entregar os requisitos acadêmicos do curso, utilizei este projeto para demonstrar minha evolução técnica em **Engenharia de Software**. O histórico de commits deste repositório documenta a transição de uma arquitetura monolítica tradicional e acoplada para um design limpo, seguro e modular, aplicando padrões de mercado.

---

## 🏗️ Evolução da Arquitetura

### 🧬 Fase 1: O "Código Legado" (Monólito Tradicional)
Inicialmente, o projeto concentrava toda a sua lógica de funcionamento dentro do arquivo principal `app.py`. As rotas da web eram responsáveis por:
- Capturar requisições HTTP.
- Executar queries diretas de banco de dados (`INSERT`, `UPDATE`, `DELETE`).
- Validar regras de negócio críticas (como checagem e subtração de estoque de produtos).

*Embora funcional, essa abordagem violava princípios de design de código, dificultando a manutenção e a criação de testes automatizados.*

### 🛠️ Fase 2: Refatoração com Princípios SOLID
Para profissionalizar o projeto, separei as responsabilidades do sistema aplicando conceitos do **SOLID**:
- **S (Single Responsibility Principle):** O arquivo `app.py` passou a atuar estritamente como a *Camada de Apresentação* (gerenciando rotas e renderizando templates). Toda a lógica pesada de estoque e carrinho foi movida para classes especialistas em um novo arquivo: `services.py` (*Camada de Negócio*).
- **D (Dependency Inversion Principle):** As classes de serviço não criam ou importam diretamente o banco de dados. A conexão do banco é **injetada** dinamicamente através do construtor (`__init__`). Isso permite alterar a tecnologia do banco (ex: migrar de SQLite para PostgreSQL ou MySQL) alterando apenas 3 linhas no arquivo principal, sem tocar na regra de negócios.

### 🔒 Fase 3: Introdução de Idempotência com UUID
Em sistemas de e-commerce reais, cliques duplos acidentais no botão de compra podem gerar cobranças duplicadas ou falhas de estoque. 
- Implementei um mecanismo de **Idempotência** no fluxo de checkout.
- Cada tentativa de compra gera um token exclusivo universal (**UUID v4**).
- A camada de serviço intercepta requisições repetidas com o mesmo token, bloqueando processamentos duplicados e garantindo a segurança financeira da operação.

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
Este projeto está licensed sob a **MIT License** — sinta-se à vontade para estudar, clonar e utilizar o código conforme as diretrizes da licença.
