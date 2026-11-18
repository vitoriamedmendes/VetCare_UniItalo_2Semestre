from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vetcare.db"

app = Flask(__name__)
app.secret_key = "vetcare-chave-local-altere-antes-de-publicar"

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar_banco():
    with conectar() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS animais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            idade INTEGER,
            sexo TEXT,
            tutor TEXT NOT NULL,
            telefone TEXT,
            observacoes TEXT,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            preco REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            data_atendimento TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Concluído',
            FOREIGN KEY (animal_id) REFERENCES animais(id) ON DELETE RESTRICT
        );
        """)
        quantidade = conn.execute("SELECT COUNT(*) FROM servicos").fetchone()[0]
        if quantidade == 0:
            conn.executemany(
                "INSERT INTO servicos (nome, descricao, preco) VALUES (?, ?, ?)",
                [
                    ("Consulta veterinária", "Avaliação clínica geral", 120.00),
                    ("Vacinação", "Aplicação de vacina", 85.00),
                    ("Banho", "Higiene e cuidados", 60.00),
                    ("Exame", "Exame laboratorial ou de imagem", 150.00),
                    ("Retorno", "Reavaliação do animal", 0.00),
                ],
            )

@app.route("/")
def inicio():
    with conectar() as conn:
        total_animais = conn.execute("SELECT COUNT(*) FROM animais").fetchone()[0]
        total_atendimentos = conn.execute("SELECT COUNT(*) FROM atendimentos").fetchone()[0]
        faturamento = conn.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM atendimentos WHERE status = 'Concluído'"
        ).fetchone()[0]
        ultimos = conn.execute("""
            SELECT a.id, a.data_atendimento, a.tipo, a.status, an.nome AS animal
            FROM atendimentos a JOIN animais an ON an.id = a.animal_id
            ORDER BY a.data_atendimento DESC, a.id DESC LIMIT 5
        """).fetchall()
    return render_template("index.html", total_animais=total_animais,
                           total_atendimentos=total_atendimentos,
                           faturamento=faturamento, ultimos=ultimos)

@app.route("/animais")
def animais():
    termo = request.args.get("q", "").strip()
    with conectar() as conn:
        if termo:
            lista = conn.execute("""
                SELECT * FROM animais
                WHERE nome LIKE ? OR tutor LIKE ? OR especie LIKE ?
                ORDER BY nome
            """, (f"%{termo}%", f"%{termo}%", f"%{termo}%")).fetchall()
        else:
            lista = conn.execute("SELECT * FROM animais ORDER BY nome").fetchall()
    return render_template("animais.html", animais=lista, q=termo)

@app.route("/animais/novo", methods=["GET", "POST"])
def novo_animal():
    if request.method == "POST":
        dados = (
            request.form.get("nome", "").strip(),
            request.form.get("especie", "").strip(),
            request.form.get("raca", "").strip(),
            request.form.get("idade") or None,
            request.form.get("sexo", ""),
            request.form.get("tutor", "").strip(),
            request.form.get("telefone", "").strip(),
            request.form.get("observacoes", "").strip(),
        )
        if not dados[0] or not dados[1] or not dados[5]:
            flash("Preencha nome, espécie e nome do tutor.", "erro")
            return render_template("animal_form.html", animal=None)
        with conectar() as conn:
            conn.execute("""
                INSERT INTO animais
                (nome, especie, raca, idade, sexo, tutor, telefone, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, dados)
        flash("Animal cadastrado com sucesso!", "sucesso")
        return redirect(url_for("animais"))
    return render_template("animal_form.html", animal=None)

@app.route("/animais/<int:animal_id>/editar", methods=["GET", "POST"])
def editar_animal(animal_id):
    with conectar() as conn:
        animal = conn.execute("SELECT * FROM animais WHERE id = ?", (animal_id,)).fetchone()
        if animal is None:
            flash("Animal não encontrado.", "erro")
            return redirect(url_for("animais"))
        if request.method == "POST":
            dados = (
                request.form.get("nome", "").strip(),
                request.form.get("especie", "").strip(),
                request.form.get("raca", "").strip(),
                request.form.get("idade") or None,
                request.form.get("sexo", ""),
                request.form.get("tutor", "").strip(),
                request.form.get("telefone", "").strip(),
                request.form.get("observacoes", "").strip(),
                animal_id,
            )
            if not dados[0] or not dados[1] or not dados[5]:
                flash("Preencha nome, espécie e nome do tutor.", "erro")
                return render_template("animal_form.html", animal=animal)
            conn.execute("""
                UPDATE animais SET nome=?, especie=?, raca=?, idade=?, sexo=?,
                tutor=?, telefone=?, observacoes=? WHERE id=?
            """, dados)
            flash("Cadastro atualizado com sucesso!", "sucesso")
            return redirect(url_for("animais"))
    return render_template("animal_form.html", animal=animal)

@app.post("/animais/<int:animal_id>/excluir")
def excluir_animal(animal_id):
    with conectar() as conn:
        possui = conn.execute(
            "SELECT COUNT(*) FROM atendimentos WHERE animal_id=?", (animal_id,)
        ).fetchone()[0]
        if possui:
            flash("Não é possível excluir: este animal possui atendimentos registrados. Mantenha o histórico.", "erro")
        else:
            conn.execute("DELETE FROM animais WHERE id=?", (animal_id,))
            flash("Cadastro excluído.", "sucesso")
    return redirect(url_for("animais"))

