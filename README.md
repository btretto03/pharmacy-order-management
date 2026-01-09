# Sistema de Controle de Vendas - Farmácia de Manipulação

Sistema desktop desenvolvido em Python para gerenciamento de pedidos, orçamentos e entregas em uma farmácia de manipulação. O projeto resolveu o problema de sincronização de dados entre múltiplos computadores em uma rede local sem a necessidade de um servidor dedicado.

## 🚀 Funcionalidades

- **Cadastro de Pedidos:** Interface ágil para inserção de novos orçamentos.
- **Sincronização em Rede:** Arquitetura Cliente-Servidor simplificada onde múltiplos terminais leem/escrevem no mesmo banco SQLite via mapeamento de rede.
- **Atualização em Tempo Real:** O sistema monitora alterações no banco e atualiza a interface automaticamente a cada cinco segundos.
- **UX Otimizada:** Navegação por teclado, cores visuais para status (Orçamento/Confirmado/Cancelado) e recurso "Segurar para ver Faturamento" para privacidade.

## 🛠 Tecnologias Utilizadas

- **Linguagem:** Python 3
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
