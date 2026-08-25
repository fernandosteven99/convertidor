from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

HEX_DIGITS = "0123456789ABCDEF"
BASES = {2: "Binario", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
WORD_SIZES = {
    8: ("Byte", 2**8 - 1),
    16: ("Word", 2**16 - 1),
    32: ("DWord", 2**32 - 1),
    64: ("QWord", 2**64 - 1),
}


def char_to_value(char):
    char = char.upper()
    if "0" <= char <= "9":
        return ord(char) - ord("0")
    if "A" <= char <= "F":
        return ord(char) - ord("A") + 10
    return -1


def value_to_char(value):
    # Mapeo manual exigido para hexadecimal: 10-15 -> A-F.
    return HEX_DIGITS[value]


def base_to_decimal(number, base):
    """Conversión por multiplicación posicional, sin int(text, base)."""
    number = number.strip().upper()

    if not number:
        raise ValueError("El número no puede estar vacío.")

    decimal = 0
    steps = []

    for index, char in enumerate(number):
        digit = char_to_value(char)
        if digit < 0 or digit >= base:
            raise ValueError(
                f"El dígito '{char}' no es válido para la base {base}."
            )

        power = len(number) - 1 - index
        contribution = digit * (base ** power)
        decimal += contribution

        steps.append({
            "digit": char,
            "value": digit,
            "power": power,
            "contribution": contribution,
        })

    return decimal, steps


def decimal_to_base(number, base):
    """Conversión por divisiones sucesivas, sin number.toString(base)."""
    if number == 0:
        return "0", [{
            "dividend": 0,
            "quotient": 0,
            "remainder": 0,
            "digit": "0"
        }]

    n = number
    remainders = []
    steps = []

    while n > 0:
        quotient = n // base
        remainder = n % base
        digit = value_to_char(remainder)

        steps.append({
            "dividend": n,
            "quotient": quotient,
            "remainder": remainder,
            "digit": digit,
        })
        remainders.append(digit)
        n = quotient

    return "".join(reversed(remainders)), steps


def validate_number(number, base, bits):
    decimal, positional_steps = base_to_decimal(number, base)
    max_value = WORD_SIZES[bits][1]

    if decimal > max_value:
        raise OverflowError(
            f"Overflow / Desbordamiento de Registro. "
            f"El máximo para {bits} bits es {max_value}."
        )

    return decimal, positional_steps


def padded_binary(decimal, bits):
    binary, _ = decimal_to_base(decimal, 2)
    return binary.zfill(bits)


def convert_all(number, base, bits):
    decimal, positional_steps = validate_number(number, base, bits)

    binary, binary_steps = decimal_to_base(decimal, 2)
    octal, octal_steps = decimal_to_base(decimal, 8)
    decimal_text, decimal_steps = decimal_to_base(decimal, 10)
    hexadecimal, hex_steps = decimal_to_base(decimal, 16)

    return {
        "decimal_value": decimal,
        "binary": binary.zfill(bits),
        "octal": octal,
        "decimal": decimal_text,
        "hexadecimal": hexadecimal,
        "padding": bits - len(binary),
        "max_value": WORD_SIZES[bits][1],
        "architecture": WORD_SIZES[bits][0],
        "positional_steps": positional_steps,
        "division_steps": {
            "binary": binary_steps,
            "octal": octal_steps,
            "decimal": decimal_steps,
            "hexadecimal": hex_steps,
        },
    }


def alu_operation(a, b, operation):
    if len(a) != len(b):
        raise ValueError("Las dos cadenas binarias deben tener la misma longitud.")

    if not a or any(bit not in "01" for bit in a + b):
        raise ValueError("La ALU solo acepta cadenas binarias.")

    result = []
    rows = []

    for index, (bit_a, bit_b) in enumerate(zip(a, b)):
        if operation == "AND":
            bit = "1" if bit_a == "1" and bit_b == "1" else "0"
        elif operation == "OR":
            bit = "1" if bit_a == "1" or bit_b == "1" else "0"
        elif operation == "XOR":
            bit = "1" if bit_a != bit_b else "0"
        else:
            raise ValueError("Operación ALU no válida.")

        result.append(bit)
        rows.append({
            "position": index,
            "a": bit_a,
            "b": bit_b,
            "result": bit
        })

    return "".join(result), rows


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/convert")
def api_convert():
    try:
        data = request.get_json(force=True)
        number = str(data.get("number", ""))
        base = int(data.get("base", 10))
        bits = int(data.get("bits", 8))

        if base not in BASES:
            return jsonify({"ok": False, "error": "Base de entrada no válida."}), 400
        if bits not in WORD_SIZES:
            return jsonify({"ok": False, "error": "Tamaño de palabra no válido."}), 400

        result = convert_all(number, base, bits)
        return jsonify({"ok": True, **result})

    except OverflowError as exc:
        return jsonify({"ok": False, "error": str(exc), "type": "overflow"}), 400
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc), "type": "validation"}), 400
    except Exception:
        return jsonify({"ok": False, "error": "Ocurrió un error inesperado."}), 500


@app.post("/api/alu")
def api_alu():
    try:
        data = request.get_json(force=True)
        a = str(data.get("a", "")).strip()
        b = str(data.get("b", "")).strip()
        operation = str(data.get("operation", "AND")).upper()

        result, rows = alu_operation(a, b, operation)
        return jsonify({"ok": True, "result": result, "rows": rows})

    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)
