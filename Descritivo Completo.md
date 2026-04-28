Unidade II - Ideação, Arquitetura Mínima e Git/GitHub® para o Projeto
Nesta Unidade crucial, faremos a transição do entendimento das ferramentas para a fase de planejamento e estruturação do seu miniprojeto. O sucesso de qualquer aplicação, especialmente aquelas assistidas por IA, reside em uma fundação sólida: uma ideia de projeto bem delineada, uma arquitetura de software clara e escalável, e um sistema de controle de versão robusto e eficiente. Exploraremos como a IA pode ser uma aliada poderosa em cada uma dessas etapas, desde a concepção até a preparação para a colaboração e entrega.

2.1 Seleção do Miniprojeto
A escolha do miniprojeto é o primeiro passo prático e um dos mais importantes para este laboratório. O objetivo não é construir um sistema complexo e completo, mas sim um Produto Mínimo Viável (MVP) que permita a você explorar e aplicar as capacidades da genAI em diferentes estágios do ciclo de vida do desenvolvimento de software. Um MVP bem definido garante que você possa focar no aprendizado e na experimentação com a IA, sem se perder em complexidades desnecessárias relacionadas ao domínio do problema.

2.1.1 Critérios para a Seleção de um Produto Mínimo Viável Assistido por Inteligência Artificial
Ao selecionar seu miniprojeto, considere os seguintes critérios para maximizar seu aprendizado e a eficácia do uso da IA:

Escopo limitado e claro: O projeto deve ter um conjunto de funcionalidades bem definido e gerenciável. Evite projetos que exijam meses de desenvolvimento ou que tenham requisitos ambíguos. A ideia é que ele possa ser concluído em um período razoável (ex: 30 horas de trabalho prático, conforme o plano de ensino).

Potencial de uso da IA: Escolha um projeto onde a genAI possa ser aplicada em múltiplas etapas: geração de código, testes, documentação, refatoração etc. Isso permitirá que você experimente as diversas funcionalidades dos assistentes de código.

Familiaridade Tecnológica: Embora a IA possa ajudar a aprender novas tecnologias, para este laboratório, é recomendável escolher uma linguagem de programação ou framework com o qual você já tenha alguma familiaridade básica. Isso reduzirá a curva de aprendizado e permitirá que você se concentre na interação com a IA.

Relevância pessoal: Um projeto que ressoa com seus interesses ou necessidades pessoais tende a ser mais motivador e engajador. Pense em pequenas automações, ferramentas utilitárias ou aplicações que você gostaria de usar.

Testabilidade: O projeto deve ser facilmente testável, permitindo que você valide as saídas da IA e pratique a escrita de testes automatizados.

2.1.2 Exemplos Detalhados de Projetos Recomendados para o Laboratório
Para guiar sua escolha, apresentamos sugestões de miniprojetos que se encaixam bem nos critérios citados no item 2.1.1, com uma análise de como a IA pode ser aplicada em cada um deles (Tabela 2):

2.2 Arquitetura Mínima (Módulos, Dependências, Fluxo de Dados)
Antes de mergulhar na codificação, um planejamento arquitetural, mesmo que mínimo, é essencial. Uma arquitetura bem definida serve como um mapa, guiando o desenvolvimento e garantindo que os componentes do sistema se encaixem de forma coesa. Uma das maiores vantagens de usar modelos de IA avançados como o Claude 4.6 Opus® é sua capacidade de atuar como um arquiteto de software virtual, auxiliando na concepção e visualização da estrutura do projeto.

2.2.1 Concebendo a Arquitetura com o Auxílio da Inteligência Artificial
Você pode utilizar a IA para gerar ideias de arquitetura, diagramas de componentes, listas de dependências e até mesmo para discutir as vantagens e desvantagens de diferentes abordagens arquiteturais. A chave é fornecer um contexto claro e um objetivo específico para a IA.

Ferramentas de diagramação assistida por IA:
Um padrão moderno e extremamente útil para documentar arquiteturas é o uso de linguagens de descrição de diagramas baseadas em texto, como o Mermaid.js ou o PlantUML. Essas linguagens permitem criar diagramas complexos (fluxogramas, diagramas de sequência, diagramas de classes etc.) a partir de um texto simples, o qual é facilmente compreendido e gerado por LLMs. Isso significa que você pode descrever sua arquitetura em linguagem natural e pedir à IA para gerar o código Mermaid correspondente.

Exemplo de prompt para geração de Diagrama Mermaid:

Contexto: Estou projetando uma Micro-API de gerenciamento de tarefas em Python® com FastAPI®. Ela terá um frontend (react) que se comunica com o backend, e este último se comunica com um banco de dados PostgreSQL®.

Objetivo: Crie um diagrama de componentes usando Mermaid.js, que mostre a interação entre o frontend, backend (API) e o banco de dados. O backend deve ter componentes para controller, service e repository.

