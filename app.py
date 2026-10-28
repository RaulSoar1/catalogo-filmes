
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-local-para-estudo")

# Caminho do banco de dados SQLite
DATABASE = os.path.join(app.root_path, "filmes.db")


def conectar_banco():
    """Abre uma conexão com o banco de dados."""
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    """Cria a tabela automaticamente se ela ainda não existir."""
    conexao = conectar_banco()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            ano INTEGER NOT NULL,
            nota REAL NOT NULL CHECK (nota >= 1 AND nota <= 10)
        )
    """)
    conexao.commit()
    conexao.close()


@app.route("/")
def index():
    """Lista todos os filmes cadastrados."""
    conexao = conectar_banco()
    filmes = conexao.execute(
        "SELECT * FROM filmes ORDER BY id DESC"
    ).fetchall()
    conexao.close()

    return render_template("index.html", filmes=filmes)


@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    """Exibe o formulário e cadastra um filme."""
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        genero = request.form.get("genero", "").strip()
        ano_texto = request.form.get("ano", "").strip()
        nota_texto = request.form.get("nota", "").strip().replace(",", ".")

        if not titulo or not genero or not ano_texto or not nota_texto:
            flash("Preencha todos os campos.", "erro")
            return render_template("form.html", filme=None)

        try:
            ano = int(ano_texto)
            nota = float(nota_texto)

            if ano < 1888 or ano > 2100:
                raise ValueError("Ano fora do intervalo permitido.")

            if not 1 <= nota <= 10:
                raise ValueError("A nota deve estar entre 1 e 10.")

        except ValueError:
            flash("Confira o ano e a nota informados.", "erro")
            return render_template("form.html", filme=None)

        conexao = conectar_banco()
        conexao.execute(
            "INSERT INTO filmes (titulo, genero, ano, nota) VALUES (?, ?, ?, ?)",
            (titulo, genero, ano, nota)
        )
        conexao.commit()
        conexao.close()

        flash("Filme cadastrado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("form.html", filme=None)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_filme(id):
    """Edita um filme existente."""
    conexao = conectar_banco()
    filme = conexao.execute(
        "SELECT * FROM filmes WHERE id = ?", (id,)
    ).fetchone()
    conexao.close()

    if filme is None:
        flash("Filme não encontrado.", "erro")
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        genero = request.form.get("genero", "").strip()
        ano_texto = request.form.get("ano", "").strip()
        nota_texto = request.form.get("nota", "").strip().replace(",", ".")

        if not titulo or not genero or not ano_texto or not nota_texto:
            flash("Preencha todos os campos.", "erro")
            return render_template("form.html", filme=filme)

        try:
            ano = int(ano_texto)
            nota = float(nota_texto)

            if ano < 1888 or ano > 2100:
                raise ValueError("Ano fora do intervalo permitido.")

            if not 1 <= nota <= 10:
                raise ValueError("A nota deve estar entre 1 e 10.")

        except ValueError:
            flash("Confira o ano e a nota informados.", "erro")
            return render_template("form.html", filme=filme)

        conexao = conectar_banco()
        conexao.execute(
            """UPDATE filmes
               SET titulo = ?, genero = ?, ano = ?, nota = ?
               WHERE id = ?""",
            (titulo, genero, ano, nota, id)
        )
        conexao.commit()
        conexao.close()

        flash("Filme atualizado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("form.html", filme=filme)


@app.route("/excluir/<int:id>", methods=["POST"])
def excluir_filme(id):
    """Exclui um filme pelo seu ID."""
    conexao = conectar_banco()
    conexao.execute("DELETE FROM filmes WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()

    flash("Filme excluído.", "sucesso")
    return redirect(url_for("index"))


# Cria a tabela quando o aplicativo inicia
criar_tabela()


if __name__ == "__main__":
    app.run(debug=True)
