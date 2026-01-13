# Sistema de Controle de Vendas - Farmácia de Manipulação

Sistema desktop desenvolvido em Python para gerenciamento de pedidos, orçamentos e entregas em uma farmácia de manipulação. O projeto resolveu o problema de sincronização de dados entre múltiplos computadores em uma rede local sem a necessidade de um servidor dedicado.

## 🚀 Funcionalidades

### 🛒 Controle de Vendas(V1)
- **Cadastro de Pedidos:** Interface ágil com *autocomplete* de clientes e produtos para inserção de novos orçamentos.
- **Sincronização em Rede:** Arquitetura Cliente-Servidor simplificada onde múltiplos terminais leem/escrevem no mesmo banco SQLite via mapeamento de rede.
- **Atualização em Tempo Real:** O sistema monitora alterações no banco e atualiza a tabela de vendas automaticamente a cada cinco segundos.
- **UX Otimizada:** Cores visuais para status (Orçamento/Confirmado/Cancelado) e recurso "Segurar para ver Faturamento" para privacidade no balcão.

### 💰 Módulo Financeiro (V2)
- **Gestão de Despesas:** Controle completo de contas a pagar (água, luz, fornecedores, retiradas).
- **Acesso Restrito:** O módulo de despesas é protegido por senha (padrão-1234), garantindo que apenas gerentes acessem dados sensíveis.
- **Projeção Automática de Fixas:** O sistema identifica despesas recorrentes (categoria "Fixa") e as projeta automaticamente nos meses seguintes como "A DEFINIR". Isso elimina a necessidade de lançar manualmente contas repetitivas todo mês.
- **Filtros Avançados:** Visualização de despesas filtradas por Mês e Ano.

## 🛠 Tecnologias Utilizadas
- **Linguagem:** Python
- **GUI:** Tkinter (Interface Gráfica Nativa)
- **Banco de Dados:** SQLite3
- **Compilação:** PyInstaller (para gerar executável .exe)
- **Bibliotecas:** `tkcalendar` (Datas), `Pillow` (Imagens).

## ⚙️ Como funciona a Arquitetura

O sistema foi projetado para ser "Portable" e fácil de manter.
1. O executável lê um arquivo local `caminho_db.txt`.
2. Este arquivo contém o caminho da rede (ex: `\\SERVIDOR\Sistema\vendas.db`).
3. Todos os computadores acessam esse mesmo arquivo `.db`, garantindo integridade dos dados.

## 📦 Como rodar o projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/btretto03/pharmacy-order-management
2. Instale as dependências
   ```bash
   pip install -r requirements.txt
4. Execute
   ```bash
    python planilha.py