Estilo: Use o tipo de diagrama C4-PlantUML, se possível, ou um diagrama de componentes simples. Identifique as setas de comunicação.

Resposta: Forneça apenas o código Mermaid.

Resultado esperado (Descrição): O diagrama de componentes ilustra a comunicação entre o frontend (react) e o backend (FastAPI®) via HTTP/JSON. O backend, por sua vez, interage com o banco de dados (PostgreSQL®) por meio de queries SQL. A arquitetura do backend é dividida em controller, service e repository, sendo que o controller recebe as requisições, o service implementa a lógica de negócio e o repository gerencia a interação com o banco de dados.

Além de diagramas, a IA pode ajudar a definir a estrutura de módulos e a hierarquia de pastas, sugerindo uma organização lógica que promova a manutenibilidade e a escalabilidade do projeto.

2.2.2 Definição de Dependências e Tecnologias
Com base na arquitetura, a IA pode auxiliar na identificação das dependências e tecnologias necessárias. Você pode descrever a funcionalidade desejada e pedir sugestões de bibliotecas ou frameworks.

Exemplo de prompt para sugestão de dependências:

Contexto: Estou construindo uma API RESTful em Python® para gerenciar usuários. Preciso de um Object-Relational Mapping (ORM) para interagir com um banco de dados PostgreSQL® e uma biblioteca para validação de dados.

Objetivo: Liste as bibliotecas Python® recomendadas para ORM e validação de dados, e gere um arquivo requirements.txt com as versões mais recentes.

Estilo: Inclua apenas as bibliotecas essenciais e suas versões.

Resultado esperado (IA):

Plaintext
fastapi==0.110.0
uvicorn==0.27.1
sqlalchemy==2.0.27
psycopg2-binary==2.9.9
pydantic==2.6.1
2.3 Git/GitHub® Essencial: Criar Repositório, .gitignore, Commits, Push, Releases/Tags; Requisitos da Submissão
O controle de versão é a espinha dorsal de qualquer projeto de software moderno, e o GitHub se tornou o padrão da indústria para hospedagem de repositórios e colaboração. No contexto do desenvolvimento assistido por IA, o Git® e o GitHub® não são apenas ferramentas para salvar o código, mas também para documentar a evolução do projeto, gerenciar contribuições (tanto humanas quanto de IA) e facilitar a entrega contínua. A IA pode otimizar significativamente seu fluxo de trabalho com Git® e GitHub®.

2.3.1 Configuração Inicial do Repositório e Boas Práticas
Para iniciar seu miniprojeto, siga os passos básicos de configuração de um repositório Git®, utilizando o terminal integrado do VS Code® ou Cursor®:

Para inicialização do repositório local, navegue até a pasta do seu projeto e execute:

Bash
git init
Este comando cria um novo repositório Git vazio na pasta atual.

Adicionando arquivos: antes de fazer o primeiro commit, adicione os arquivos do seu projeto à área de staging:

Bash
git add .
Importante: Certifique-se de que seu arquivo .gitignore esteja configurado antes de adicionar todos os arquivos, para evitar que arquivos desnecessários (como dependências de pacotes, arquivos de cache ou credenciais) sejam versionados.

Primeiro commit: Registre o estado inicial do seu projeto:

Bash
git commit -m "feat: estrutura inicial do projeto e setup básico"
Utilize mensagens de commit claras e descritivas, seguindo o padrão Conventional Commits (abordado abaixo).

Criação do Repositório Remoto no GitHub®: Acesse o GitHub®, crie um novo repositório vazio e siga as instruções para conectar seu repositório local ao remoto:

Bash
git remote add origin <URL_DO_SEU_REPOSITORIO_GITHUB>
git branch -M main
git push -u origin main
2.3.2 O Papel Crucial do .gitignore Inteligente
Um arquivo .gitignore bem elaborado é fundamental para manter seu repositório limpo e focado apenas no código-fonte relevante. Ao trabalhar com IA, é comum gerar arquivos temporários, ambientes virtuais ( .venv ), pastas de cache (__pycache__, .next, node_modules) e arquivos de configuração específicos de IDEs (.vscode, .idea). Incluir esses arquivos no controle de versão pode levar a conflitos desnecessários, aumentar o tamanho do repositório e expor informações sensíveis.

A IA pode ser uma excelente aliada na criação e manutenção do seu .gitignore.

Exemplo de prompt para geração de .gitignore:

Contexto: Estou iniciando um projeto Python® com FastAPI®, usando VS Code®. Também pretendo usar Node.js® para o frontend no futuro. Preciso de um arquivo .gitignore abrangente.

Objetivo: Gere um arquivo .gitignore que ignore arquivos e pastas comuns de Python®, Node.js®, VS Code® e ambientes virtuais.

Estilo: Organize as seções por tecnologia.

Resposta: Forneça apenas o conteúdo do arquivo .gitignore.

