from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from forms import ProdutoForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'minha_chave_secreta'
db = SQLAlchemy(app)
Bootstrap(app)

# Modelo de Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar_produto', methods=['GET', 'POST'])
def adicionar_produto():
    form = ProdutoForm()
    if form.validate_on_submit():
        novo_produto = Produto(
            nome=form.nome.data,
            quantidade=form.quantidade.data,
            preco=form.preco.data
        )
        db.session.add(novo_produto)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('lista_produtos'))
    return render_template('adicionar_produto.html', form=form)

@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=produto)

    if form.validate_on_submit():
        produto.nome = form.nome.data
        produto.quantidade = form.quantidade.data
        produto.preco = form.preco.data
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('lista_produtos'))

    return render_template('editar_produto.html', form=form, produto=produto)

@app.route('/remover_produto/<int:id>', methods=['POST'])
def remover_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto removido com sucesso!', 'danger')
    return redirect(url_for('lista_produtos'))

@app.route('/produtos', methods=['GET'])
def lista_produtos():
    query = request.args.get('q')  # Obtém o termo de busca
    if query:
        produtos = Produto.query.filter(Produto.nome.ilike(f'%{query}%')).all()
    else:
        produtos = Produto.query.all()
    
    return render_template('produtos.html', produtos=produtos, query=query)



@app.template_filter('moeda')
def moeda(preco):
    # Formata com duas casas decimais, troca o ponto pela vírgula e garante o "R$" na frente
    return f"R$ {preco:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criação do banco de dados
    app.run(debug=True)