import tkinter as tk
from tkinter import messagebox, ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import sqlite3
import datetime

# Model - Responsável pela interação com o banco de dados
class AtendimentoModel:
    def __init__(self):
        self.conexao = sqlite3.connect('atendimentos.db')
        self.cursor = self.conexao.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        
        # Cria a tabela de municipes
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='municipes'")
        if not self.cursor.fetchone():
            self.cursor.execute('''
            CREATE TABLE municipes (
                cpf TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                endereco TEXT,
                bairro TEXT NOT NULL DEFAULT 'Bairro Não Informado',
                telefone TEXT NOT NULL,
                rg TEXT,
                titulo_eleitor TEXT,
                zona TEXT,
                secao TEXT
            )
            ''')
            print("Tabela 'municipes' criada com sucesso.")

        # Cria a tabela de atendimentos
        # Verificar e criar a tabela de atendimentos, se não existir
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='atendimentos'")
        if not self.cursor.fetchone():
            self.cursor.execute('''
            CREATE TABLE atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL,
                tipo_pedido TEXT NOT NULL,
                descricao TEXT,
                anexos TEXT,
                data_horario TEXT NOT NULL,
                prazo_resolucao TEXT,
                assessor TEXT,
                prioridade TEXT NOT NULL DEFAULT 'Normal',
                status TEXT NOT NULL DEFAULT 'Pendente',
                FOREIGN KEY (cpf) REFERENCES municipes (cpf)
            )
            ''')
        print("Tabela 'atendimentos' criada com sucesso.")

        # Confirma as alterações no banco de dados
        self.conexao.commit()
        print("Tabelas criadas e prontas para uso.")



    def registrar_municipe(self, cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao):
        self.cursor.execute('''
        INSERT OR IGNORE INTO municipes (cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao))
        self.conexao.commit()

    def buscar_municipes(self, termo):
        self.cursor.execute('''
        SELECT * FROM municipes WHERE nome LIKE ? OR cpf LIKE ?
        ''', (f"%{termo}%", f"%{termo}%"))
        return self.cursor.fetchall()
    
    def buscar_municipe_por_cpf(self, cpf):
        self.cursor.execute('''
            SELECT cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao 
            FROM municipes 
            WHERE cpf = ?
        ''', (cpf,))
        return self.cursor.fetchone()


    def atualizar_municipe(self, cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao):
        self.cursor.execute('''
        UPDATE municipes
        SET nome = ?, endereco = ?, bairro = ?, telefone = ?, rg = ?, titulo_eleitor = ?, zona = ?, secao = ?
        WHERE cpf = ?
        ''', (nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao, cpf))
        self.conexao.commit()

    def registrar_atendimento(self, cpf, tipo_pedido, descricao, anexos, data_horario, prazo_resolucao, assessor, prioridade, status):
        self.cursor.execute('''
        INSERT INTO atendimentos (cpf, tipo_pedido, descricao, anexos, data_horario, prazo_resolucao, assessor, prioridade, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cpf, tipo_pedido, descricao, anexos, data_horario, prazo_resolucao, assessor, prioridade, status))
        self.conexao.commit()

    def consultar_atendimentos(self, filtro_nome=None, filtro_cpf=None):
        query = '''
        SELECT 
            a.id,               -- 0: ID do atendimento
            m.cpf,              -- 1: CPF do munícipe
            m.nome,             -- 2: Nome do munícipe
            a.tipo_pedido,      -- 3: Tipo de pedido
            a.descricao,        -- 4: Descrição do atendimento
            a.data_horario,     -- 5: Data e horário do atendimento
            a.prazo_resolucao,  -- 6: Prazo para resolução
            a.assessor,         -- 7: Assessor responsável
            a.status,           -- 8: Status do atendimento
            a.prioridade        -- 9: Prioridade do atendimento
        FROM atendimentos a
        JOIN municipes m ON a.cpf = m.cpf
        '''
        parametros = []
        condicoes = []

        # Filtros opcionais
        if filtro_cpf:
            condicoes.append("m.cpf = ?")
            parametros.append(filtro_cpf)
        if filtro_nome:
            condicoes.append("m.nome LIKE ?")
            parametros.append(f"%{filtro_nome}%")
        if condicoes:
            query += " WHERE " + " AND ".join(condicoes)

        # Adicionando a cláusula ORDER BY
        query += " ORDER BY a.data_horario DESC"

        self.cursor.execute(query, parametros)
        return self.cursor.fetchall()


    def atualizar_atendimento(self, atendimento_id, cpf, tipo_pedido, descricao, status, prazo_resolucao, assessor, prioridade):
        self.cursor.execute('''
        UPDATE atendimentos
        SET cpf = ?, tipo_pedido = ?, descricao = ?, status = ?, prazo_resolucao = ?, assessor = ?, prioridade = ?
        WHERE id = ?
        ''', (cpf, tipo_pedido, descricao, status, prazo_resolucao, assessor, prioridade, atendimento_id))
        self.conexao.commit()

    def consultar_municipes(self):
        self.cursor.execute('''
        SELECT cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao FROM municipes
        ''')
        return self.cursor.fetchall()

    def fechar_conexao(self):
        self.conexao.close()

