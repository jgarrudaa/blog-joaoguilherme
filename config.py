SECRET_KEY = "Bl0gJ0tt4"     # senha secreta para sessão e outras coisas
USUARIO_ADMIN = "admin"        # senha do adm (alterar para uma mais segura
SENHA_ADMIN = "admin123"          # senha do adm (alterar para uma mais segura

# Variável de controle de ambiente, poderá ser "local" ou "produção"
ambiente = "local"

if ambiente == "local":
	# ------ INFORMAÇÕES DO SEU BLOG LOCAL, DEIXE COMO ESTÁ
	HOST = "localhost"
	USER = "root"
	PASSWORD = "senai"
	DATABASE = "blog_joaoguilherme"
elif ambiente == "produção":
	# ------ INFORMAÇÕES VINDAS DO DATABASE DO PYTHON ANYWHERE
	HOST =  "jgarruda.mysql.pythonanywhere-services.com"
	USER = "jgarruda"
	PASSWORD = "Guilherme.27"
	DATABASE = "jgarruda$blogjoaoguilherme"