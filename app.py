from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuração do Banco de Dados
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurantekishimoto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuração do Flask-Admin
admin = Admin(app, name='Administração', template_mode='bootstrap3')

# Definição dos Modelos
class Cliente(db.Model):
    cpf_cliente = db.Column(db.String(14), primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    tel_cliente = db.Column(db.String(20), nullable=False)
    endereco_cliente = db.Column(db.String(255), nullable=False)
    email_cliente = db.Column(db.String(120), unique=True, nullable=False)
    senha_cliente = db.Column(db.String(100), nullable=False)

class Pedido(db.Model):
    id_pedido = db.Column(db.Integer, primary_key=True)
    cpf_cliente = db.Column(db.String(14), db.ForeignKey('cliente.cpf_cliente'), nullable=False)
    data_pedido = db.Column(db.DateTime, nullable=False)
    status_pedido = db.Column(db.String(50), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)

class Entregador(db.Model):
    cpf_entregador = db.Column(db.String(14), primary_key=True)
    nome_entregador = db.Column(db.String(100), nullable=False)
    tel_entregador = db.Column(db.String(20), nullable=False)
    email_entregador = db.Column(db.String(120), unique=True, nullable=False)

class Produto(db.Model):
    id_produto = db.Column(db.Integer, primary_key=True)
    nome_produto = db.Column(db.String(100), nullable=False)
    descricao_produto = db.Column(db.String(255), nullable=False)
    preco_produto = db.Column(db.Float, nullable=False)
    imagem_produto = db.Column(db.String(255), nullable=True)

class Cardapio(db.Model):
    id_cardapio = db.Column(db.Integer, primary_key=True)
    nome_cardapio = db.Column(db.String(100), nullable=False)
    descricao_cardapio = db.Column(db.String(255), nullable=False)

# Adicionar modelos ao Flask-Admin
admin.add_view(ModelView(Cliente, db.session))
admin.add_view(ModelView(Pedido, db.session))
admin.add_view(ModelView(Entregador, db.session))
admin.add_view(ModelView(Produto, db.session))
admin.add_view(ModelView(Cardapio, db.session))

# Função para verificar se o usuário está autenticado
def is_authenticated():
    return 'user_id' in session

# Rotas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/nossahistoria/')
def nossa_historia():
    return render_template('nossahistoria.html')

@app.route('/cardapio/')
def cardapio():
    return render_template('cardapio.html')

@app.route('/carrinho/')
def carrinho():
    return render_template('carrinho.html')

@app.route('/meuperfil/', methods=['GET', 'POST'])
def meu_perfil():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    cliente_logado = Cliente.query.filter_by(email_cliente=session['user_email']).first()

    if request.method == 'POST':
        # Atualização dos dados do cliente
        cliente_logado.nome_cliente = request.form['edit-nome']
        cliente_logado.tel_cliente = request.form['edit-telefone']
        cliente_logado.endereco_cliente = request.form['edit-endereco']
        cliente_logado.email_cliente = request.form['edit-email']
        
        db.session.commit()
        flash('Informações atualizadas com sucesso.')

        # Redireciona para evitar reenvios acidentais do formulário
        return redirect(url_for('meu_perfil'))

    return render_template('meuperfil.html', cliente=cliente_logado)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cliente = Cliente.query.filter_by(email_cliente=email).first()

        if cliente and bcrypt.check_password_hash(cliente.senha_cliente, password):
            session['user_id'] = cliente.cpf_cliente  # Exemplo: use um identificador único para o usuário
            session['user_email'] = cliente.email_cliente  # Armazena o email na sessão
            flash('Login bem-sucedido!')
            return redirect(url_for('home'))  # Redireciona para a página inicial após o login
        else:
            flash('Credenciais inválidas. Verifique seu email e senha.')

    return render_template('login.html')

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['fullName']
        cpf = request.form['cpf']
        senha = request.form['password']
        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
        
        novo_cliente = Cliente(
            cpf_cliente=cpf,
            nome_cliente=nome,
            tel_cliente=request.form['phone'],
            endereco_cliente=request.form['address'],
            email_cliente=request.form['email'],
            senha_cliente=hashed_senha
        )
        db.session.add(novo_cliente)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça o login para continuar.')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

@app.route('/esqueceu/')
def esqueceu():
    return render_template('esqueceu.html')

@app.route('/metodpag/', methods=['GET', 'POST'])
def metodpag():
    if request.method == 'POST':
        # Processamento do método de pagamento
        return redirect(url_for('sucesso'))
    
    return render_template('metodpag.html')

@app.route('/novasenha/', methods=['GET', 'POST'])
def novasenha():
    if request.method == 'POST':
        nova_senha = request.form['novaSenha']
        confirmar_senha = request.form['confirmarSenha']
        
        if nova_senha == confirmar_senha:
            hashed_senha = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
            # Atualize a senha no banco de dados conforme necessário
            flash('Senha alterada com sucesso. Faça o login com sua nova senha.')
            return redirect(url_for('login'))
        else:
            flash('As senhas não coincidem. Tente novamente.')

    return render_template('novasenha.html')

@app.route('/telapagamento/')
def telapagamento():
    cliente_logado = Cliente.query.filter_by(email_cliente=session['user_email']).first()
    return render_template('telapagamento.html', cliente=cliente_logado)

@app.route('/sucesso/', methods=['GET', 'POST'])
def sucesso():
    if request.method == 'POST':
        # Lógica para finalizar a compra
        flash('Compra realizada com sucesso!')
        return render_template('sucesso.html')
    
    return render_template('sucesso.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

