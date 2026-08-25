const $ = (selector) => document.querySelector(selector);

const numberInput = $("#number");
const baseInput = $("#base");
const bitsInput = $("#bits");
const convertBtn = $("#convertBtn");
const inputStatus = $("#inputStatus");

function setStatus(element, text, type = "neutral") {
    element.textContent = text;
    element.className = `status ${type}`;
}

function renderValidation(data) {
    $("#validationGrid").innerHTML = `
        <div class="validation-item">
            <span>ARQUITECTURA</span>
            <strong>${data.architecture}</strong>
        </div>
        <div class="validation-item">
            <span>TAMAÑO</span>
            <strong>${bitsInput.value} bits</strong>
        </div>
        <div class="validation-item">
            <span>VALOR BASE 10</span>
            <strong>${data.decimal_value}</strong>
        </div>
        <div class="validation-item">
            <span>REGISTRO</span>
            <strong>0 — ${data.max_value}</strong>
        </div>
    `;
    $("#validationCard").classList.remove("hidden");
}

function renderSteps(data) {
    $("#positionalSteps").innerHTML = data.positional_steps.map((step) =>
        `<div class="step">
            ${step.digit} × base<sup>${step.power}</sup>
            = ${step.contribution}
        </div>`
    ).join("");

    const steps = data.division_steps.binary;
    $("#divisionSteps").innerHTML = steps.map((step) =>
        `<div class="step">
            ${step.dividend} ÷ 2 = ${step.quotient}
            &nbsp; residuo ${step.remainder}
        </div>`
    ).join("");
}

async function convert() {
    const number = numberInput.value.trim();

    if (!number) {
        setStatus(inputStatus, "Ingresa un número", "error");
        return;
    }

    convertBtn.disabled = true;
    setStatus(inputStatus, "Validando…");

    try {
        const response = await fetch("/api/convert", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                number,
                base: Number(baseInput.value),
                bits: Number(bitsInput.value)
            })
        });

        const data = await response.json();

        if (!data.ok) {
            $("#validationCard").classList.remove("hidden");
            $("#validationGrid").innerHTML = `
                <div class="validation-item" style="grid-column: 1/-1">
                    <span>ERROR DE VALIDACIÓN</span>
                    <strong style="color: #ff8998">${data.error}</strong>
                </div>`;
            $("#resultsCard").classList.add("hidden");
            $("#algorithmCard").classList.add("hidden");
            setStatus(inputStatus, data.type === "overflow" ? "Overflow" : "Dato inválido", "error");
            return;
        }

        $("#binaryResult").textContent = data.binary;
        $("#octalResult").textContent = data.octal;
        $("#decimalResult").textContent = data.decimal;
        $("#hexResult").textContent = data.hexadecimal;
        $("#architectureBadge").textContent = `${data.architecture} · ${bitsInput.value} bits`;

        renderValidation(data);
        renderSteps(data);

        $("#resultsCard").classList.remove("hidden");
        $("#algorithmCard").classList.remove("hidden");

        setStatus(inputStatus, "Conversión correcta", "success");
    } catch (error) {
        setStatus(inputStatus, "No se pudo conectar con Python", "error");
    } finally {
        convertBtn.disabled = false;
    }
}

async function executeALU() {
    const a = $("#aluA").value.trim();
    const b = $("#aluB").value.trim();
    const operation = $("#operation").value;

    if (a.length !== b.length) {
        alert("Las dos cadenas deben tener la misma cantidad de bits.");
        return;
    }

    try {
        const response = await fetch("/api/alu", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({a, b, operation})
        });

        const data = await response.json();

        if (!data.ok) {
            alert(data.error);
            return;
        }

        $("#aluResult").textContent = data.result;
        $("#aluRows").innerHTML = data.rows.map((row) =>
            `<div class="alu-bit">
                bit ${row.position}<br>
                ${row.a} ${operation} ${row.b} → <strong>${row.result}</strong>
            </div>`
        ).join("");

        $("#aluResultBox").classList.remove("hidden");
    } catch {
        alert("No se pudo conectar con el servidor Python.");
    }
}

convertBtn.addEventListener("click", convert);
$("#aluBtn").addEventListener("click", executeALU);

document.querySelectorAll("[data-copy]").forEach(button => {
    button.addEventListener("click", async () => {
        const value = $("#" + button.dataset.copy).textContent;
        await navigator.clipboard.writeText(value);
        button.textContent = "✓ Copiado";
        setTimeout(() => button.textContent = "Copiar", 1200);
    });
});

$("#copyLinkBtn").addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(window.location.href);
        $("#copyLinkBtn").textContent = "✓ Enlace copiado";
        setTimeout(() => $("#copyLinkBtn").textContent = "Copiar enlace", 1500);
    } catch {
        alert(window.location.href);
    }
});

numberInput.addEventListener("keydown", event => {
    if (event.key === "Enter") convert();
});
