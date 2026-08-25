# Conversor Multibase & ALU — Python + Flask

Proyecto académico construido para Visual Studio Code usando Python.

## Estructura

```text
conversor_multibase_python/
├── app.py
├── requirements.txt
├── vercel.json
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── app.js
```

## Ejecutar en Visual Studio Code

Abre la carpeta en VS Code.

### 1. Crear entorno virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Flask

```bash
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
python app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

## Algoritmos implementados

- Cualquier base → decimal mediante multiplicación posicional.
- Decimal → cualquier base mediante divisiones sucesivas.
- Mapeo manual hexadecimal 10-15 → A-F.
- Padding binario según 8, 16, 32 o 64 bits.
- Validación de Overflow.
- Nodo central en base 10.
- ALU bit a bit con AND, OR y XOR.

No se utilizan `int(numero, base)` ni `toString(base)` para realizar las conversiones solicitadas.

## Publicar en Vercel

Sube el proyecto a GitHub y luego importa el repositorio en Vercel.

El archivo `vercel.json` ya está incluido para desplegar la aplicación Flask.

## Nota

La aplicación acepta valores sin signo entre 0 y 2^bits - 1, de acuerdo con el ejemplo de Overflow del enunciado.
