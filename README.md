# Juntar Arquivos em PDF

Aplicação web criada com **Streamlit** que permite fazer upload de imagens e PDFs e exportar tudo em um único arquivo PDF combinado.

## Funcionalidades

- Upload de múltiplos arquivos (imagens e/ou PDFs) simultaneamente
- Suporte aos formatos: `PDF`, `PNG`, `JPG`, `JPEG`, `WEBP`, `BMP`, `TIFF`
- Imagens são convertidas em páginas A4 com proporção preservada
- PDFs têm todas as suas páginas incluídas na ordem original
- Barra de progresso durante o processamento
- Download do PDF final com um clique

## Requisitos

- Python 3.9+
- Dependências listadas em `requirements.txt`

## Instalação

```bash
# Clone o repositório ou copie os arquivos para uma pasta
cd afs_juntar_arquivos

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

1. Clique em **Browse files** e selecione um ou mais arquivos
2. Confira a lista de arquivos carregados
3. Clique em **Gerar PDF combinado**
4. Faça o download do arquivo `arquivos_combinados.pdf`

## Estrutura do projeto

```
afs_juntar_arquivos/
├── app.py            # Aplicação Streamlit
├── requirements.txt  # Dependências Python
├── README.md         # Este arquivo
└── .venv/            # Ambiente virtual (não versionado)
```

## Dependências

| Pacote | Uso |
|--------|-----|
| `streamlit` | Interface web |
| `pypdf` | Leitura e escrita de PDFs |
| `Pillow` | Processamento de imagens |
| `reportlab` | Renderização de imagens em páginas PDF |