Resultado esperado (IA - exemplo de .gitignore):

Plaintext
# Python
__pycache__/
*.pyc
*.pyd
*.pyo
.Python
build/
dist/
*.egg-info/
.venv/
venv/

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.pnp/
.pnp.js

# VS Code
.vscode/
.history/

# Environment variables
.env
.env.*

# OS generated files
.DS_Store
Thumbs.db
2.3.3 Conventional Commits com Auxílio da Inteligência Artificial
Manter um histórico de commits limpo, consistente e informativo é uma prática essencial para a manutenibilidade do projeto e para facilitar a revisão de código. O padrão Conventional Commits oferece uma estrutura para as mensagens de commit, tornando o histórico legível e permitindo a automação de tarefas, como a geração de changelogs. A IA pode ser uma ferramenta poderosa para ajudar a aderir a esse padrão.

Estrutura de um Conventional Commit:
<tipo>[escopo opcional]: <descrição>
[corpo opcional]
[rodapé opcional]

Tipo: Indica a natureza da mudança (ex.: feat para nova funcionalidade, fix para correção de bug, docs para documentação, chore para tarefas de manutenção, refactor para refatoração de código, test para adição de testes).

Escopo (opcional): Descreve a parte do sistema que foi afetada pela mudança (ex: feat(auth):, fix(api):).

Descrição: Uma breve frase imperativa que resume a mudança.

Corpo (opcional): Uma descrição mais detalhada da mudança.

Rodapé (opcional): Referências a issues, pull requests ou quebras de compatibilidade (breaking change).

A IA, especialmente o Claude Code® ou as extensões de chat do Copilot®, pode sugerir mensagens de commit baseadas nas alterações que você realizou. Após mudanças estarem "staged" (git add .), você pode pedir à IA que gere uma mensagem de commit.

Exemplo de prompt para geração de mensagem de commit:

Contexto: Fiz alterações nos arquivos src/services/user_service.py e src/api/routes.py. Adicionei uma nova funcionalidade para criar usuários e corrigi um pequeno bug na validação de e-mail.

Objetivo: Gere uma mensagem de commit seguindo o padrão Conventional Commits.

Estilo: Use feat para a nova funcionalidade e fix para a correção de bug. Combine-os, caso seja apropriado.

Resposta: Forneça apenas a mensagem de commit.

Resultado esperado (IA):

Plaintext
feat(user): Adiciona funcionalidade de criação de usuário

fix(validation): Corrige bug na validação de e-mail em user_service.
Essa prática não só melhora a qualidade do seu histórico de commits, mas também o ajuda a pensar de forma mais estruturada sobre as mudanças que você está introduzindo (Blischack et al., 2016).

2.3.4 Requisitos para Submissão Final do Projeto no GitHub®
Para que seu miniprojeto seja considerado completo e pronto para avaliação, ele deve aderir a um conjunto de requisitos de submissão. A publicação no GitHub não é apenas um ato de entrega, mas uma demonstração de suas habilidades quanto ao controle de versão e documentação.

Checklist de submissão:

Repositório público: O projeto deve estar hospedado em um repositório público no GitHub®, acessível para revisão. Certifique-se de que não há informações sensíveis (chaves de API, senhas) expostas. Utilize variáveis de ambiente ou arquivos .env (devidamente ignorados pelo .gitignore) para credenciais.

Histórico de commits consistente: O repositório deve conter um histórico de commits que demonstre a evolução do projeto. Recomenda-se um mínimo de 5 a 10 commits significativos, seguindo o padrão Conventional Commits, para ilustrar o processo de desenvolvimento.

Arquivo README.md detalhado: O README.md é a porta de entrada do seu projeto. Ele deve ser completo, claro e profissional, contendo:

Um título e uma breve descrição do projeto;

Instruções detalhadas sobre como configurar o ambiente e rodar o projeto localmente;

Exemplos de uso ou como interagir com a aplicação/API;

Uma lista das tecnologias utilizadas, incluindo os modelos de IA e assistentes de código;

Uma seção de "Limitações e Próximos Passos", onde você pode discutir o que não foi implementado e como o projeto poderia ser expandido;

Créditos e licença;

Gerenciamento de dependências: O projeto deve incluir um arquivo que liste todas as suas dependências (ex.: requirements.txt para Python®, package.json para Node.js®), permitindo que outros desenvolvedores repliquem seu ambiente facilmente;

Testes automatizados: Seções de testes unitários ou de integração devem estar presentes, demonstrando a robustez do código e a validação das funcionalidades implementadas. Os testes devem ser executáveis e passar com sucesso;

Releases ou tags: É uma boa prática criar uma "Release" ou uma "Tag" (ex.: v1.0.0) no GitHub® para marcar a versão de entrega do seu miniprojeto. Isso sinaliza um ponto estável e finalizado do desenvolvimento.