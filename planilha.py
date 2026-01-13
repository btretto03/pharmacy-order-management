# -------------------------------------------------------------------------
# SISTEMA DE CONTROLE DE VENDAS - Exclusiva Formulas
# -------------------------------------------------------------------------
# Autor: Bruno Antonio Tretto
# Ano: 2026
# Licença: Uso exclusivo para portfólio. Proibida cópia comercial.
#
# Descrição:
# Este software resolve o problema de concorrência de pedidos em uma rede local.
# Ele permite que múltiplos vendedores lancem pedidos simultaneamente
# em um banco de dados SQLite centralizado em rede, com atualização em tempo real na interface.
# -------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, simpledialog
import sqlite3
from datetime import datetime
from tkcalendar import Calendar
from PIL import Image, ImageTk 
import os
import sys

# --- CONFIGURAÇÕES VISUAIS
COLOR_PRIMARY = "#133A68"    # Azul Institucional
COLOR_SECONDARY = "#D4AF37"  # Dourado (Detalhes)
COLOR_BG = "#F4F7F6"         # Fundo Off-White
COLOR_TEXT = "#333333"       # Texto (preto)
COLOR_SUCCESS = "#2E7D32"    # Verde Escuro
COLOR_DANGER = "#C62828"     # Vermelho

# --- CORES DE STATUS (DESPESAS)
COLOR_BG_PENDENTE = '#FFEBEE' 
COLOR_BG_PAGO = '#C8E6C9'     
COLOR_BG_SEM_DATA = '#E0E0E0' 

FONT_MAIN = ("Helvetica", 10)
FONT_BOLD = ("Helvetica", 10, "bold")
FONT_HEADER = ("Helvetica", 16, "bold")
FONT_TITLE = ("Helvetica", 22, "bold")