# Controller - Responsável pela lógica da aplicação
class AtendimentoController:
    def __init__(self, model):
        self.model = model

    def registrar_municipe(self, cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao):
        self.model.registrar_municipe(cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao)

    def buscar_municipes(self, termo):
        return self.model.buscar_municipes(termo)
    
    def buscar_municipe_por_cpf(self, cpf):
        return self.model.buscar_municipe_por_cpf(cpf)

    def atualizar_municipe(self, cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao):
        self.model.atualizar_municipe(cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao)

    def registrar_atendimento(self, cpf, tipo_pedido, descricao, anexos, data_horario, prazo_resolucao, assessor, prioridade, status="Pendente"):
        self.model.registrar_atendimento(cpf, tipo_pedido, descricao, anexos, data_horario, prazo_resolucao, assessor, prioridade, status)

    def consultar_atendimentos(self, filtro_nome=None, filtro_cpf=None):
        return self.model.consultar_atendimentos(filtro_nome, filtro_cpf)

    def consultar_todos_atendimentos(self):
        return self.model.consultar_atendimentos()  # Sem filtros retorna todos os atendimentos

    def atualizar_atendimento(self, atendimento_id, cpf, tipo_pedido, descricao, status, prazo_resolucao, assessor, prioridade):
        self.model.atualizar_atendimento(atendimento_id, cpf, tipo_pedido, descricao, status, prazo_resolucao, assessor, prioridade)

    def consultar_municipes(self):
        return self.model.consultar_municipes()

    def gerar_relatorio_pdf(self, atendimentos, caminho_pdf="relatorio_atendimentos.pdf"):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(caminho_pdf, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.drawString(100, 750, "Relatório Completo de Atendimentos")
        c.drawString(100, 735, "-" * 80)

        y = 720
        for atendimento in atendimentos:
            try:
                # Atualize os índices de acordo com a consulta SQL
                c.drawString(100, y, f"ID: {atendimento[0]}")                 # ID
                c.drawString(100, y - 15, f"CPF: {atendimento[1]}")           # CPF
                c.drawString(100, y - 30, f"Nome: {atendimento[2]}")          # Nome
                c.drawString(100, y - 45, f"Tipo de Pedido: {atendimento[3]}")# Tipo de Pedido
                c.drawString(100, y - 60, f"Descrição: {atendimento[4]}")     # Descrição
                c.drawString(100, y - 75, f"Data/Horário: {atendimento[5]}")  # Data e Horário
                c.drawString(100, y - 90, f"Prazo: {atendimento[6]}")         # Prazo
                c.drawString(100, y - 105, f"Assessor: {atendimento[7]}")     # Assessor
                c.drawString(100, y - 120, f"Status: {atendimento[8]}")       # Status
                c.drawString(100, y - 135, f"Prioridade: {atendimento[9]}")   # Prioridade
                y -= 160

                # Verifique se a página precisa ser mudada
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = 750
            except IndexError:
                print(f"Erro ao acessar os dados do atendimento: {atendimento}")

        c.save()
        print(f"Relatório salvo em {caminho_pdf}")

    
    def gerar_relatorio_municipe(self, cpf):
        return self.model.consultar_atendimentos(filtro_cpf=cpf)

    def gerar_relatorio_tipo_pedido(self, tipo_pedido):
        query = '''
        SELECT a.id, m.nome, m.cpf, a.tipo_pedido, a.status, a.prioridade, m.bairro
        FROM atendimentos a
        JOIN municipes m ON a.cpf = m.cpf
        WHERE a.tipo_pedido = ?
        '''
        self.model.cursor.execute(query, (tipo_pedido,))
        return self.model.cursor.fetchall()

    def gerar_relatorio_bairro(self, bairro):
        query = '''
        SELECT a.id, m.nome, m.cpf, a.tipo_pedido, a.status, a.prioridade, m.bairro
        FROM atendimentos a
        JOIN municipes m ON a.cpf = m.cpf
        WHERE m.bairro = ?
        '''
        self.model.cursor.execute(query, (bairro,))
        return self.model.cursor.fetchall()


# Telas do sistema
# Tela de Registro de Atendimento
class RegistroAtendimentoView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self.municipe_dados = None
        self._construir_interface()

    def _construir_interface(self):
        # Layout dividido em duas colunas
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # ===================== Left Frame =====================
        # Campo de Busca por Nome
        ttk.Label(left_frame, text="Buscar Munícipe:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entrada_busca = ttk.Entry(left_frame, width=50)
        self.entrada_busca.grid(row=0, column=1, pady=2)

        ttk.Button(left_frame, text="Buscar", command=self.buscar_municipe).grid(row=0, column=2, pady=2)

        # Combobox para Seleção de Munícipe
        ttk.Label(left_frame, text="Selecionar Munícipe:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.combo_municipes = ttk.Combobox(left_frame, state="readonly", width=47)
        self.combo_municipes.grid(row=1, column=1, pady=2)
        self.combo_municipes.bind("<<ComboboxSelected>>", self.selecionar_municipe)

        # Tipo de Pedido
        ttk.Label(left_frame, text="Tipo de Pedido:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tipo_pedido_var = tk.StringVar()
        self.tipo_pedido_var.set("Selecione o tipo de pedido")
        self.tipo_pedido_dropdown = ttk.Combobox(left_frame, textvariable=self.tipo_pedido_var, values=[
            "Saúde", "Educação", "Segurança", "Transporte", "Cultura", "Esporte e Lazer", "Infraestrutura",
            "Meio Ambiente", "Inclusão Social", "Causa Animal", "Outros"
        ], state="readonly", width=47)
        self.tipo_pedido_dropdown.grid(row=2, column=1, pady=2)

        # Descrição
        ttk.Label(left_frame, text="Descrição:").grid(row=3, column=0, sticky=tk.NW, pady=2)
        self.entrada_descricao = tk.Text(left_frame, width=50, height=5)
        self.entrada_descricao.grid(row=3, column=1, pady=2)

        # Prazo de Resolução
        ttk.Label(left_frame, text="Prazo de Resolução (em dias):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entrada_prazo_resolucao = ttk.Entry(left_frame, width=50)
        self.entrada_prazo_resolucao.grid(row=4, column=1, pady=2)

        # Assessor Responsável
        ttk.Label(left_frame, text="Assessor Responsável:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entrada_assessor = ttk.Entry(left_frame, width=50)
        self.entrada_assessor.grid(row=5, column=1, pady=2)

        # Prioridade
        ttk.Label(left_frame, text="Prioridade:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.prioridade_var = tk.StringVar(value="Normal")
        self.prioridade_dropdown = ttk.Combobox(left_frame, textvariable=self.prioridade_var, values=["Baixa", "Normal", "Alta"],
                                                state="readonly", width=47)
        self.prioridade_dropdown.grid(row=6, column=1, pady=2)

        # Botões
        ttk.Button(left_frame, text="Salvar Atendimento", command=self.salvar_atendimento).grid(row=7, column=1, sticky=tk.W, pady=10)
        ttk.Button(left_frame, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=8, column=1, sticky=tk.W, pady=10)

        # ===================== Right Frame =====================
        ttk.Label(right_frame, text="Informações do Munícipe", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.info_nome = ttk.Label(right_frame, text="Nome: N/A")
        self.info_nome.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.info_endereco = ttk.Label(right_frame, text="Endereço: N/A")
        self.info_endereco.grid(row=2, column=0, sticky=tk.W, pady=2)

        self.info_bairro = ttk.Label(right_frame, text="Bairro: N/A")
        self.info_bairro.grid(row=3, column=0, sticky=tk.W, pady=2)

        self.info_telefone = ttk.Label(right_frame, text="Telefone: N/A")
        self.info_telefone.grid(row=4, column=0, sticky=tk.W, pady=2)

        self.info_rg = ttk.Label(right_frame, text="RG: N/A")
        self.info_rg.grid(row=5, column=0, sticky=tk.W, pady=2)

        self.info_titulo_eleitor = ttk.Label(right_frame, text="Título de Eleitor: N/A")
        self.info_titulo_eleitor.grid(row=6, column=0, sticky=tk.W, pady=2)

        self.info_zona = ttk.Label(right_frame, text="Zona: N/A")
        self.info_zona.grid(row=7, column=0, sticky=tk.W, pady=2)

        self.info_secao = ttk.Label(right_frame, text="Seção: N/A")
        self.info_secao.grid(row=8, column=0, sticky=tk.W, pady=2)

    def buscar_municipe(self):
        termo = self.entrada_busca.get()
        if termo:
            municipes = self.controller.buscar_municipes(termo)
            self.combo_municipes["values"] = [f"{m[1]} - {m[0]}" for m in municipes]  # Nome - CPF
            if municipes:
                self.combo_municipes.set("Selecione um munícipe")
            else:
                messagebox.showinfo("Atenção", "Nenhum munícipe encontrado.")
        else:
            messagebox.showerror("Erro", "Por favor, insira um nome ou CPF para buscar.")

    def selecionar_municipe(self, event):
        selecionado = self.combo_municipes.get()
        if selecionado:
            cpf = selecionado.split(" - ")[1]  # Extrai o CPF do texto "Nome - CPF"
            self.municipe_dados = self.controller.buscar_municipes(cpf)[0]  # Retorna o primeiro registro encontrado
            self.preencher_informacoes_municipe()

    def preencher_informacoes_municipe(self):
        if self.municipe_dados:
            self.info_nome.config(text=f"Nome: {self.municipe_dados[1]}")
            self.info_endereco.config(text=f"Endereço: {self.municipe_dados[2]}")
            self.info_bairro.config(text=f"Bairro: {self.municipe_dados[3]}")
            self.info_telefone.config(text=f"Telefone: {self.municipe_dados[4]}")
            self.info_rg.config(text=f"RG: {self.municipe_dados[5]}")
            self.info_titulo_eleitor.config(text=f"Título de Eleitor: {self.municipe_dados[6]}")
            self.info_zona.config(text=f"Zona: {self.municipe_dados[7]}")
            self.info_secao.config(text=f"Seção: {self.municipe_dados[8]}")

    def salvar_atendimento(self):
        if not self.municipe_dados:
            messagebox.showerror("Erro", "Por favor, selecione um munícipe para registrar o atendimento.")
            return

        tipo_pedido = self.tipo_pedido_var.get()
        descricao = self.entrada_descricao.get("1.0", tk.END).strip()
        prioridade = self.prioridade_var.get()

        if tipo_pedido == "Selecione o tipo de pedido" or not descricao:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        self.controller.registrar_atendimento(
            self.municipe_dados[0], tipo_pedido, descricao, "", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.entrada_prazo_resolucao.get(), self.entrada_assessor.get(), prioridade
        )
        messagebox.showinfo("Sucesso", "Atendimento registrado com sucesso!")
        self.switch_view(DashboardView)

# Tela de Registro de Munícipe
class RegistroMunicipeView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Campos de Registro
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entrada_cpf = ttk.Entry(self, width=50)
        self.entrada_cpf.grid(row=0, column=1, pady=2)

        ttk.Label(self, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entrada_nome = ttk.Entry(self, width=50)
        self.entrada_nome.grid(row=1, column=1, pady=2)

        ttk.Label(self, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entrada_endereco = ttk.Entry(self, width=50)
        self.entrada_endereco.grid(row=2, column=1, pady=2)

        # Adicionando o campo Bairro
        ttk.Label(self, text="Bairro:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entrada_bairro = ttk.Entry(self, width=50)
        self.entrada_bairro.grid(row=3, column=1, pady=2)

        ttk.Label(self, text="Telefone:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entrada_telefone = ttk.Entry(self, width=50)
        self.entrada_telefone.grid(row=4, column=1, pady=2)

        ttk.Label(self, text="RG:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entrada_rg = ttk.Entry(self, width=50)
        self.entrada_rg.grid(row=5, column=1, pady=2)

        ttk.Label(self, text="Título de Eleitor:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.entrada_titulo = ttk.Entry(self, width=50)
        self.entrada_titulo.grid(row=6, column=1, pady=2)

        ttk.Label(self, text="Zona:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.entrada_zona = ttk.Entry(self, width=50)
        self.entrada_zona.grid(row=7, column=1, pady=2)

        ttk.Label(self, text="Seção:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.entrada_secao = ttk.Entry(self, width=50)
        self.entrada_secao.grid(row=8, column=1, pady=2)

        # Botões de Ação
        ttk.Button(self, text="Salvar Munícipe", command=self.salvar_municipe).grid(row=9, column=1, sticky=tk.W, pady=10)
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=10, column=1, sticky=tk.W, pady=10)

    def salvar_municipe(self):
        cpf = self.entrada_cpf.get()
        nome = self.entrada_nome.get()
        bairro = self.entrada_bairro.get()
        telefone = self.entrada_telefone.get()
        

        if not (cpf and nome and telefone and bairro):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
            return
        # Registrar o munícipe no banco
        self.controller.registrar_municipe(
            cpf, nome, self.entrada_endereco.get(), bairro, telefone,
            self.entrada_rg.get(), self.entrada_titulo.get(),
            self.entrada_zona.get(), self.entrada_secao.get()
        )
        messagebox.showinfo("Sucesso", "Munícipe registrado com sucesso!")
        self.switch_view(DashboardView)

# Tela de Histórico de Atendimentos
class HistoricoAtendimentoView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Campos de Filtro
        filtro_frame = ttk.Frame(self)
        filtro_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        ttk.Label(filtro_frame, text="Filtrar por Nome:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.filtro_nome = ttk.Entry(filtro_frame, width=30)
        self.filtro_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filtro_frame, text="Filtrar por CPF:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.filtro_cpf = ttk.Entry(filtro_frame, width=30)
        self.filtro_cpf.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filtro_frame, text="Filtrar", command=self.carregar_atendimentos).grid(row=0, column=4, padx=10, pady=5)

        # Tabela Interativa
        tabela_frame = ttk.Frame(self)
        tabela_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.treeview = ttk.Treeview(
            tabela_frame, 
            columns=("ID", "CPF", "Nome", "Tipo de Pedido", "Status", "Prioridade"), 
            show="headings"
        )

        # Configurar cabeçalhos
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("CPF", text="CPF")
        self.treeview.heading("Nome", text="Nome")
        self.treeview.heading("Tipo de Pedido", text="Tipo de Pedido")
        self.treeview.heading("Status", text="Status")
        self.treeview.heading("Prioridade", text="Prioridade")

        # Ajustar larguras
        self.treeview.column("ID", width=50, anchor="center")
        self.treeview.column("CPF", width=120, anchor="center")
        self.treeview.column("Nome", width=150, anchor="w")
        self.treeview.column("Tipo de Pedido", width=150, anchor="w")
        self.treeview.column("Status", width=100, anchor="center")
        self.treeview.column("Prioridade", width=100, anchor="center")

        self.treeview.pack(fill="both", expand=True)

        # Botões de Ação
        botoes_frame = ttk.Frame(self)
        botoes_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        ttk.Button(botoes_frame, text="Editar Atendimento Selecionado", command=self.editar_atendimento).grid(row=0, column=0, padx=5)
        ttk.Button(botoes_frame, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=0, column=1, padx=5)

        # Configurar redimensionamento
        self.grid_rowconfigure(1, weight=1)  # Tabela expande verticalmente
        self.grid_columnconfigure(0, weight=1)  # Layout se ajusta horizontalmente

    def carregar_atendimentos(self):
        filtro_nome = self.filtro_nome.get()
        filtro_cpf = self.filtro_cpf.get()
        atendimentos = self.controller.consultar_atendimentos(filtro_nome, filtro_cpf)

        # Limpar a tabela antes de carregar os dados
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Adicionar dados à tabela
        for atendimento in atendimentos:
            self.treeview.insert("", "end", values=(
                atendimento[0],  # ID
                atendimento[1],  # CPF
                atendimento[2],  # Nome
                atendimento[3],  # Tipo de Pedido
                atendimento[8],  # Status
                atendimento[9]   # Prioridade
            ))

    def editar_atendimento(self):
        try:
            # Obter o item selecionado
            selected_item = self.treeview.selection()[0]
            atendimento_data = self.treeview.item(selected_item)['values']

            # Obter o ID do atendimento
            atendimento_id = atendimento_data[0]

            # Buscar o atendimento pelo ID
            atendimento = next((a for a in self.controller.consultar_atendimentos() if a[0] == atendimento_id), None)

            if atendimento:
                EditarAtendimentoView(self, self.controller, atendimento_id)
            else:
                messagebox.showerror("Erro", "Atendimento não encontrado.")
        except IndexError:
            messagebox.showerror("Erro", "Por favor, selecione um atendimento para editar.")

# Tela de Edição de Atendimento // MUDARR
class EditarAtendimentoView(tk.Toplevel):
    def __init__(self, parent, controller, atendimento_id):
        super().__init__(parent)
        self.controller = controller
        self.atendimento_id = atendimento_id
        self.title("Editar Atendimento")
        self.geometry("600x500")
        self._construir_interface()

    def _construir_interface(self):
        # Recuperar os dados do atendimento
        atendimento = self.controller.consultar_atendimentos()
        atendimento_dados = [a for a in atendimento if a[0] == self.atendimento_id][0]

        # Configuração de layout com espaçamento e alinhamento
        padding_y = 5  # Espaçamento vertical

        # Campo CPF
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=padding_y)
        self.cpf_var = tk.StringVar(value=atendimento_dados[1])  # CPF
        self.entrada_cpf = ttk.Entry(self, textvariable=self.cpf_var, width=50, state='disabled')
        self.entrada_cpf.grid(row=0, column=1, pady=padding_y)

        # Campo Nome
        ttk.Label(self, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=padding_y)
        self.nome_var = tk.StringVar(value=atendimento_dados[2])  # Nome
        self.entrada_nome = ttk.Entry(self, textvariable=self.nome_var, width=50, state='disabled')
        self.entrada_nome.grid(row=1, column=1, pady=padding_y)

        # Campo Tipo de Pedido
        ttk.Label(self, text="Tipo de Pedido:").grid(row=2, column=0, sticky=tk.W, pady=padding_y)
        self.tipo_pedido_var = tk.StringVar(value=atendimento_dados[3])  # Tipo de Pedido
        self.tipo_pedido_dropdown = ttk.Combobox(
            self,
            textvariable=self.tipo_pedido_var,
            values=[
                "Saúde", "Educação", "Segurança", "Transporte", "Cultura",
                "Esporte e Lazer", "Infraestrutura", "Meio Ambiente",
                "Inclusão Social", "Causa Animal", "Outros"
            ],
            state="readonly",
            width=47
        )
        self.tipo_pedido_dropdown.grid(row=2, column=1, pady=padding_y)

        # Campo Descrição
        ttk.Label(self, text="Descrição:").grid(row=3, column=0, sticky=tk.W, pady=padding_y)
        self.descricao_var = tk.StringVar(value=atendimento_dados[4])  # Descrição
        self.entrada_descricao = ttk.Entry(self, textvariable=self.descricao_var, width=50)
        self.entrada_descricao.grid(row=3, column=1, pady=padding_y)

        # Campo Prazo de Resolução
        ttk.Label(self, text="Prazo de Resolução (em dias):").grid(row=4, column=0, sticky=tk.W, pady=padding_y)
        self.prazo_var = tk.StringVar(value=atendimento_dados[6])  # Prazo de Resolução
        self.entrada_prazo = ttk.Entry(self, textvariable=self.prazo_var, width=50)
        self.entrada_prazo.grid(row=4, column=1, pady=padding_y)

        # Campo Assessor Responsável
        ttk.Label(self, text="Assessor Responsável:").grid(row=5, column=0, sticky=tk.W, pady=padding_y)
        self.assessor_var = tk.StringVar(value=atendimento_dados[7])  # Assessor
        self.entrada_assessor = ttk.Entry(self, textvariable=self.assessor_var, width=50)
        self.entrada_assessor.grid(row=5, column=1, pady=padding_y)

        # Campo Status
        ttk.Label(self, text="Status:").grid(row=6, column=0, sticky=tk.W, pady=padding_y)
        self.status_var = tk.StringVar(value=atendimento_dados[8])  # Status
        self.status_dropdown = ttk.Combobox(
            self,
            textvariable=self.status_var,
            values=["Pendente", "Em Andamento", "Concluído"],
            state="readonly",
            width=47
        )
        self.status_dropdown.grid(row=6, column=1, pady=padding_y)

        # Campo Prioridade
        ttk.Label(self, text="Prioridade:").grid(row=7, column=0, sticky=tk.W, pady=padding_y)
        self.prioridade_var = tk.StringVar(value=atendimento_dados[9])  # Prioridade
        self.prioridade_dropdown = ttk.Combobox(
            self,
            textvariable=self.prioridade_var,
            values=["Baixa", "Normal", "Alta"],
            state="readonly",
            width=47
        )
        self.prioridade_dropdown.grid(row=7, column=1, pady=padding_y)

        # Botão para Salvar Alterações
        ttk.Button(self, text="Salvar Alterações", command=self.salvar_alteracoes).grid(row=8, column=1, pady=20)


    def salvar_alteracoes(self):
        cpf = self.cpf_var.get()
        tipo_pedido = self.tipo_pedido_var.get()
        descricao = self.descricao_var.get()
        prazo_resolucao = self.prazo_var.get()
        assessor = self.assessor_var.get()
        status = self.status_var.get()
        prioridade = self.prioridade_var.get()

        if tipo_pedido and tipo_pedido != "Selecione o tipo de pedido":
            self.controller.atualizar_atendimento(
                self.atendimento_id, cpf, tipo_pedido, descricao, status, prazo_resolucao, assessor, prioridade
            )
            messagebox.showinfo("Sucesso", "Atendimento atualizado com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

# Tela de Edição de Munícipe
class EditarMunicipeView(tk.Toplevel):
    def __init__(self, parent, controller, municipe_dados):
        super().__init__(parent)
        self.controller = controller
        self.cpf = municipe_dados[0]  # O CPF é o identificador principal
        self.title("Editar Munícipe")
        self.geometry("500x600")
        self._construir_interface(municipe_dados)

    def _construir_interface(self, municipe_dados):
        # Campo CPF (desabilitado para edição)
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cpf_var = tk.StringVar(value=municipe_dados[0])
        self.entrada_cpf = ttk.Entry(self, textvariable=self.cpf_var, width=50, state='disabled')  # CPF não é editável
        self.entrada_cpf.grid(row=0, column=1, pady=5)

        # Campo Nome
        ttk.Label(self, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nome_var = tk.StringVar(value=municipe_dados[1])
        self.entrada_nome = ttk.Entry(self, textvariable=self.nome_var, width=50)
        self.entrada_nome.grid(row=1, column=1, pady=5)

        # Campo Endereço
        ttk.Label(self, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.endereco_var = tk.StringVar(value=municipe_dados[2])
        self.entrada_endereco = ttk.Entry(self, textvariable=self.endereco_var, width=50)
        self.entrada_endereco.grid(row=2, column=1, pady=5)

        # Campo Bairro
        ttk.Label(self, text="Bairro:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.bairro_var = tk.StringVar(value=municipe_dados[3])
        self.entrada_bairro = ttk.Entry(self, textvariable=self.bairro_var, width=50)
        self.entrada_bairro.grid(row=3, column=1, pady=5)

        # Campo Telefone
        ttk.Label(self, text="Telefone:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.telefone_var = tk.StringVar(value=municipe_dados[4])
        self.entrada_telefone = ttk.Entry(self, textvariable=self.telefone_var, width=50)
        self.entrada_telefone.grid(row=4, column=1, pady=5)

        # Campo RG
        ttk.Label(self, text="RG:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.rg_var = tk.StringVar(value=municipe_dados[5])
        self.entrada_rg = ttk.Entry(self, textvariable=self.rg_var, width=50)
        self.entrada_rg.grid(row=5, column=1, pady=5)

        # Campo Título de Eleitor
        ttk.Label(self, text="Título de Eleitor:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.titulo_var = tk.StringVar(value=municipe_dados[6])
        self.entrada_titulo = ttk.Entry(self, textvariable=self.titulo_var, width=50)
        self.entrada_titulo.grid(row=6, column=1, pady=5)

        # Campo Zona
        ttk.Label(self, text="Zona:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.zona_var = tk.StringVar(value=municipe_dados[7])
        self.entrada_zona = ttk.Entry(self, textvariable=self.zona_var, width=50)
        self.entrada_zona.grid(row=7, column=1, pady=5)

        # Campo Seção (corrigir para estar habilitado)
        ttk.Label(self, text="Seção:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.secao_var = tk.StringVar(value=municipe_dados[8])
        self.entrada_secao = ttk.Entry(self, textvariable=self.secao_var, width=50)
        self.entrada_secao.grid(row=8, column=1, pady=5)

        # Botão para Salvar Alterações
        ttk.Button(self, text="Salvar Alterações", command=self.salvar_alteracoes).grid(row=9, column=1, pady=20, sticky=tk.E)

    def salvar_alteracoes(self):
        # Recuperar os dados atualizados dos campos
        nome = self.nome_var.get()
        endereco = self.endereco_var.get()
        bairro = self.bairro_var.get()
        telefone = self.telefone_var.get()
        rg = self.rg_var.get()
        titulo_eleitor = self.titulo_var.get()
        zona = self.zona_var.get()
        secao = self.secao_var.get()

        # Validar campos obrigatórios
        if nome and telefone and bairro:
            # Atualizar no banco de dados
            self.controller.atualizar_municipe(self.cpf, nome, endereco, bairro, telefone, rg, titulo_eleitor, zona, secao)
            messagebox.showinfo("Sucesso", "Munícipe atualizado com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

# Tela de Histórico de Munícipes
class HistoricoMunicipeView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Tabela Interativa
        self.treeview = ttk.Treeview(self, columns=("CPF", "Nome", "Endereço", "Bairro","Telefone", "RG", "Título", "Zona", "Seção"), show="headings")
        self.treeview.heading("CPF", text="CPF")
        self.treeview.heading("Nome", text="Nome")
        self.treeview.heading("Endereço", text="Endereço")
        self.treeview.heading("Bairro", text="Bairro")
        self.treeview.heading("Telefone", text="Telefone")
        self.treeview.heading("RG", text="RG")
        self.treeview.heading("Título", text="Título de Eleitor")
        self.treeview.heading("Zona", text="Zona")
        self.treeview.heading("Seção", text="Seção")
        self.treeview.pack(fill="both", expand=True)

        # Botões de Ação
        ttk.Button(self, text="Editar Munícipe Selecionado", command=self.editar_municipe).pack(pady=10)
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).pack(pady=10)

        # Carregar Munícipes
        self.carregar_municipes()

    def carregar_municipes(self):
        municipes = self.controller.consultar_municipes()
        for municipe in municipes:
            self.treeview.insert("", "end", values=municipe)

    def editar_municipe(self):
        try:
            # Obter o item selecionado na tabela
            selected_item = self.treeview.selection()[0]
            municipe_data = self.treeview.item(selected_item)['values']  # Pega os valores do munícipe

            if municipe_data:
                # Passar os dados do munícipe para a janela de edição
                EditarMunicipeView(self, self.controller, municipe_data)
            else:
                messagebox.showerror("Erro", "Munícipe não encontrado.")
        except IndexError:
            messagebox.showerror("Erro", "Por favor, selecione um munícipe para editar.")



class DashboardView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Estrutura principal: Divisão em três frames (menu, indicadores e tabela)
        menu_frame = ttk.Frame(self, width=200)
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Menu lateral com botões
        ttk.Label(menu_frame, text="Menu", font=("Helvetica", 16)).pack(pady=10)
        
        ttk.Button(menu_frame, text="Registrar Atendimento", command=lambda: self.switch_view(RegistroAtendimentoView)).pack(fill="x", pady=5)
        ttk.Button(menu_frame, text="Registrar Munícipe", command=lambda: self.switch_view(RegistroMunicipeView)).pack(fill="x", pady=5)
        ttk.Button(menu_frame, text="Histórico de Atendimentos", command=lambda: self.switch_view(HistoricoAtendimentoView)).pack(fill="x", pady=5)
        ttk.Button(menu_frame, text="Histórico de Munícipes", command=lambda: self.switch_view(HistoricoMunicipeView)).pack(fill="x", pady=5)
        ttk.Button(menu_frame, text="Gerar Relatório", command=lambda: self.switch_view(RelatorioView)).pack(fill="x", pady=5)
        ttk.Button(menu_frame, text="Gerenciar Tarefas", command=lambda: self.switch_view(TarefasView)).pack(fill="x", pady=5)

        # Indicadores de resumo no topo do frame principal
        resumo_frame = ttk.Frame(main_frame)
        resumo_frame.grid(row=0, column=0, sticky="ew", pady=10)

        ttk.Label(resumo_frame, text="Resumo", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        atendimentos_abertos = ttk.Label(
            resumo_frame, text="Atendimentos Abertos: 5", font=("Helvetica", 14), foreground="red"
        )
        atendimentos_abertos.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        tarefas_pendentes = ttk.Label(
            resumo_frame, text="Tarefas Pendentes: 3", font=("Helvetica", 14), foreground="orange"
        )
        tarefas_pendentes.grid(row=1, column=1, padx=10, pady=5, sticky="e")

        # Tabela interativa no centro
        tabela_frame = ttk.Frame(main_frame)
        tabela_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.treeview = ttk.Treeview(
            tabela_frame, 
            columns=("ID", "Nome", "Tipo de Pedido", "Status", "Prioridade"), 
            show="headings"
        )

        # Configurar cabeçalhos da tabela
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("Nome", text="Nome")
        self.treeview.heading("Tipo de Pedido", text="Tipo de Pedido")
        self.treeview.heading("Status", text="Status")
        self.treeview.heading("Prioridade", text="Prioridade")

        # Configurar largura das colunas
        self.treeview.column("ID", width=50, anchor="center")
        self.treeview.column("Nome", width=150, anchor="w")
        self.treeview.column("Tipo de Pedido", width=200, anchor="w")
        self.treeview.column("Status", width=100, anchor="center")
        self.treeview.column("Prioridade", width=100, anchor="center")

        # Adicionar tabela à tela
        self.treeview.pack(fill="both", expand=True)

        # Configuração para redimensionamento
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Carregar os atendimentos no Dashboard
        self.carregar_atendimentos()

    def carregar_atendimentos(self):
        # Consultar todos os atendimentos sem filtros
        atendimentos = self.controller.consultar_atendimentos()

        # Limpar a tabela antes de carregar os dados
        self.treeview.delete(*self.treeview.get_children())

        # Adicionar dados à tabela do Dashboard
        for atendimento in atendimentos:
            self.treeview.insert(
                "",
                "end",
                values=(
                    atendimento[0],  # ID do atendimento
                    atendimento[2],  # Nome do munícipe
                    atendimento[3],  # Tipo de pedido
                    atendimento[8],  # Status do atendimento
                    atendimento[9],  # Prioridade do atendimento
                )
            )

# Tela de Relatórios
class RelatorioView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self.municipe_info_labels = {}
        self._construir_interface()

    def _construir_interface(self):
        # Layout principal dividido em duas colunas
        left_frame = ttk.Frame(self, width=400)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        right_frame = ttk.Frame(self, width=400)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # ===================== Left Frame =====================
        ttk.Label(left_frame, text="Relatórios", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=3, pady=10)

        # Opção de Relatório por CPF
        ttk.Label(left_frame, text="Relatório por CPF:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entrada_cpf = ttk.Entry(left_frame, width=30)
        self.entrada_cpf.grid(row=1, column=1, pady=2)
        ttk.Button(left_frame, text="Gerar", command=self.gerar_relatorio_cpf).grid(row=1, column=2, pady=2)

        # Botão para Buscar Munícipe
        ttk.Button(left_frame, text="Buscar Munícipe", command=self.buscar_municipe).grid(row=2, column=1, pady=5)

        # Opção de Relatório por Tipo de Pedido
        ttk.Label(left_frame, text="Relatório por Tipo de Pedido:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.tipo_pedido_var = tk.StringVar()
        self.tipo_pedido_dropdown = ttk.Combobox(left_frame, textvariable=self.tipo_pedido_var, values=[
            "Saúde", "Educação", "Segurança", "Transporte", "Cultura", "Esporte e Lazer",
            "Infraestrutura", "Meio Ambiente", "Inclusão Social", "Causa Animal", "Outros"
        ], state="readonly", width=27)
        self.tipo_pedido_dropdown.grid(row=3, column=1, pady=2)
        ttk.Button(left_frame, text="Gerar", command=self.gerar_relatorio_tipo_pedido).grid(row=3, column=2, pady=2)

        # Opção de Relatório por Bairro
        ttk.Label(left_frame, text="Relatório por Bairro:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entrada_bairro = ttk.Entry(left_frame, width=30)
        self.entrada_bairro.grid(row=4, column=1, pady=2)
        ttk.Button(left_frame, text="Gerar", command=self.gerar_relatorio_bairro).grid(row=4, column=2, pady=2)

        # Botão para Gerar Todos os Relatórios
        ttk.Button(left_frame, text="Gerar Todos os Relatórios", command=self.gerar_todos_relatorios).grid(row=5, column=1, pady=10)

        # Botão para Voltar ao Dashboard
        ttk.Button(left_frame, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=6, column=1, pady=10)

        # ===================== Right Frame =====================
        ttk.Label(right_frame, text="Informações do Munícipe", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        # Criando os labels de informações do munícipe
        labels = ["CPF", "Nome", "Endereço", "Bairro", "Telefone", "RG", "Título de Eleitor", "Zona", "Seção"]
        for i, label_text in enumerate(labels):
            ttk.Label(right_frame, text=f"{label_text}:").grid(row=i + 1, column=0, sticky=tk.W, pady=2)
            self.municipe_info_labels[label_text] = ttk.Label(right_frame, text="N/A", font=("Helvetica", 10))
            self.municipe_info_labels[label_text].grid(row=i + 1, column=1, sticky=tk.W, pady=2)

    def gerar_relatorio_cpf(self):
        cpf = self.entrada_cpf.get()
        if cpf:
            atendimentos = self.controller.gerar_relatorio_municipe(cpf)
            if atendimentos:
                municipe_dados = self.controller.buscar_municipe_por_cpf(cpf)
                if municipe_dados:
                    self.atualizar_informacoes_municipe(municipe_dados)
                else:
                    self.limpar_informacoes_municipe()
                self.controller.gerar_relatorio_pdf(atendimentos, caminho_pdf=f"relatorio_{cpf}.pdf")
                messagebox.showinfo("Relatório", f"Relatório gerado para o CPF {cpf}.")
            else:
                messagebox.showerror("Erro", "Nenhum atendimento encontrado para o CPF fornecido.")
                self.limpar_informacoes_municipe()
        else:
            messagebox.showerror("Erro", "Por favor, insira o CPF.")

    def gerar_relatorio_tipo_pedido(self):
        tipo_pedido = self.tipo_pedido_var.get()
        if tipo_pedido:
            atendimentos = self.controller.gerar_relatorio_tipo_pedido(tipo_pedido)
            if atendimentos:
                self.controller.gerar_relatorio_pdf(atendimentos, caminho_pdf=f"relatorio_{tipo_pedido}.pdf")
                messagebox.showinfo("Relatório", f"Relatório gerado para o tipo de pedido {tipo_pedido}.")
            else:
                messagebox.showerror("Erro", "Nenhum atendimento encontrado para o tipo de pedido selecionado.")
        else:
            messagebox.showerror("Erro", "Por favor, selecione um tipo de pedido.")

    def gerar_relatorio_bairro(self):
        bairro = self.entrada_bairro.get()
        if bairro:
            atendimentos = self.controller.gerar_relatorio_bairro(bairro)
            if atendimentos:
                self.controller.gerar_relatorio_pdf(atendimentos, caminho_pdf=f"relatorio_{bairro}.pdf")
                messagebox.showinfo("Relatório", f"Relatório gerado para o bairro {bairro}.")
            else:
                messagebox.showerror("Erro", "Nenhum atendimento encontrado para o bairro fornecido.")
        else:
            messagebox.showerror("Erro", "Por favor, insira o bairro.")

    def gerar_todos_relatorios(self):
        atendimentos = self.controller.consultar_todos_atendimentos()
        if atendimentos:
            self.controller.gerar_relatorio_pdf(atendimentos, caminho_pdf="relatorio_completo.pdf")
            messagebox.showinfo("Relatório", "Relatório completo gerado com sucesso.")
        else:
            messagebox.showerror("Erro", "Nenhum atendimento encontrado.")

    def buscar_municipe(self):
        cpf = self.entrada_cpf.get()
        if cpf:
            municipe_dados = self.controller.buscar_municipe_por_cpf(cpf)
            if municipe_dados:
                self.atualizar_informacoes_municipe(municipe_dados)
            else:
                messagebox.showerror("Erro", "Nenhum munícipe encontrado com o CPF fornecido.")
        else:
            messagebox.showerror("Erro", "Por favor, insira o CPF para buscar o munícipe.")

    def atualizar_informacoes_municipe(self, municipe_dados):
        campos = ["CPF", "Nome", "Endereço", "Bairro", "Telefone", "RG", "Título de Eleitor", "Zona", "Seção"]
        for i, campo in enumerate(campos):
            self.municipe_info_labels[campo].config(text=municipe_dados[i])

    def limpar_informacoes_municipe(self):
        for label in self.municipe_info_labels.values():
            label.config(text="N/A")

# Tela de Gerenciamento de Tarefas (Kanban)
class TarefasView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        ttk.Label(self, text="Tarefas - Kanban View").pack()
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).pack(pady=10)

# MainApplication - Classe Principal que gerencia a navegação
class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x600")
        self.root.title("Sistema de Atendimento ao Gabinete")
        self.model = AtendimentoModel()
        self.controller = AtendimentoController(self.model)
        self.current_view = None
        self.switch_view(DashboardView)

    def switch_view(self, view_class):
        # Remove a view atual e cria a nova view
        if self.current_view is not None:
            self.current_view.pack_forget()
        self.current_view = view_class(self.root, self.controller, self.switch_view)
        self.current_view.pack(fill="both", expand=True)

# Inicialização da Aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
