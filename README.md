# SDG Interlinkages

Pacote Python para reconstruir redes de interdependência entre metas dos ODS a partir de duas bases. O motor analítico deriva da revisão publicada do projeto `2c6632f2e265f8172d0e8de7752fed1a8d26828f`. O lançador, a organização dos resultados e a exportação de figuras são locais.

## Aplicativo Gradio

**No Windows**, extraia o ZIP completo do GitHub ou clone o repositório. Abra a pasta que contém este README e dê dois cliques em `launch_app.bat`. O lançador usa Python 3.10+ e cria ou reutiliza `.venv`. Na primeira vez, aguarde a instalação. O aplicativo abre no navegador local. Mantenha a janela do terminal aberta durante as análises. Se o navegador não abrir, copie a URL local exibida no terminal. Para encerrar, pressione Ctrl+C.

**No Linux ou macOS**, execute a partir da raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-app.txt
python app.py
```

| Aba | Entrada | Escolha do método |
| --- | --- | --- |
| IGES/JRC | Região ou país da árvore da UNSD. Opcionalmente, envie um CSV já coletado para essa área. | Pearson |
| SDGIndex | Região, agregado ou país das planilhas incluídas no repositório. | Pearson, Spearman ou ambos |

Escolha o recorte e a área e clique em **Executar análise**. A tela mostra as cinco primeiras linhas de cada ranking por método e, separadamente, os quatro grupos de destaque quando houver metas elegíveis. Clique numa linha do ranking para ver o indicador. A galeria apresenta as redes completa, de sinergias e de trade-offs. Baixe a planilha `_full.xlsx` isoladamente ou o ZIP com toda a execução. A seleção **Ambos** produz resultados separados por método, inclusive no ZIP.

As duas abas compartilham uma fila de cálculo. As execuções terminadas permanecem em `output/`. O Gradio guarda também cópias temporárias dos arquivos disponibilizados ao navegador.

## Executar pelo terminal

Extraia o ZIP inteiro. No Windows, instale Python 3.10 ou superior com o lançador `py` ou o executável `python` disponível. Abra `launch.bat`. Na primeira execução, ele cria o ambiente virtual e instala as dependências. É necessário acesso ao índice de pacotes nessa instalação. A escolha é feita em três etapas.

1. IGES/JRC ou SDGIndex.
2. Região ou país.
3. Código ou nome da área exibida.

O SDGIndex executa Pearson e Spearman, cada um na sua subpasta. Para executar somente um, use a linha de comando. No Linux ou macOS, a partir da pasta do README:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ods
```

Exemplos para o terminal, com o ambiente virtual ativo:

```bash
python -m ods --versao IGES_JRC --tipo pais --area 76
python -m ods --versao IGES_JRC --tipo regiao --area 1
python -m ods --versao IGES_JRC --tipo pais --area 76 --csv coleta_brasil.csv
python -m ods --versao SDGIndex --tipo pais --area BRA --metodo pearson
python -m ods --versao SDGIndex --tipo regiao --area World --metodo ambos
```

Use `--saida PASTA` para trocar a raiz das saídas. No Windows, os mesmos argumentos podem ser passados a `launch.bat`.

## Fontes e processamento

**IGES/JRC.** O catálogo geográfico local usa os códigos M49 e a árvore continental da UNSD. A coleta consulta a API por indicador, em lotes paginados. Um CSV já coletado, no formato achatado dessa API e com o código da área selecionada, permite executar offline. O motor seleciona séries, trata lacunas conforme as regras de cada série, consolida medidas compartilhadas e usa normatividade por indicador. Calcula Pearson para as séries elegíveis, cruza as relações com as decisões IGES/JRC e aplica a classificação temporal antes de calcular os graus e rankings.

