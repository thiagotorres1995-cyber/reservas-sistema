# -*- coding: utf-8 -*-
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json

class SistemaReservasDB:
    def __init__(self):
        self.db_path = "reservas.db"
        self.init_db()
        self.suites = self._inicializar_suites()
        self.tipos_suite = {
            "Suite com varanda": ["201", "202", "203", "204"],
            "Suite família": ["303", "304"],
            "Suite casal": ["301", "205"],
            "Suite deficiente": ["101"]
        }

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id TEXT PRIMARY KEY,
                data_reserva TEXT,
                origem TEXT,
                destino TEXT,
                data_viagem TEXT,
                suite_tipo TEXT,
                suite_numero TEXT,
                passageiros TEXT,
                telefone TEXT,
                valor_total REAL,
                valor_entrada REAL,
                forma_pagamento TEXT,
                data_pagamento TEXT,
                status TEXT DEFAULT 'confirmada'
            )
        ''')
        conn.commit()
        conn.close()

    def _inicializar_suites(self):
        return {
            "201": {"tipo": "Suite com varanda", "valor": 1200, "varanda": True},
            "202": {"tipo": "Suite com varanda", "valor": 1200, "varanda": True},
            "203": {"tipo": "Suite com varanda", "valor": 1200, "varanda": True},
            "204": {"tipo": "Suite com varanda", "valor": 1200, "varanda": True},
            "303": {"tipo": "Suite família", "valor": 1000, "varanda": False},
            "304": {"tipo": "Suite família", "valor": 1000, "varanda": False},
            "301": {"tipo": "Suite casal", "valor": 900, "varanda": False},
            "205": {"tipo": "Suite casal", "valor": 900, "varanda": False},
            "101": {"tipo": "Suite deficiente", "valor": 800, "varanda": False, "acessivel": True}
        }

    def fazer_reserva(self, dados):
        novo_id = str(int(datetime.now().timestamp()))
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reservas (id, data_reserva, origem, destino, data_viagem, suite_tipo, suite_numero,
                                passageiros, telefone, valor_total, valor_entrada, forma_pagamento, data_pagamento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            novo_id,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            dados['origem'], dados['destino'], dados['data_viagem'],
            dados['suite_tipo'], dados['suite_numero'],
            json.dumps(dados['passageiros']),
            dados['telefone'], dados['valor_total'], dados['valor_entrada'],
            dados['forma_pagamento'], dados['data_pagamento']
        ))
        conn.commit()
        conn.close()
        return True, novo_id

    def listar_reservas_ordenadas(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM reservas WHERE status = "confirmada"
            ORDER BY DATE(SUBSTR(data_viagem, 7, 4) || "-" || SUBSTR(data_viagem, 4, 2) || "-" || SUBSTR(data_viagem, 1, 2))
        ''')
        reservas = cursor.fetchall()
        conn.close()
        return [
            {
                'id': r[0],
                'data_reserva': r[1],
                'origem': r[2],
                'destino': r[3],
                'data_viagem': r[4],
                'suite_tipo': r[5],
                'suite_numero': r[6],
                'passageiros': json.loads(r[7]),
                'telefone': r[8],
                'valor_total': r[9],
                'valor_entrada': r[10],
                'forma_pagamento': r[11],
                'data_pagamento': r[12]
            }
            for r in reservas
        ]

    def verificar_disponibilidade(self, data, suite_tipo):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT suite_numero FROM reservas
            WHERE data_viagem = ? AND status = "confirmada"
        ''', (data,))
        ocupadas = {r[0] for r in cursor.fetchall()}
        conn.close()
        todos = self.tipos_suite.get(suite_tipo, [])
        return [num for num in todos if num not in ocupadas]

    def cancelar_reserva(self, reserva_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE reservas SET status = "cancelada" WHERE id = ?', (reserva_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

class ReservaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚢 F/B Leão de Judá X – Sistema de Reservas")
        self.root.geometry("1000x700")
        self.db = SistemaReservasDB()
        self.create_notebook()

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # ABA 1: Nova Reserva
        self.aba_nova = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_nova, text="Nova Reserva")
        self.create_nova_reserva()

        # ABA 2: Ver Disponibilidade
        self.aba_disp = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_disp, text="Ver Disponibilidade")
        self.create_disponibilidade()

        # ABA 3: Lista de Reservas
        self.aba_lista = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_lista, text="Lista de Reservas")
        self.create_lista_reservas()

    # ================= ABA 1: Nova Reserva =================
    def create_nova_reserva(self):
        frame = ttk.LabelFrame(self.aba_nova, text="Nova Reserva", padding=15)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Linha 1
        ttk.Label(frame, text="Origem:").grid(row=0, column=0, sticky='w')
        self.origem_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.origem_var,
                     values=["Manaus", "Codajás", "Coari", "Tefé", "Alvarães", "Uarini"],
                     state='readonly', width=15).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Destino:").grid(row=0, column=2, sticky='w')
        self.destino_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.destino_var,
                     values=["Manaus", "Codajás", "Coari", "Tefé", "Alvarães", "Uarini"],
                     state='readonly', width=15).grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Data Viagem:").grid(row=0, column=4, sticky='w')
        self.data_viagem = DateEntry(frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.data_viagem.grid(row=0, column=5, padx=5)

        # Linha 2 – TIPO depois NÚMERO
        ttk.Label(frame, text="Tipo Suite:").grid(row=1, column=0, sticky='w')
        self.tipo_suite_var = tk.StringVar()
        self.tipo_combo = ttk.Combobox(frame, textvariable=self.tipo_suite_var,
                                       values=list(self.db.tipos_suite.keys()),
                                       state='readonly', width=18)
        self.tipo_combo.grid(row=1, column=1, padx=5)
        self.tipo_combo.bind("<<ComboboxSelected>>", self.atualizar_numeros)

        ttk.Label(frame, text="Número:").grid(row=1, column=2, sticky='w')
        self.numero_var = tk.StringVar()
        self.numero_combo = ttk.Combobox(frame, textvariable=self.numero_var,
                                         state='readonly', width=10)
        self.numero_combo.grid(row=1, column=3, padx=5)

        # Passageiros
        pass_frame = ttk.LabelFrame(frame, text="Passageiros", padding=5)
        pass_frame.grid(row=2, column=0, columnspan=6, sticky='nsew', pady=10)
        self.passageiros_tree = ttk.Treeview(pass_frame, columns=("Nome", "Nascimento"), show='headings', height=5)
        self.passageiros_tree.heading("Nome", text="Nome")
        self.passageiros_tree.heading("Nascimento", text="Data Nascimento")
        self.passageiros_tree.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(pass_frame, orient='vertical', command=self.passageiros_tree.yview)
        scroll.pack(side='right', fill='y')
        self.passageiros_tree.configure(yscrollcommand=scroll.set)

        btn_frame = ttk.Frame(pass_frame)
        btn_frame.pack(side='right', padx=5)
        ttk.Button(btn_frame, text="+", command=self.adicionar_passageiro).pack()
        ttk.Button(btn_frame, text="-", command=self.remover_passageiro).pack()

        # Contato e valores
        ttk.Label(frame, text="Telefone:").grid(row=3, column=0, sticky='w')
        self.telefone_entry = ttk.Entry(frame, width=15)
        self.telefone_entry.grid(row=3, column=1)

        ttk.Label(frame, text="Valor Total (R$):").grid(row=3, column=2, sticky='w')
        self.valor_total_entry = ttk.Entry(frame, width=12)
        self.valor_total_entry.grid(row=3, column=3)

        ttk.Label(frame, text="Valor Entrada (R$):").grid(row=3, column=4, sticky='w')
        self.valor_entrada_entry = ttk.Entry(frame, width=12)
        self.valor_entrada_entry.grid(row=3, column=5)

        # Forma de pagamento
        ttk.Label(frame, text="Forma de Pagamento:").grid(row=4, column=0, sticky='w')
        self.forma_pagamento_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.forma_pagamento_var,
                     values=["Pix", "Débito", "Crédito", "Dinheiro"],
                     state='readonly', width=12).grid(row=4, column=1)

        ttk.Label(frame, text="Data Pagamento:").grid(row=4, column=2, sticky='w')
        self.data_pagamento = DateEntry(frame, width=12, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.data_pagamento.grid(row=4, column=3)

        # Botão final
        ttk.Button(frame, text="Confirmar Reserva", command=self.confirmar_reserva).grid(row=5, column=0, columnspan=6, pady=15)

    # ================= ABA 2: Ver Disponibilidade =================
    def create_disponibilidade(self):
        frame = ttk.LabelFrame(self.aba_disp, text="Ver Disponibilidade", padding=15)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Data Viagem:").grid(row=0, column=0, sticky='w')
        self.disp_data = DateEntry(frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.disp_data.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Tipo de Suite:").grid(row=0, column=2, sticky='w')
        self.disp_tipo_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.disp_tipo_var,
                     values=list(self.db.tipos_suite.keys()),
                     state='readonly').grid(row=0, column=3, padx=5)

        ttk.Button(frame, text="Verificar", command=self.mostrar_disponibilidade).grid(row=0, column=4, padx=10)

        # Tree com detalhes de CADA suíte
        self.disp_tree = ttk.Treeview(frame, columns=("Tipo", "Número", "Valor", "Varanda", "Acessível"), show='headings', height=12)
        for col in ("Tipo", "Número", "Valor", "Varanda", "Acessível"):
            self.disp_tree.heading(col, text=col)
        self.disp_tree.grid(row=1, column=0, columnspan=5, sticky='nsew', pady=10)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.disp_tree.yview)
        scroll.grid(row=1, column=5, sticky='ns')
        self.disp_tree.configure(yscrollcommand=scroll.set)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

    # ================= ABA 3: Lista de Reservas =================
    def create_lista_reservas(self):
        frame = ttk.LabelFrame(self.aba_lista, text="Reservas (próximas primeiro)", padding=15)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.lista_tree = ttk.Treeview(frame, columns=("ID", "Origem", "Destino", "Data", "Suite", "Passageiros", "Valor", "Pagamento"), show='headings')
        for col in ("ID", "Origem", "Destino", "Data", "Suite", "Passageiros", "Valor", "Pagamento"):
            self.lista_tree.heading(col, text=col)
            self.lista_tree.column(col, width=90 if col != "Suite" else 150)
        self.lista_tree.pack(fill='both', expand=True)

        ttk.Button(frame, text="Atualizar Lista", command=self.carregar_lista_reservas).pack(pady=5)
        ttk.Button(frame, text="Cancelar Reserva Selecionada", command=self.cancelar_reserva_lista).pack()

    # ================= Métodos Auxiliares =================
    def atualizar_numeros(self, event=None):
        tipo = self.tipo_suite_var.get()
        numeros = self.db.tipos_suite.get(tipo, [])
        self.numero_combo['values'] = numeros
        if numeros:
            self.numero_combo.current(0)
        else:
            self.numero_combo.set('')

    def adicionar_passageiro(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Passageiro")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Nome:").pack()
        nome_entry = ttk.Entry(dialog)
        nome_entry.pack()

        ttk.Label(dialog, text="Data Nascimento:").pack()
        nasc_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', date_pattern='dd/mm/yyyy')
        nasc_entry.pack()

        def salvar():
            nome = nome_entry.get().strip()
            nasc = nasc_entry.get()
            if nome:
                self.passageiros_tree.insert('', 'end', values=(nome, nasc))
                dialog.destroy()
            else:
                messagebox.showwarning("Atenção", "Informe o nome")

        ttk.Button(dialog, text="Salvar", command=salvar).pack(pady=10)

    def remover_passageiro(self):
        selected = self.passageiros_tree.selection()
        if selected:
            self.passageiros_tree.delete(selected)

    def confirmar_reserva(self):
        data = self.data_viagem.get()
        origem = self.origem_var.get()
        destino = self.destino_var.get()
        tipo_suite = self.tipo_suite_var.get()
        numero = self.numero_var.get()

        if not all([origem, destino, data, tipo_suite, numero]):
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios")
            return

        passageiros = []
        for item in self.passageiros_tree.get_children():
            vals = self.passageiros_tree.item(item)['values']
            passageiros.append({"nome": vals[0], "nascimento": vals[1]})
        if not passageiros:
            messagebox.showwarning("Atenção", "Adicione pelo menos um passageiro")
            return

        try:
            valor_total = float(self.valor_total_entry.get())
            valor_entrada = float(self.valor_entrada_entry.get())
            forma = self.forma_pagamento_var.get()
            data_pag = self.data_pagamento.get()
        except ValueError:
            messagebox.showwarning("Atenção", "Valores inválidos")
            return

        dados = {
            'origem': origem, 'destino': destino, 'data_viagem': data,
            'suite_tipo': tipo_suite, 'suite_numero': numero,
            'passageiros': passageiros, 'telefone': self.telefone_entry.get(),
            'valor_total': valor_total, 'valor_entrada': valor_entrada,
            'forma_pagamento': forma, 'data_pagamento': data_pag
        }

        ok, rid = self.db.fazer_reserva(dados)
        if ok:
            messagebox.showinfo("Sucesso", f"Reserva confirmada!\nID: {rid}")
            self.atualizar_numeros()
            self.carregar_lista_reservas()
        else:
            messagebox.showerror("Erro", "Erro ao salvar reserva")

    def mostrar_disponibilidade(self):
        data = self.disp_data.get()
        tipo = self.disp_tipo_var.get()
        if not (data and tipo):
            messagebox.showwarning("Atenção", "Selecione data e tipo de suite")
            return

        for item in self.disp_tree.get_children():
            self.disp_tree.delete(item)

        disponiveis = self.db.verificar_disponibilidade(data, tipo)
        if disponiveis:
            for num in disponiveis:
                info = self.db.suites[num]
                self.disp_tree.insert('', 'end', values=(
                    info['tipo'], num, f"R$ {info['valor']:.2f}",
                    "Sim" if info.get('varanda') else "Não",
                    "Sim" if info.get('acessivel') else "Não"
                ))
        else:
            self.disp_tree.insert('', 'end', values=("---", "Sem disponibilidade", "---", "---", "---"))

    def carregar_lista_reservas(self):
        reservas = self.db.listar_reservas_ordenadas()
        for item in self.lista_tree.get_children():
            self.lista_tree.delete(item)

        for r in reservas:
            self.lista_tree.insert('', 'end', values=(
                r['id'], r['origem'], r['destino'], r['data_viagem'],
                f"{r['suite_tipo']} {r['suite_numero']}",
                len(r['passageiros']), f"R$ {r['valor_total']:.2f}", r['forma_pagamento']
            ))

    def cancelar_reserva_lista(self):
        selected = self.lista_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma reserva")
            return
        rid = self.lista_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"Cancelar reserva {rid}?"):
            if self.db.cancelar_reserva(rid):
                messagebox.showinfo("Sucesso", "Cancelado!")
                self.carregar_lista_reservas()
                self.atualizar_numeros()
            else:
                messagebox.showerror("Erro", "Erro ao cancelar")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservaApp(root)
    root.mainloop()