@app.route("/atendimentos", methods=["GET", "POST"])
def atendimentos():
    if request.method == "POST":
        animal_id = request.form.get("animal_id")
        data_atendimento = request.form.get("data_atendimento")
        tipo = request.form.get("tipo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        try:
            valor = float(request.form.get("valor", "0").replace(",", "."))
        except ValueError:
            valor = -1
        if not animal_id or not data_atendimento or not tipo or valor < 0:
            flash("Confira os campos do atendimento e informe um valor válido.", "erro")
        else:
            with conectar() as conn:
                existe = conn.execute("SELECT id FROM animais WHERE id=?", (animal_id,)).fetchone()
                if existe:
                    conn.execute("""
                        INSERT INTO atendimentos
                        (animal_id, data_atendimento, tipo, descricao, valor)
                        VALUES (?, ?, ?, ?, ?)
                    """, (animal_id, data_atendimento, tipo, descricao, valor))
                    flash("Atendimento registrado!", "sucesso")
                else:
                    flash("Selecione um animal cadastrado.", "erro")
        return redirect(url_for("atendimentos"))

    with conectar() as conn:
        lista_animais = conn.execute("SELECT id, nome, tutor FROM animais ORDER BY nome").fetchall()
        lista = conn.execute("""
            SELECT at.*, an.nome AS animal, an.tutor
            FROM atendimentos at JOIN animais an ON an.id=at.animal_id
            ORDER BY at.data_atendimento DESC, at.id DESC
        """).fetchall()
    return render_template("atendimentos.html", animais=lista_animais, atendimentos=lista,
                           hoje=date.today().isoformat())

@app.post("/atendimentos/<int:atendimento_id>/status")
def alterar_status(atendimento_id):
    novo_status = request.form.get("status")
    if novo_status in ("Concluído", "Pendente", "Cancelado"):
        with conectar() as conn:
            conn.execute("UPDATE atendimentos SET status=? WHERE id=?", (novo_status, atendimento_id))
        flash("Status atualizado.", "sucesso")
    return redirect(url_for("atendimentos"))

@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        try:
            preco = float(request.form.get("preco", "0").replace(",", "."))
        except ValueError:
            preco = -1
        if not nome or preco < 0:
            flash("Informe um nome e um preço válido.", "erro")
        else:
            try:
                with conectar() as conn:
                    conn.execute("INSERT INTO servicos (nome, descricao, preco) VALUES (?, ?, ?)",
                                 (nome, descricao, preco))
                flash("Serviço cadastrado!", "sucesso")
            except sqlite3.IntegrityError:
                flash("Já existe um serviço com esse nome.", "erro")
        return redirect(url_for("servicos"))
    with conectar() as conn:
        lista = conn.execute("SELECT * FROM servicos ORDER BY nome").fetchall()
    return render_template("servicos.html", servicos=lista)

@app.post("/servicos/<int:servico_id>/excluir")
def excluir_servico(servico_id):
    with conectar() as conn:
        conn.execute("DELETE FROM servicos WHERE id=?", (servico_id,))
    flash("Serviço removido da lista.", "sucesso")
    return redirect(url_for("servicos"))

@app.route("/relatorios")
def relatorios():
    with conectar() as conn:
        por_status = conn.execute("""
            SELECT status, COUNT(*) AS quantidade, COALESCE(SUM(valor),0) AS total
            FROM atendimentos GROUP BY status ORDER BY status
        """).fetchall()
        historico = conn.execute("""
            SELECT at.*, an.nome AS animal, an.tutor
            FROM atendimentos at JOIN animais an ON an.id=at.animal_id
            ORDER BY at.data_atendimento DESC, at.id DESC
        """).fetchall()
        faturamento = conn.execute("""
            SELECT COALESCE(SUM(valor),0) FROM atendimentos WHERE status='Concluído'
        """).fetchone()[0]
    return render_template("relatorios.html", por_status=por_status,
                           historico=historico, faturamento=faturamento)

@app.route("/custos", methods=["GET", "POST"])
def custos():
    resultado = None
    if request.method == "POST":
        campos = ["computadores", "preco_computador", "monitores", "preco_monitor",
                  "switches", "preco_switch", "roteadores", "preco_roteador",
                  "metros_cabo", "preco_metro", "mao_obra", "dias_implantacao"]
        valores = {}
        try:
            for campo in campos:
                valores[campo] = float(request.form.get(campo, "0").replace(",", "."))
                if valores[campo] < 0:
                    raise ValueError
            total = (
                valores["computadores"] * valores["preco_computador"] +
                valores["monitores"] * valores["preco_monitor"] +
                valores["switches"] * valores["preco_switch"] +
                valores["roteadores"] * valores["preco_roteador"] +
                valores["metros_cabo"] * valores["preco_metro"] +
                valores["mao_obra"]
            )
            resultado = {"total": total, "dias": valores["dias_implantacao"], "valores": valores}
        except ValueError:
            flash("Use somente números iguais ou maiores que zero.", "erro")
    return render_template("custos.html", resultado=resultado)

@app.route("/projeto")
def projeto():
    return render_template("projeto.html")

@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

@app.errorhandler(404)
def pagina_nao_encontrada(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True)