**SDGIndex.** Inclui as planilhas anuais utilizadas pelo site para 169 países e 14 regiões ou agregados e o mapeamento editorial de 101 indicadores para metas. O programa lê a aba `Observacoes_componentes` da área selecionada e recalcula os pares entre objetivos a partir dos níveis dos escores de 2000 a 2025. Exclui pares do mesmo ODS ou da mesma meta antes dos testes. O limiar de inclusão é p nominal < 0,10 com pelo menos oito observações pareadas e coeficiente não nulo. Os testes defasados e condicionais informam a orientação exploratória. No caso indeterminado, o motor representa o par com dois arcos e registra a evidência de direção. As planilhas de origem são identificáveis por arquivo em `data/SDGIndex/`. A proveniência dos arquivos compactados originais está em `provenance.json`.

Nos dois modos, uma relação inicialmente divergente dos sentidos do progresso é excluída quando algum R² temporal é inferior a 0,1, ou quando algum R² é inferior a 0,2 e o módulo do coeficiente é inferior a 0,4. As demais divergentes com direção definida mudam de tipo. O coeficiente observado é preservado. A aba **Casos adversos** registra as decisões. Colab é a soma ponderada das sinergias enviadas menos os trade-offs enviados. Neglect soma os trade-offs recebidos e as sinergias recebidas de origens em retrocesso. Os quatro grupos de destaque seguem as regras de direção, ambição e cruzamento de rankings da versão publicada, incluindo empates na quinta posição.

## Resultados

Cada execução cria uma pasta datada com identificador próprio. As duas pastas principais ficam em `output/`. Exemplos de caminhos relativos:

```text
output/IGES_JRC/pais/76/<execução>/
output/SDGIndex/regiao/World/<execução>/pearson/
output/SDGIndex/regiao/World/<execução>/spearman/
```

| Arquivo | Conteúdo |
| --- | --- |
| `*_full.xlsx` | Dados, cálculos, atributos, destaques e auditoria do método escolhido |
| `*_interlinkages.xlsx` | Rankings, destaques e casos adversos |
| `*_network.csv` e `*_nodes.csv` | Tabelas de arestas e nós para análise externa |
| `*_full.png`, `*_synergy.png`, `*_trade-off.png` | Rede completa e recortes de sinergias e trade-offs |

Os PNGs usam disposição por forças com semente fixa. As coordenadas podem diferir das do navegador. As metas aparecem pelos seus números. Nos CSVs do SDGIndex, o identificador composto distingue indicadores associados à mesma meta. Na figura completa, branco e cinza distinguem os grupos a e c, amarelo e vermelho os grupos b e d. Sinergias de origens em retrocesso aparecem em vinho claro e trade-offs dessas origens, em cinza claro. As figuras resumem a rede; as planilhas conservam a evidência de cada arco.

## Estrutura e integração em Python

| Caminho | Função |
| --- | --- |
| `app.py` | Interface Gradio, seleção de área, apresentação de resultados e geração do ZIP |
| `launch_app.bat` e `launch.bat` | Lançadores Windows para navegador e terminal |
| `ods/service.py` | Catálogo de áreas e execução compartilhada pelas duas interfaces |
| `ods/engine/` | Motores analíticos, regras, normatividade e tabelas auxiliares |
| `ods/render.py` | Exportação das três redes em PNG |
| `data/` | Catálogos, ícones, mapeamento indicador–meta e planilhas de escores |
| `tests/` | Testes de regressão e dados de verificação |

Para integrar o motor a outra aplicação ou automatizar um recorte:

```python
from ods.service import list_areas, run_analysis

paises = list_areas("SDGIndex", "pais")
pasta = run_analysis("SDGIndex", "pais", "BRA", method="pearson")
print(paises["BRA"], pasta)
```

O parâmetro `output_dir` permite escolher outra raiz gravável. Para o IGES/JRC, `csv_path` recebe o caminho do CSV opcional. O terminal usa `requirements.txt`; o navegador usa `requirements-app.txt`, que inclui as dependências do cálculo.

## Testes

```bash
python -m unittest discover -s tests
```

O conjunto inclui regressões de consolidação de séries, normatividade, limites de reclassificação, rankings e cálculos nacionais comparados ao SciPy. A coleta sintética de teste permite validar o IGES/JRC sem acesso à UNSD.