def resource_path(relative_path):
    """
    Função para rodar o exe com recursos embutidos.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#DADOS ESPECÍFICOS #
CIDADES = [
    'Cidade 1', 'Cidade 2', 'Cidade 3', 'Cidade 4', 
    'Cidade 5', 'Cidade 6', 'Cidade 7', 'Outros'
]

VENDEDORES = ['Vendedora 1', 'Vendedora 2', 'Vendedora 3']

STATUS_OPCOES = ['ORÇAMENTO', 'CONFIRMADO', 'CANCELADO']
CATEGORIAS_DESPESA = ['Fixa', 'Variável', 'Pessoal/Retirada', 'Impostos', 'Fornecedor', 'Outros']
STATUS_DESPESA = ['PENDENTE', 'PAGO']

# Filtros de data
MESES_FILTRO = {
    'Todos': 'Todos', 'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
    'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
    'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
}

# Gera lista de anos automaticamente a partir de 2025 até 2037
ANOS_FILTRO = ['Todos'] + [str(ano) for ano in range(2025, 2037)]

class AppControleVendas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Vendas v1.0")
        self.root.geometry("1360x720")
        self.root.configure(bg=COLOR_BG)
        
        # Variável que armazena o faturamento mensal (Cache visual)
        self.total_cache = "R$ 0,00" 
        
        # Lógica de conexão com Banco de Dados
        self.db_name = "vendas.db" 
        
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        config_file = os.path.join(application_path, "caminho_db.txt")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    path_lido = f.read().strip()
                    if path_lido:
                        self.db_name = path_lido
            except Exception as e:
                print(f"Erro ao ler configuração: {e}")

        # Inicializa conexão
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.criar_tabela()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao conectar no Banco de Dados:\n{self.db_name}\n\nVerifique a conexão de rede.\nErro: {e}")
            self.root.destroy()
            sys.exit()

        # Listas para autocomplete em memória
        self.lista_clientes_db = []
        self.lista_produtos_db = []
        self.logo_img = None 

        # --- CONSTRUÇÃO DA INTERFACE ---
        self.configurar_estilos()
        self.criar_cabecalho()
        self.criar_area_filtros()
        self.criar_formulario()
        self.criar_tabela_listagem()
        self.criar_rodape()

        self.carregar_sugestoes_memoria()
        
        # Inicia loop de atualização automática
        self.iniciar_loop_atualizacao()

    def iniciar_loop_atualizacao(self):
        """Atualiza a tabela a cada 5 segundos"""
        try:
            self.carregar_dados(manter_selecao=True)
        except:
            pass 
        self.root.after(5000, self.iniciar_loop_atualizacao)

    def configurar_estilos(self):
        """Configura o tema do Tkinter (Flat Design)"""
        style = ttk.Style()
        style.theme_use('clam') 
        style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        style.configure('TCombobox', foreground=COLOR_TEXT, selectbackground=COLOR_SECONDARY, padding=5)
        
        # Estilo da Tabela
        style.configure("Treeview.Heading", font=FONT_BOLD, background=COLOR_PRIMARY, foreground=COLOR_SECONDARY, relief="flat", padding=10)
        style.configure("Treeview", background="white", fieldbackground="white", foreground=COLOR_TEXT, rowheight=30, font=FONT_MAIN, borderwidth=0)
        style.map("Treeview", background=[('selected', COLOR_SECONDARY)], foreground=[('selected', COLOR_PRIMARY)])
        
        style.configure("TLabelframe", background=COLOR_BG, bordercolor=COLOR_PRIMARY, borderwidth=2)
        style.configure("TLabelframe.Label", font=FONT_BOLD, foreground=COLOR_PRIMARY, background=COLOR_BG, padding=(0, 5))

    def criar_cabecalho(self):
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARY, pady=15, padx=20)
        header_frame.pack(fill="x")

        try:
            caminho_imagem = resource_path("logo.png")
            if os.path.exists(caminho_imagem):
                img = Image.open(caminho_imagem)
                img = img.resize((70, 70), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=COLOR_PRIMARY)
                lbl_logo.pack(side="left", padx=(0, 15))
        except Exception as e:
            print(f"Erro logo: {e}")

        title_container = tk.Frame(header_frame, bg=COLOR_PRIMARY)
        title_container.pack(side="left", fill="y")
        tk.Label(title_container, text="SISTEMA DE GESTÃO", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, font=FONT_TITLE).pack(anchor="w")
        tk.Label(title_container, text="Controle de Vendas e Pedidos", bg=COLOR_PRIMARY, fg="white", font=("Helvetica", 12)).pack(anchor="w")

        # Botão para o Módulo Financeiro (Despesas)
        btn_desp = tk.Button(header_frame, text="💲 DESPESAS", bg=COLOR_SECONDARY, fg=COLOR_PRIMARY, 
                             font=("Arial", 10, "bold"), bd=2, relief="raised", cursor="hand2",
                             command=self.pedir_senha_custom) 
        btn_desp.pack(side="right", padx=20, ipady=5, ipadx=10)

        # Área de Faturamento (Oculta por padrão)
        frame_fat = tk.Frame(header_frame, bg=COLOR_PRIMARY, cursor="hand2")
        frame_fat.pack(side="right", padx=10)

        self.lbl_total = tk.Label(frame_fat, text="-------", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, font=("Helvetica", 24, "bold"), cursor="hand2")
        self.lbl_total.pack(side="bottom", anchor="e")
        
        lbl_titulo_fat = tk.Label(frame_fat, text="Faturamento (Segure para ver):", bg=COLOR_PRIMARY, fg="white", font=FONT_MAIN, cursor="hand2")
        lbl_titulo_fat.pack(side="top", anchor="e")

        for widget in [frame_fat, self.lbl_total, lbl_titulo_fat]:
            widget.bind("<Button-1>", self.mostrar_faturamento)
            widget.bind("<ButtonRelease-1>", self.esconder_faturamento)

    def mostrar_faturamento(self, event):
        self.lbl_total.config(text=self.total_cache)

    def esconder_faturamento(self, event):
        self.lbl_total.config(text="-------")

    # ==========================================
    # LÓGICA DE SENHA E MÓDULO FINANCEIRO
    # ==========================================
    def pedir_senha_custom(self):
        """Popup de senha seguro"""
        pop_senha = Toplevel(self.root)
        pop_senha.title("Acesso Restrito")
        
        largura = 300
        altura = 150
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (largura // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (altura // 2)
        pop_senha.geometry(f"{largura}x{altura}+{x}+{y}")
        pop_senha.configure(bg=COLOR_BG)
        pop_senha.transient(self.root)
        pop_senha.grab_set() 
        
        tk.Label(pop_senha, text="Digite a senha de acesso:", bg=COLOR_BG, font=FONT_BOLD).pack(pady=(20, 5))
        
        ent_senha = tk.Entry(pop_senha, show="*", font=("Arial", 12), justify='center')
        ent_senha.pack(pady=5, padx=20)
        ent_senha.focus_force() 
        
        def verificar(event=None):
            senha = ent_senha.get()
            if senha == "1234":
                pop_senha.destroy()
                self.abrir_janela_despesas()
            else:
                messagebox.showerror("Erro", "Senha incorreta!", parent=pop_senha)
                ent_senha.delete(0, 'end')
        
        ent_senha.bind('<Return>', verificar)
        
        btn_ok = tk.Button(pop_senha, text="ENTRAR", bg=COLOR_PRIMARY, fg="white", command=verificar)
        btn_ok.pack(pady=10)

    def abrir_janela_despesas(self):
        """Janela principal de Despesas"""
        self.top_desp = Toplevel(self.root)
        self.top_desp.title("Gerenciamento de Despesas")
        self.top_desp.geometry("1100x700")
        self.top_desp.configure(bg=COLOR_BG)
        
        # Filtros
        frame_topo = tk.Frame(self.top_desp, bg=COLOR_BG, pady=15, padx=20)
        frame_topo.pack(fill="x")
        lbl_style = {"bg": COLOR_BG, "fg": COLOR_PRIMARY, "font": FONT_BOLD}
        
        tk.Label(frame_topo, text="Mês:", **lbl_style).pack(side="left", padx=(0, 5))
        self.combo_mes_desp = ttk.Combobox(frame_topo, values=list(MESES_FILTRO.keys()), width=12, state="readonly", font=FONT_MAIN)
        try: self.combo_mes_desp.current(datetime.now().month)
        except: self.combo_mes_desp.current(0)
        self.combo_mes_desp.pack(side="left")
        self.combo_mes_desp.bind("<<ComboboxSelected>>", self.carregar_dados_despesas)
        
        tk.Label(frame_topo, text="Ano:", **lbl_style).pack(side="left", padx=(15, 5))
        self.combo_ano_desp = ttk.Combobox(frame_topo, values=ANOS_FILTRO, width=10, state="readonly", font=FONT_MAIN)
        ano_atual = str(datetime.now().year)
        if ano_atual in ANOS_FILTRO: self.combo_ano_desp.set(ano_atual)
        else: self.combo_ano_desp.current(0)
        self.combo_ano_desp.pack(side="left")
        self.combo_ano_desp.bind("<<ComboboxSelected>>", self.carregar_dados_despesas)

        # Totalizador
        tk.Label(frame_topo, text="Total Despesas:", **lbl_style).pack(side="left", padx=(30, 5))
        self.lbl_total_despesas = tk.Label(frame_topo, text="R$ 0,00", bg=COLOR_BG, fg=COLOR_DANGER, font=("Helvetica", 14, "bold"))
        self.lbl_total_despesas.pack(side="left")
        
        # Formulário Nova Despesa
        frame_form = ttk.LabelFrame(self.top_desp, text="  Nova Conta a Pagar  ", padding=15)
        frame_form.pack(fill="x", padx=20, pady=5)
        
        lbl_form = {"bg": COLOR_BG, "fg": COLOR_TEXT, "font": FONT_MAIN, "anchor": "w"}
        entry_form = {"font": FONT_MAIN, "bd": 2, "relief": "groove", "bg": "white"}
        
        tk.Label(frame_form, text="Descrição:", **lbl_form).grid(row=0, column=0, sticky="w")
        self.entry_desc_desp = tk.Entry(frame_form, width=30, **entry_form)
        self.entry_desc_desp.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_form, text="Categoria:", **lbl_form).grid(row=0, column=2, sticky="w", padx=15)
        self.combo_cat_desp = ttk.Combobox(frame_form, values=CATEGORIAS_DESPESA, width=18, font=FONT_MAIN)
        self.combo_cat_desp.current(0)
        self.combo_cat_desp.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_form, text="Valor (R$):", **lbl_form).grid(row=0, column=4, sticky="w", padx=15)
        self.entry_val_desp = tk.Entry(frame_form, width=12, **entry_form)
        self.entry_val_desp.grid(row=0, column=5, padx=5)
        
        tk.Label(frame_form, text="Vencimento:", **lbl_form).grid(row=0, column=6, sticky="w", padx=15)
        self.entry_venc_desp = tk.Entry(frame_form, width=12, **entry_form)
        self.entry_venc_desp.grid(row=0, column=7, padx=5)
        self.entry_venc_desp.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Button(frame_form, text="DATA", bg=COLOR_SECONDARY, fg=COLOR_PRIMARY, bd=1, 
                  command=lambda: self.abrir_popup_calendario(self.entry_venc_desp)).grid(row=0, column=8)
                  
        tk.Button(frame_form, text="LANÇAR", bg=COLOR_DANGER, fg="white", font=FONT_BOLD, 
                  command=self.adicionar_despesa).grid(row=0, column=9, padx=20)
        
        self.entry_desc_desp.bind('<Return>', lambda e: self.adicionar_despesa())
        self.entry_val_desp.bind('<Return>', lambda e: self.adicionar_despesa())
        self.entry_venc_desp.bind('<Return>', lambda e: self.adicionar_despesa())

        # Tabela de Despesas
        frame_lista = ttk.LabelFrame(self.top_desp, text="  Contas do Mês  ", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Colunas centralizadas, ID Oculto
        cols = ("ID", "Descrição", "Categoria", "Valor", "Vencimento", "Status")
        self.tree_desp = ttk.Treeview(frame_lista, columns=cols, show="headings", style="Treeview")
        
        self.tree_desp["displaycolumns"] = ("Descrição", "Categoria", "Valor", "Vencimento", "Status")
        
        self.tree_desp.heading("Descrição", text="Descrição")
        self.tree_desp.column("Descrição", width=300, anchor="center")
        self.tree_desp.heading("Categoria", text="Categoria")
        self.tree_desp.column("Categoria", width=150, anchor="center")
        self.tree_desp.heading("Valor", text="Valor")
        self.tree_desp.column("Valor", width=120, anchor="center")
        self.tree_desp.heading("Vencimento", text="Vencimento")
        self.tree_desp.column("Vencimento", width=100, anchor="center")
        self.tree_desp.heading("Status", text="Status")
        self.tree_desp.column("Status", width=100, anchor="center")
        
        self.tree_desp.tag_configure('pendente', background=COLOR_BG_PENDENTE)
        self.tree_desp.tag_configure('pago', background=COLOR_BG_PAGO)
        self.tree_desp.tag_configure('sem_data', background=COLOR_BG_SEM_DATA) 
        
        self.tree_desp.bind("<Double-1>", self.abrir_edicao_despesa) 

        self.tree_desp.pack(fill="both", expand=True)
        
        # Rodapé Financeiro
        frame_foot = tk.Frame(self.top_desp, bg=COLOR_BG, pady=10)
        frame_foot.pack(fill="x", padx=20)
        
        tk.Button(frame_foot, text="Excluir Conta", bg="#757575", fg="white", font=FONT_BOLD, 
                  command=self.deletar_despesa).pack(side="left")

        tk.Button(frame_foot, text="MARCAR COMO PAGO", bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, 
                  command=self.pagar_despesa).pack(side="right")
        
        self.carregar_dados_despesas()
        self.entry_desc_desp.focus_set()

    def adicionar_despesa(self):
        """Lança despesa no banco. Suporta valor zerado mediante confirmação."""
        try:
            val_str = self.entry_val_desp.get().replace(",", ".")
            aviso_zerado = False
            
            if not val_str:
                if not messagebox.askyesno("Confirmar", "Valor não informado, deseja prosseguir?", parent=self.top_desp):
                    return
                valor = 0.0
                aviso_zerado = True
            else:
                valor = float(val_str)
            
            desc = self.entry_desc_desp.get().strip().upper()
            if not desc: return
            
            venc_br = self.entry_venc_desp.get()
            try: venc_db = datetime.strptime(venc_br, '%d/%m/%Y').strftime("%Y-%m-%d")
            except: venc_db = "" 
            
            self.cursor.execute("INSERT INTO despesas (descricao, categoria, valor, vencimento, status) VALUES (?, ?, ?, ?, ?)",
                                (desc, self.combo_cat_desp.get(), valor, venc_db, 'PENDENTE'))
            self.conn.commit()
            self.entry_desc_desp.delete(0, 'end')
            self.entry_val_desp.delete(0, 'end')
            self.carregar_dados_despesas()
            self.entry_desc_desp.focus_set() 
            
            if not aviso_zerado:
                messagebox.showinfo("Sucesso", "Conta lançada!", parent=self.top_desp)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido", parent=self.top_desp)

    def carregar_dados_despesas(self, event=None):
        """
        Carrega dados financeiros. 
        Mostra:
        1. Despesas reais do banco que batem com filtro de data (ou sem data).
        2. Projeções automáticas de despesas FIXAS que ainda não existem neste mês.
        """
        for i in self.tree_desp.get_children():
            self.tree_desp.delete(i)
            
        mes = self.combo_mes_desp.get()
        ano = self.combo_ano_desp.get()
        
        query = "SELECT * FROM despesas WHERE 1=1"
        params = []
        filtros_data = []
        
        if mes != 'Todos':
            filtros_data.append(f"strftime('%m', vencimento) = '{MESES_FILTRO[mes]}'")
        if ano != 'Todos':
            filtros_data.append(f"strftime('%Y', vencimento) = '{ano}'")
        
        if filtros_data:
            clausula_tempo = " AND (" + " AND ".join(filtros_data) + " OR vencimento = '' OR vencimento IS NULL)"
            query += clausula_tempo
        
        query += " ORDER BY CASE WHEN vencimento = '' THEN 0 ELSE 1 END, vencimento ASC"
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        total = 0
        descricoes_no_mes = []

        # 1. Carrega dados REAIS
        for row in rows:
            descricoes_no_mes.append(row[1]) 
            
            if not row[4]: 
                venc_br = "SEM DATA"
                tag = 'sem_data'
            else:
                try: venc_br = datetime.strptime(row[4], "%Y-%m-%d").strftime("%d/%m/%Y")
                except: venc_br = row[4]
                tag = 'pago' if row[5] == 'PAGO' else 'pendente'
            
            val_fmt = "R$ {:,.2f}".format(row[3]).replace(",", "X").replace(".", ",").replace("X", ".")
            status = row[5]
            
            # ORDEM: ID, Desc, Cat, Val, Venc, Status
            self.tree_desp.insert("", "end", values=(row[0], row[1], row[2], val_fmt, venc_br, status), tags=(tag,))
            total += row[3]

        # 2. PROJEÇÃO DE FIXAS
        if mes != 'Todos' and ano != 'Todos':
            self.cursor.execute("SELECT DISTINCT descricao, valor, categoria FROM despesas WHERE categoria='Fixa'")
            fixas_historico = self.cursor.fetchall()
            
            for desc, val, cat in fixas_historico:
                if desc not in descricoes_no_mes:
                    val_fmt = "R$ {:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")
                    id_virtual = f"FIX_||{desc}||{val}"
                    self.tree_desp.insert("", 0, values=(id_virtual, desc, cat, val_fmt, "A DEFINIR", "A LANÇAR"), tags=('sem_data',))
            
        self.lbl_total_despesas.config(text="R$ {:,.2f}".format(total).replace(",", "X").replace(".", ",").replace("X", "."))

    def abrir_edicao_despesa(self, event):
        """NOVA FUNÇÃO: Abre janela completa para editar despesa ou confirmar projeção"""
        selected = self.tree_desp.selection()
        if not selected: return
        item = self.tree_desp.item(selected)
        
        # Dados da linha selecionada
        id_conta = item['values'][0]
        desc_atual = item['values'][1]
        cat_atual = item['values'][2]
        val_atual_fmt = item['values'][3]
        venc_atual = item['values'][4]
        status_atual = item['values'][5]
        
        # Limpa formatação do valor para edição
        val_limpo = str(val_atual_fmt).replace("R$ ", "").replace(".", "").replace(",", ".")
        
        # Configura Janela
        popup = Toplevel(self.top_desp)
        popup.title("Editar Despesa")
        popup.geometry("450x450")
        popup.configure(bg=COLOR_BG)
        
        lbl_style = {"bg": COLOR_BG, "fg": COLOR_PRIMARY, "font": FONT_BOLD, "anchor": "w"}
        entry_style = {"font": FONT_MAIN, "bd": 2, "relief": "groove", "bg": "white"}
        
        tk.Label(popup, text="Detalhes da Despesa", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, font=FONT_HEADER, pady=10).pack(fill="x")
        
        frame_c = tk.Frame(popup, bg=COLOR_BG, padx=20, pady=20)
        frame_c.pack(fill="both", expand=True)
        
        # Campos
        tk.Label(frame_c, text="Descrição:", **lbl_style).pack(fill="x")
        edit_desc = tk.Entry(frame_c, **entry_style)
        edit_desc.pack(fill="x", pady=(0, 10))
        edit_desc.insert(0, desc_atual)
        
        tk.Label(frame_c, text="Categoria:", **lbl_style).pack(fill="x")
        edit_cat = ttk.Combobox(frame_c, values=CATEGORIAS_DESPESA, font=FONT_MAIN)
        edit_cat.pack(fill="x", pady=(0, 10))
        edit_cat.set(cat_atual)
        
        tk.Label(frame_c, text="Valor (R$):", **lbl_style).pack(fill="x")
        edit_val = tk.Entry(frame_c, **entry_style)
        edit_val.pack(fill="x", pady=(0, 10))
        edit_val.insert(0, val_limpo)
        
        # Data com Calendário
        tk.Label(frame_c, text="Vencimento:", **lbl_style).pack(fill="x")
        f_data = tk.Frame(frame_c, bg=COLOR_BG)
        f_data.pack(fill="x", pady=(0, 10))
        
        edit_venc = tk.Entry(f_data, **entry_style)
        edit_venc.pack(side="left", fill="x", expand=True)
        if venc_atual != "A DEFINIR" and venc_atual != "SEM DATA":
            edit_venc.insert(0, venc_atual)
            
        tk.Button(f_data, text="DATA", bg=COLOR_SECONDARY, fg=COLOR_PRIMARY, bd=1, 
                  command=lambda: self.abrir_popup_calendario(edit_venc)).pack(side="left", padx=5)
        
        tk.Label(frame_c, text="Status:", **lbl_style).pack(fill="x")
        edit_status = ttk.Combobox(frame_c, values=STATUS_DESPESA, font=FONT_MAIN)
        edit_status.pack(fill="x", pady=(0, 10))
        # Ajusta status se for projeção
        if status_atual == "A LANÇAR":
            edit_status.set("PENDENTE")
        else:
            edit_status.set(status_atual)
            
        def salvar():
            try:
                # Validações
                n_desc = edit_desc.get().strip().upper()
                n_cat = edit_cat.get()
                n_val_str = edit_val.get().replace(",", ".")
                n_venc_br = edit_venc.get()
                n_status = edit_status.get()
                
                if not n_val_str: n_val = 0.0
                else: n_val = float(n_val_str)
                
                try:
                    n_venc_db = datetime.strptime(n_venc_br, '%d/%m/%Y').strftime("%Y-%m-%d")
                except:
                    # Se deixar vazio ou inválido, salva como vazio (sem data)
                    n_venc_db = ""
                
                # Lógica de Salvar (Novo ou Edição)
                if str(id_conta).startswith("FIX_"):
                    # É PROJEÇÃO: Cria nova
                    self.cursor.execute("INSERT INTO despesas (descricao, categoria, valor, vencimento, status) VALUES (?, ?, ?, ?, ?)",
                                        (n_desc, n_cat, n_val, n_venc_db, n_status))
                else:
                    # É EXISTENTE: Atualiza
                    self.cursor.execute("""
                        UPDATE despesas SET descricao=?, categoria=?, valor=?, vencimento=?, status=?
                        WHERE id=?
                    """, (n_desc, n_cat, n_val, n_venc_db, n_status, id_conta))
                
                self.conn.commit()
                popup.destroy()
                self.carregar_dados_despesas()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {e}")

        tk.Button(popup, text="SALVAR", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, font=FONT_BOLD, 
                  command=salvar).pack(fill="x", side="bottom", pady=10, padx=20)

    def pagar_despesa(self):
        """Marca como PAGO. Se for projeção, cria e paga."""
        sel = self.tree_desp.selection()
        if not sel: return
        item = self.tree_desp.item(sel)
        id_conta = item['values'][0]
        
        if str(id_conta).startswith("FIX_"):
            partes = str(id_conta).split("||")
            desc_real = partes[1]
            val_real = float(partes[2])
            
            mes_idx = MESES_FILTRO.get(self.combo_mes_desp.get())
            ano = self.combo_ano_desp.get()
            if mes_idx and ano != 'Todos':
                venc_db = f"{ano}-{mes_idx}-10"
            else:
                venc_db = datetime.now().strftime("%Y-%m-%d")

            self.cursor.execute("INSERT INTO despesas (descricao, categoria, valor, vencimento, status) VALUES (?, ?, ?, ?, ?)",
                                (desc_real, 'Fixa', val_real, venc_db, 'PAGO'))
        else:
            self.cursor.execute("UPDATE despesas SET status='PAGO' WHERE id=?", (id_conta,))
            
        self.conn.commit()
        self.carregar_dados_despesas()

    def deletar_despesa(self):
        """
        CORRIGIDO: Lógica de exclusão inteligente.
        - Se for projeção (FIX_): Pergunta se quer deletar TUDO (histórico e futuro).
        - Se for real e Fixa: Pergunta se apaga só a do mês ou TUDO.
        - Se for variável: Apaga só a do mês.
        """
        sel = self.tree_desp.selection()
        if not sel: return
        
        item = self.tree_desp.item(sel)
        id_conta = item['values'][0]
        desc_conta = item['values'][1]
        cat_conta = item['values'][2]
        
        # Caso 1: É uma projeção (linha cinza "A DEFINIR")
        if str(id_conta).startswith("FIX_"):
            # Extrai a descrição real do ID virtual se necessário, ou usa a da coluna
            if "||" in str(id_conta):
                desc_real = str(id_conta).split("||")[1]
            else:
                desc_real = desc_conta

            if messagebox.askyesno("Excluir Recorrência", 
                                   f"Deseja excluir '{desc_real}' de TODOS os meses?\n\nIsso removerá todo o histórico e impedirá novos lançamentos futuros."):
                self.cursor.execute("DELETE FROM despesas WHERE descricao=? AND categoria='Fixa'", (desc_real,))
                self.conn.commit()
                self.carregar_dados_despesas()
            return

        # Caso 2: É uma conta Real (já lançada no banco)
        if cat_conta == 'Fixa':
            # Pergunta se quer apagar só essa ou a série inteira
            resposta = messagebox.askyesnocancel("Excluir Despesa Fixa", 
                                                 "Esta é uma despesa FIXA.\n\n"
                                                 "SIM: Exclui de TODOS os meses (Histórico e Futuro)\n"
                                                 "NÃO: Exclui APENAS deste mês\n"
                                                 "CANCELAR: Não faz nada")
            
            if resposta is None: return # Cancelou
            
            if resposta: # SIM -> Delete All
                self.cursor.execute("DELETE FROM despesas WHERE descricao=? AND categoria='Fixa'", (desc_conta,))
            else: # NÃO -> Delete Single
                self.cursor.execute("DELETE FROM despesas WHERE id=?", (id_conta,))
        else:
            # Caso 3: Despesa Variável comum
            if not messagebox.askyesno("Confirmar", "Excluir esta conta?", parent=self.top_desp): return
            self.cursor.execute("DELETE FROM despesas WHERE id=?", (id_conta,))
            
        self.conn.commit()
        self.carregar_dados_despesas()

    # ==========================================
    # INTERFACE PRINCIPAL (PEDIDOS)
    # ==========================================
    def criar_area_filtros(self):
        """Barra de filtros principal"""
        frame_topo = tk.Frame(self.root, bg=COLOR_BG, pady=15, padx=20)
        frame_topo.pack(fill="x")
        lbl_style = {"bg": COLOR_BG, "fg": COLOR_PRIMARY, "font": FONT_BOLD}
        
        tk.Label(frame_topo, text="Filtrar por Mês:", **lbl_style).pack(side="left", padx=(0, 5))
        self.combo_filtro_mes = ttk.Combobox(frame_topo, values=list(MESES_FILTRO.keys()), width=12, state="readonly", font=FONT_MAIN)
        try: self.combo_filtro_mes.current(datetime.now().month)
        except: self.combo_filtro_mes.current(0)
        self.combo_filtro_mes.pack(side="left")
        self.combo_filtro_mes.bind("<<ComboboxSelected>>", self.carregar_dados) 
        
        tk.Label(frame_topo, text="Ano:", **lbl_style).pack(side="left", padx=(15, 5))
        self.combo_filtro_ano = ttk.Combobox(frame_topo, values=ANOS_FILTRO, width=8, state="readonly", font=FONT_MAIN)
        ano_atual = str(datetime.now().year)
        if ano_atual in ANOS_FILTRO: self.combo_filtro_ano.set(ano_atual)
        else: self.combo_filtro_ano.current(0)
        self.combo_filtro_ano.pack(side="left")
        self.combo_filtro_ano.bind("<<ComboboxSelected>>", self.carregar_dados)
        
        tk.Label(frame_topo, text="Buscar Cliente:", **lbl_style).pack(side="left", padx=(30, 5))
        self.entry_filtro_nome = tk.Entry(frame_topo, width=25, font=FONT_MAIN, bd=2, relief="groove")
        self.entry_filtro_nome.pack(side="left")
        self.entry_filtro_nome.bind("<KeyRelease>", self.carregar_dados)

    def criar_formulario(self):
        """Área de input de Pedidos"""
        self.frame_form = ttk.LabelFrame(self.root, text="  Novo Pedido  ", padding=15)
        self.frame_form.pack(fill="x", padx=20, pady=5)
        lbl_style = {"bg": COLOR_BG, "fg": COLOR_TEXT, "font": FONT_MAIN, "anchor": "w"}
        entry_style = {"font": FONT_MAIN, "bd": 2, "relief": "groove", "bg": "white"}
        
        # Nome do Cliente
        tk.Label(self.frame_form, text="Nome Cliente:", **lbl_style).grid(row=0, column=0, sticky="w")
        self.entry_nome_novo = tk.Entry(self.frame_form, width=30, **entry_style)
        self.entry_nome_novo.grid(row=0, column=1, padx=5, pady=5)
        self.entry_nome_novo.bind('<KeyRelease>', self.atualizar_lista_clientes)
        self.entry_nome_novo.bind('<Down>', lambda e: self.mover_foco_lista(self.listbox_clientes))
        
        self.listbox_clientes = tk.Listbox(self.root, width=45, height=5, font=FONT_MAIN, bg="#FFFDE7", bd=2, relief="ridge")
        self.listbox_clientes.bind("<<ListboxSelect>>", self.selecionar_cliente)
        self.listbox_clientes.bind("<Return>", self.selecionar_cliente)
        self.listbox_clientes.bind("<Motion>", self.destacar_no_mouse)
        
        tk.Label(self.frame_form, text="Cidade:", **lbl_style).grid(row=0, column=2, sticky="w", padx=(20,0))
        self.combo_cidade = ttk.Combobox(self.frame_form, values=CIDADES, width=18, font=FONT_MAIN)
        self.combo_cidade.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(self.frame_form, text="Vendedor:", **lbl_style).grid(row=0, column=4, sticky="w", padx=(20,0))
        self.combo_vendedor = ttk.Combobox(self.frame_form, values=VENDEDORES, width=18, font=FONT_MAIN)
        self.combo_vendedor.current(0) 
        self.combo_vendedor.grid(row=0, column=5, padx=5, pady=5)
        
        # Produto
        tk.Label(self.frame_form, text="Produto/Fórmula:", **lbl_style).grid(row=1, column=0, sticky="w", pady=10)
        self.entry_produto = tk.Entry(self.frame_form, width=30, **entry_style)
        self.entry_produto.grid(row=1, column=1, padx=5, pady=10)
        self.entry_produto.bind('<KeyRelease>', self.atualizar_lista_produtos)
        self.entry_produto.bind('<Down>', lambda e: self.mover_foco_lista(self.listbox_produtos))
        
        self.listbox_produtos = tk.Listbox(self.root, width=45, height=5, font=FONT_MAIN, bg="#FFFDE7", bd=2, relief="ridge")
        self.listbox_produtos.bind("<<ListboxSelect>>", self.selecionar_produto)
        self.listbox_produtos.bind("<Return>", self.selecionar_produto)
        self.listbox_produtos.bind("<Motion>", self.destacar_no_mouse)
        
        # Valor e Data
        tk.Label(self.frame_form, text="Valor (R$):", **lbl_style).grid(row=1, column=2, sticky="w", padx=(20,0))
        self.entry_valor = tk.Entry(self.frame_form, width=18, **entry_style)
        self.entry_valor.grid(row=1, column=3, padx=5, pady=10)
        
        tk.Label(self.frame_form, text="Data Entrega:", **lbl_style).grid(row=1, column=4, sticky="w", padx=(20,0))
        frame_cal = tk.Frame(self.frame_form, bg=COLOR_BG)
        frame_cal.grid(row=1, column=5, padx=5, sticky="w")
        self.entry_entrega = tk.Entry(frame_cal, width=14, **entry_style, fg=COLOR_PRIMARY)
        self.entry_entrega.pack(side="left")
        self.entry_entrega.insert(0, datetime.now().strftime("%d/%m/%Y")) 
        
        btn_cal = tk.Button(frame_cal, text="DATA", bg=COLOR_SECONDARY, fg=COLOR_PRIMARY, 
                            font=("Arial", 9, "bold"), bd=1, relief="raised", cursor="hand2",
                            command=lambda: self.abrir_popup_calendario(self.entry_entrega))
        btn_cal.pack(side="left", padx=2)
        
        # Status e Salvar
        tk.Label(self.frame_form, text="Status:", **lbl_style).grid(row=1, column=6, sticky="w", padx=(20,0))
        self.combo_status = ttk.Combobox(self.frame_form, values=STATUS_OPCOES, width=15, font=FONT_MAIN)
        self.combo_status.current(0) 
        self.combo_status.grid(row=1, column=7, padx=5, pady=10)
        
        btn_add = tk.Button(self.frame_form, text="SALVAR PEDIDO", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, 
                            font=("Helvetica", 11, "bold"), width=18, height=2, bd=0, cursor="hand2",
                            activebackground=COLOR_SECONDARY, activeforeground=COLOR_PRIMARY,
                            command=self.adicionar_pedido)
        btn_add.grid(row=0, column=8, rowspan=2, padx=20)

    def criar_tabela_listagem(self):
        """Cria a tabela principal que exibe os dados"""
        frame_lista = ttk.LabelFrame(self.root, text="  Últimos Lançamentos  ", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=20, pady=10)
        
        cols = ("ID", "Data", "Nome", "Cidade", "Vendedor", "Produto", "Valor", "Entrega", "Status")
        self.tree = ttk.Treeview(frame_lista, columns=cols, show="headings", style="Treeview")
        
        config_cols = {
            "Data": (90, "center"), "Nome": (200, "center"), "Cidade": (100, "center"),
            "Vendedor": (90, "center"), "Produto": (200, "center"), "Valor": (100, "center"),
            "Entrega": (90, "center"), "Status": (110, "center")
        }
        self.tree["displaycolumns"] = list(config_cols.keys())
        for col, (largura, ancora) in config_cols.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=largura, anchor=ancora)
        
        self.tree.bind("<Double-1>", self.abrir_janela_edicao)
        
        self.tree.tag_configure('orcamento', background='#FFF3CD')
        self.tree.tag_configure('confirmado', background='#C8E6C9') 
        self.tree.tag_configure('cancelado', background='#FFEBEE')
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def criar_rodape(self):
        """Botões de ação rápida no rodapé"""
        frame_footer = tk.Frame(self.root, bg=COLOR_BG, pady=15, padx=20)
        frame_footer.pack(fill="x")
        btn_style = {"font": FONT_BOLD, "bd": 0, "cursor": "hand2", "padx": 15, "pady": 8}
        
        btn_del = tk.Button(frame_footer, text="Excluir Selecionado", bg="#757575", fg="white", 
                            command=self.deletar_pedido, **btn_style)
        btn_del.pack(side="left")
        
        btn_cancelar = tk.Button(frame_footer, text="✖ Cancelar Pedido", bg=COLOR_DANGER, fg="white", 
                                 command=self.cancelar_pedido, **btn_style)
        btn_cancelar.pack(side="left", padx=10)
        
        btn_confirmar = tk.Button(frame_footer, text="✔ Confirmar Pedido", bg=COLOR_SUCCESS, fg="white", 
                                  command=self.confirmar_pedido, **btn_style)
        btn_confirmar.pack(side="left")

    def criar_tabela(self):
        """Inicializa tabelas do banco"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT, nome TEXT, cidade TEXT, produto TEXT,
                valor REAL, status TEXT, vendedor TEXT, entrega TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT, categoria TEXT, valor REAL, 
                vencimento TEXT, status TEXT
            )
        """)
        self.conn.commit()

    def abrir_popup_calendario(self, entry_alvo):
        """Popup de calendário"""
        if isinstance(entry_alvo, tk.Entry):
            parent = entry_alvo.winfo_toplevel()
        else:
            parent = self.root

        top_cal = Toplevel(parent)
        top_cal.title("Selecione a Data")
        
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        top_cal.geometry(f"+{x}+{y}")
        
        cal = Calendar(top_cal, selectmode='day', locale='pt_BR', date_pattern='dd/mm/yyyy',
                       showweeknumbers=False,
                       background=COLOR_PRIMARY, foreground='white',
                       headersbackground=COLOR_PRIMARY, headersforeground='white',
                       selectbackground=COLOR_SECONDARY, selectforeground=COLOR_PRIMARY,
                       bordercolor=COLOR_PRIMARY, font=FONT_MAIN)
        cal.pack(padx=10, pady=10)
        
        def data_selecionada(event):
            data = cal.get_date()
            entry_alvo.delete(0, tk.END)
            entry_alvo.insert(0, data)
            top_cal.destroy()
            
        cal.bind("<<CalendarSelected>>", data_selecionada)

    # --- Autocomplete Helpers ---
    def carregar_sugestoes_memoria(self):
        try:
            self.cursor.execute("SELECT DISTINCT nome FROM pedidos ORDER BY nome")
            self.lista_clientes_db = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute("SELECT DISTINCT produto FROM pedidos ORDER BY produto")
            self.lista_produtos_db = [row[0] for row in self.cursor.fetchall()]
        except: 
            pass

    def destacar_no_mouse(self, event):
        listbox = event.widget
        try:
            index = listbox.nearest(event.y)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            listbox.activate(index)
        except: 
            pass

    def mover_foco_lista(self, listbox):
        if listbox.winfo_ismapped() and listbox.size() > 0:
            listbox.focus_set()
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(0)
            listbox.activate(0)

    def atualizar_lista_clientes(self, event):
        if event.keysym in ['Up', 'Down', 'Return', 'Left', 'Right', 'Tab']: return
        digitado = self.entry_nome_novo.get()
        if digitado == '':
            self.listbox_clientes.place_forget()
            return
        lista_filtrada = [x for x in self.lista_clientes_db if digitado.lower() in x.lower()]
        if lista_filtrada:
            self.listbox_clientes.delete(0, tk.END)
            for i, nome in enumerate(lista_filtrada): 
                self.listbox_clientes.insert(tk.END, nome)
                if i % 2 == 0: self.listbox_clientes.itemconfigure(i, background="#f0f0f0")
            x = self.entry_nome_novo.winfo_rootx() - self.root.winfo_rootx()
            y = self.entry_nome_novo.winfo_rooty() + self.entry_nome_novo.winfo_height() - self.root.winfo_rooty()
            self.listbox_clientes.place(x=x, y=y, width=self.entry_nome_novo.winfo_width())
            self.listbox_clientes.lift()
        else:
            self.listbox_clientes.place_forget()

    def selecionar_cliente(self, event):
        try:
            selection = self.listbox_clientes.curselection()
            if selection:
                nome_escolhido = self.listbox_clientes.get(selection[0])
                self.entry_nome_novo.delete(0, tk.END)
                self.entry_nome_novo.insert(0, nome_escolhido)
                self.listbox_clientes.place_forget()
                self.preencher_cidade_automatica(nome_escolhido)
                self.entry_produto.focus_set()
        except: pass

    def atualizar_lista_produtos(self, event):
        if event.keysym in ['Up', 'Down', 'Return', 'Left', 'Right', 'Tab']: return
        digitado = self.entry_produto.get()
        if digitado == '':
            self.listbox_produtos.place_forget()
            return
        lista_filtrada = [x for x in self.lista_produtos_db if digitado.lower() in x.lower()]
        if lista_filtrada:
            self.listbox_produtos.delete(0, tk.END)
            for i, prod in enumerate(lista_filtrada): 
                self.listbox_produtos.insert(tk.END, prod)
                if i % 2 == 0: self.listbox_produtos.itemconfigure(i, background="#f0f0f0")
            x = self.entry_produto.winfo_rootx() - self.root.winfo_rootx()
            y = self.entry_produto.winfo_rooty() + self.entry_produto.winfo_height() - self.root.winfo_rooty()
            self.listbox_produtos.place(x=x, y=y, width=self.entry_produto.winfo_width())
            self.listbox_produtos.lift()
        else:
            self.listbox_produtos.place_forget()

    def selecionar_produto(self, event):
        try:
            selection = self.listbox_produtos.curselection()
            if selection:
                prod_escolhido = self.listbox_produtos.get(selection[0])
                self.entry_produto.delete(0, tk.END)
                self.entry_produto.insert(0, prod_escolhido)
                self.listbox_produtos.place_forget()
                self.entry_valor.focus_set()
        except: pass

    def preencher_cidade_automatica(self, nome_cliente):
        self.cursor.execute("SELECT cidade FROM pedidos WHERE nome = ? ORDER BY id DESC LIMIT 1", (nome_cliente,))
        resultado = self.cursor.fetchone()
        if resultado:
            cidade_encontrada = resultado[0]
            if cidade_encontrada in CIDADES: self.combo_cidade.set(cidade_encontrada)
            else: self.combo_cidade.set(cidade_encontrada)

    def abrir_janela_edicao(self, event):
        """Popup de edição de pedido"""
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected)
        dados = item['values']
        pedido_id = dados[0]
        
        popup = Toplevel(self.root)
        popup.title(f"Editar Pedido #{pedido_id}")
        popup.geometry("450x550")
        popup.configure(bg=COLOR_BG)
        
        lbl_style = {"bg": COLOR_BG, "fg": COLOR_PRIMARY, "font": FONT_BOLD, "anchor": "w"}
        entry_style = {"font": FONT_MAIN, "bd": 2, "relief": "groove", "bg": "white"}
        
        tk.Label(popup, text=f"Editando: {dados[2]}", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, font=FONT_HEADER, pady=10).pack(fill="x")
        frame_conteudo = tk.Frame(popup, bg=COLOR_BG, padx=20, pady=20)
        frame_conteudo.pack(fill="both", expand=True)
        
        tk.Label(frame_conteudo, text="Nome Cliente:", **lbl_style).pack(fill="x", pady=(10,0))
        edit_nome = tk.Entry(frame_conteudo, **entry_style)
        edit_nome.pack(fill="x", pady=(0,10))
        edit_nome.insert(0, dados[2])
        
        frame_row1 = tk.Frame(frame_conteudo, bg=COLOR_BG)
        frame_row1.pack(fill="x", pady=(0,10))
        tk.Label(frame_row1, text="Cidade:", **lbl_style).pack(side="left")
        edit_cidade = ttk.Combobox(frame_row1, values=CIDADES, width=15, font=FONT_MAIN)
        edit_cidade.pack(side="left", padx=(5, 20))
        edit_cidade.set(dados[3])
        
        tk.Label(frame_row1, text="Vendedor:", **lbl_style).pack(side="left")
        edit_vendedor = ttk.Combobox(frame_row1, values=VENDEDORES, width=15, font=FONT_MAIN)
        edit_vendedor.pack(side="left", padx=5)
        edit_vendedor.set(dados[4])
        
        tk.Label(frame_conteudo, text="Produto:", **lbl_style).pack(fill="x")
        edit_produto = tk.Entry(frame_conteudo, **entry_style)
        edit_produto.pack(fill="x", pady=(0,10))
        edit_produto.insert(0, dados[5])
        
        frame_row2 = tk.Frame(frame_conteudo, bg=COLOR_BG)
        frame_row2.pack(fill="x", pady=(0,10))
        tk.Label(frame_row2, text="Valor (R$):", **lbl_style).pack(side="left")
        edit_valor = tk.Entry(frame_row2, width=15, **entry_style)
        edit_valor.pack(side="left", padx=(5, 20))
        valor_limpo = str(dados[6]).replace("R$ ", "").replace(".", "").replace(",", ".")
        edit_valor.insert(0, valor_limpo)
        tk.Label(frame_row2, text="Status:", **lbl_style).pack(side="left")
        edit_status = ttk.Combobox(frame_row2, values=STATUS_OPCOES, width=15, font=FONT_MAIN)
        edit_status.pack(side="left", padx=5)
        edit_status.set(dados[8])

        frame_row3 = tk.Frame(frame_conteudo, bg=COLOR_BG)
        frame_row3.pack(fill="x", pady=(10,0))
        f_ped = tk.Frame(frame_row3, bg=COLOR_BG)
        f_ped.pack(side="left", expand=True, fill="x", padx=(0,10))
        tk.Label(f_ped, text="Data Pedido:", **lbl_style).pack(anchor="w")
        f_ped_in = tk.Frame(f_ped, bg=COLOR_BG)
        f_ped_in.pack(fill="x")
        edit_data_pedido = tk.Entry(f_ped_in, **entry_style, width=12)
        edit_data_pedido.pack(side="left", expand=True, fill="x")
        edit_data_pedido.insert(0, dados[1])
        tk.Button(f_ped_in, text="DATA", bg=COLOR_SECONDARY, fg=COLOR_PRIMARY, bd=1, command=lambda: self.abrir_popup_calendario(edit_data_pedido)).pack(side="left", padx=2)
        
        f_ent = tk.Frame(frame_row3, bg=COLOR_BG)
        f_ent.pack(side="left", expand=True, fill="x")
        tk.Label(f_ent, text="Data Entrega:", **lbl_style).pack(anchor="w")
        f_ent_in = tk.Frame(f_ent, bg=COLOR_BG)
        f_ent_in.pack(fill="x")
        edit_data_entrega = tk.Entry(f_ent_in, **entry_style, width=12)
        edit_data_entrega.pack(side="left", expand=True, fill="x")
        edit_data_entrega.insert(0, dados[7])
        tk.Button(f_ent_in, text="DATA", bg=COLOR_SECONDARY, fg=COLOR_PRIMARY, bd=1, command=lambda: self.abrir_popup_calendario(edit_data_entrega)).pack(side="left", padx=2)
        
        def salvar_alteracoes():
            try:
                val_str = edit_valor.get().replace(",", ".")
                novo_valor = float(val_str)
                try:
                    dt_ped_obj = datetime.strptime(edit_data_pedido.get(), '%d/%m/%Y')
                    dt_ped_db = dt_ped_obj.strftime("%Y-%m-%d")
                except: dt_ped_db = edit_data_pedido.get()
                try:
                    dt_ent_obj = datetime.strptime(edit_data_entrega.get(), '%d/%m/%Y')
                    dt_ent_db = dt_ent_obj.strftime("%Y-%m-%d")
                except: dt_ent_db = edit_data_entrega.get()
                
                self.cursor.execute("""
                    UPDATE pedidos SET
                        data = ?, nome = ?, cidade = ?, produto = ?,
                        valor = ?, status = ?, vendedor = ?, entrega = ?
                    WHERE id = ?
                """, (dt_ped_db, edit_nome.get().upper(), edit_cidade.get(), edit_produto.get().upper(),
                      novo_valor, edit_status.get(), edit_vendedor.get(), dt_ent_db, pedido_id))
                self.conn.commit()
                self.carregar_dados()
                popup.destroy()
                messagebox.showinfo("Sucesso", "Pedido atualizado com sucesso!")
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido. Use apenas números e ponto/vírgula.")
                
        tk.Button(popup, text="SALVAR ALTERAÇÕES", bg=COLOR_PRIMARY, fg=COLOR_SECONDARY, 
                  font=FONT_BOLD, bd=0, pady=10, cursor="hand2",
                  command=salvar_alteracoes).pack(fill="x", side="bottom")

    def adicionar_pedido(self):
        try:
            val_str = self.entry_valor.get().replace(",", ".")
            if not val_str: 
                messagebox.showwarning("Atenção", "Preencha o valor.")
                return
            valor = float(val_str)
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            nome_cliente = self.entry_nome_novo.get().strip().upper() 
            if not nome_cliente:
                 messagebox.showwarning("Atenção", "Preencha o nome do cliente.")
                 return
            vendedor = self.combo_vendedor.get().strip()
            produto = self.entry_produto.get().strip().upper()
            data_entrega_br = self.entry_entrega.get()
            try:
                dt_obj = datetime.strptime(data_entrega_br, '%d/%m/%Y')
                data_entrega_db = dt_obj.strftime("%Y-%m-%d")
            except:
                data_entrega_db = data_entrega_br
            self.cursor.execute("""
                INSERT INTO pedidos (data, nome, cidade, produto, valor, status, vendedor, entrega)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_hoje, nome_cliente, self.combo_cidade.get(), produto, valor, self.combo_status.get(), vendedor, data_entrega_db))
            self.conn.commit()
            
            self.entry_nome_novo.delete(0, 'end')
            self.entry_produto.delete(0, 'end')
            self.entry_valor.delete(0, 'end')
            self.entry_entrega.delete(0, tk.END)
            self.entry_entrega.insert(0, datetime.now().strftime("%d/%m/%Y"))
            self.listbox_clientes.place_forget()
            self.listbox_produtos.place_forget()
            self.carregar_dados()
            self.carregar_sugestoes_memoria()
            messagebox.showinfo("Sucesso", "Pedido salvo!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")

    def carregar_dados(self, event=None, manter_selecao=False):
        id_selecionado = None
        if manter_selecao:
            selected = self.tree.selection()
            if selected:
                item = self.tree.item(selected)
                if item and 'values' in item:
                    id_selecionado = item['values'][0]

        for i in self.tree.get_children():
            self.tree.delete(i)
            
        mes_selecionado = self.combo_filtro_mes.get()
        ano_selecionado = self.combo_filtro_ano.get()
        nome_buscado = self.entry_filtro_nome.get()
        
        query = "SELECT * FROM pedidos WHERE 1=1"
        params = []
        if mes_selecionado != 'Todos':
            query += " AND strftime('%m', data) = ?"
            params.append(MESES_FILTRO[mes_selecionado])
        if ano_selecionado != 'Todos':
            query += " AND strftime('%Y', data) = ?"
            params.append(ano_selecionado)
        if nome_buscado:
            query += " AND nome LIKE ?"
            params.append(f"%{nome_buscado}%")
        query += " ORDER BY data DESC"
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            total_confirmado = 0
            for row in rows:
                row_id = row[0]
                try: data_br = datetime.strptime(row[1], "%Y-%m-%d").strftime("%d/%m/%Y")
                except: data_br = row[1]
                nome = row[2]
                cidade = row[3]
                produto = row[4]
                valor_fmt = "R$ {:,.2f}".format(row[5]).replace(",", "X").replace(".", ",").replace("X", ".")
                status = row[6]
                try: vendedor = row[7] if row[7] else "-"
                except: vendedor = "-"
                try: 
                    entrega_raw = row[8]
                    if entrega_raw:
                        entrega_br = datetime.strptime(entrega_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
                    else: entrega_br = "-"
                except: entrega_br = "-"
                tag_cor = 'orcamento'
                if status == 'CONFIRMADO': tag_cor = 'confirmado'
                elif status == 'CANCELADO': tag_cor = 'cancelado'
                
                item_id = self.tree.insert("", "end", values=(row_id, data_br, nome, cidade, vendedor, produto, valor_fmt, entrega_br, status), tags=(tag_cor,))
                
                if manter_selecao and id_selecionado and row_id == id_selecionado:
                    self.tree.selection_set(item_id)
                    self.tree.see(item_id)

                if status == "CONFIRMADO":
                    total_confirmado += row[5]
            
            total_fmt = "R$ {:,.2f}".format(total_confirmado).replace(",", "X").replace(".", ",").replace("X", ".")
            self.total_cache = total_fmt
            if str(self.lbl_total.cget("text")) != "-------":
                 self.lbl_total.config(text=self.total_cache)
        except: pass

    def confirmar_pedido(self):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected)
        pedido_id = item['values'][0]
        self.cursor.execute("UPDATE pedidos SET status='CONFIRMADO' WHERE id=?", (pedido_id,))
        self.conn.commit()
        self.carregar_dados()

    def cancelar_pedido(self):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected)
        pedido_id = item['values'][0]
        if not messagebox.askyesno("Cancelar", "Tem certeza que deseja CANCELAR este pedido?"): return
        self.cursor.execute("UPDATE pedidos SET status='CANCELADO' WHERE id=?", (pedido_id,))
        self.conn.commit()
        self.carregar_dados()

    def deletar_pedido(self):
        selected = self.tree.selection()
        if not selected: return
        if not messagebox.askyesno("Excluir", "ATENÇÃO: Isso apagará o pedido do banco de dados.\nConfirmar exclusão?"): return
        item = self.tree.item(selected)
        pedido_id = item['values'][0]
        self.cursor.execute("DELETE FROM pedidos WHERE id=?", (pedido_id,))
        self.conn.commit()
        self.carregar_dados()
        self.carregar_sugestoes_memoria()

if __name__ == "__main__":
    root = tk.Tk()
    try: 
        if os.path.exists("logo.png"):
            icon = ImageTk.PhotoImage(file="logo.png")
            root.iconphoto(False, icon)
    except: pass
    
    app = AppControleVendas(root)
    root.mainloop()