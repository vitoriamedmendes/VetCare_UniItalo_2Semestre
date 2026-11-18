# VetCare | Sistema de gestão veterinária

Projeto acadêmico demonstrativo desenvolvido com Python, Flask, SQLite, HTML, CSS e JavaScript.

## 1. Requisitos
- Python 3.10 ou superior
- Navegador atualizado
- VS Code (recomendado)

## 2. Como executar no Windows
1. Extraia o ZIP.
2. Abra a pasta `VetCare` no VS Code.
3. Abra o terminal integrado: Terminal > Novo Terminal.
4. Crie o ambiente virtual:
   `py -m venv .venv`
5. Ative:
   PowerShell: `.\.venv\Scripts\Activate.ps1`
   CMD: `.venv\Scripts\activate.bat`
6. Instale as dependências:
   `py -m pip install -r requirements.txt`
7. Execute:
   `py app.py`
8. Abra no navegador:
   `http://127.0.0.1:5000`

O arquivo `vetcare.db` será criado automaticamente na primeira execução.
Para encerrar, volte ao terminal e pressione `Ctrl + C`.

## 3. Funcionalidades
- Painel inicial com indicadores.
- Cadastro, listagem, pesquisa, edição e exclusão protegida de animais.
- Registro de atendimentos e alteração de status.
- Cadastro e consulta de serviços.
- Histórico, relatório e faturamento de atendimentos concluídos.
- Simulador de custos de infraestrutura e tempo de implantação.
- Página institucional com contextualização do projeto e ODS.
- Página educativa sobre sistemas operacionais, hardware e software.

## 4. Observações importantes
- Este é um protótipo acadêmico local. Não use dados reais/sensíveis de clientes ou animais.
- O banco SQLite persiste os dados no arquivo `vetcare.db`.
- Faça cópias de segurança desse arquivo.
- Antes de publicar na internet, implemente autenticação, controle de acesso, proteção CSRF, validação adicional, HTTPS, política de privacidade e gestão segura de segredos.
- A página de ODS usa o ODS 3 (Saúde e Bem-Estar) como proposta de alinhamento. Confirme com o professor se essa escolha atende ao recorte esperado.
- O programa em C da pasta `c_program` é um módulo complementar separado. O regulamento descreve o menu em C, mas não determina que o site seja programado em C.
