document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll("input[tooltip]");
    let tooltip;

    inputs.forEach(input => {
        input.addEventListener("mouseenter", (e) => {
            const text = input.getAttribute("tooltip");

            tooltip = document.createElement("div");
            tooltip.className = "tooltip";
            tooltip.innerText = text;
            document.body.appendChild(tooltip);

            const rect = input.getBoundingClientRect();
            tooltip.style.left = rect.left + window.scrollX + "px";
            tooltip.style.top = rect.top + window.scrollY - 30 + "px";
        });

        input.addEventListener("mouseleave", () => {
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }
        });
    });

    const helpIcons = document.querySelectorAll(".help-icon");

    helpIcons.forEach(icon => {
        const dropdown = icon.nextElementSibling; 
        const helpText = icon.getAttribute("data-help");

        if (dropdown && helpText) {
            dropdown.innerText = helpText; 

            icon.addEventListener("click", () => {
                document.querySelectorAll(".help-dropdown.show").forEach(openDropdown => {
                    if (openDropdown !== dropdown) {
                        openDropdown.classList.remove("show");
                    }
                });
                dropdown.classList.toggle("show");
            });
        }
    });

    document.addEventListener("click", (event) => {
        helpIcons.forEach(icon => {
            const dropdown = icon.nextElementSibling;
            if (dropdown && dropdown.classList.contains("show") && !icon.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.classList.remove("show");
            }
        });
    });


    const formulario = document.querySelector('form');
    const inputNegocio = document.getElementById('negocio');

    formulario.addEventListener('submit', function(event) {
        const valorNegocio = inputNegocio.value.trim();
        const regex = /^[^,]+,\s*[^,]+$/; // Expresión regular para "algo, algo"

        if (!regex.test(valorNegocio)) {
            event.preventDefault(); // Evita que se envíe el formulario
            alert('Por favor, introduce el nombre del negocio y la ciudad en el formato: Nombre del negocio, Ciudad.');
            inputNegocio.classList.add('error'); 
            inputNegocio.focus(); 
        } else {
            inputNegocio.classList.remove('error'); 
        }
    });

    // Opcional: Eliminar la clase de error al escribir en el campo
    inputNegocio.addEventListener('input', function() {
        inputNegocio.classList.remove('error');
    });
});