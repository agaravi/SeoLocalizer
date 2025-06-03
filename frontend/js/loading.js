document.addEventListener('DOMContentLoaded', function() {
    // Definimos una función para iniciar el proceso después de que el DOM esté listo
    function initializeLoading() {
        const bodyElement = document.body;
        const analysisId = bodyElement.dataset.analysisId;
        const nombreNegocio = bodyElement.dataset.nombreNegocio;

        if (!analysisId || !nombreNegocio) {
            console.error("Error: analysisId o nombreNegocio no encontrado en el dataset del body después de esperar. Redirigiendo a error genérico.");
            window.location.href = `/analysis_error/no-id-found`; // Redirige al backend para manejar el error
            return;
        }

        const progressBar = document.querySelector('.progress-bar');
        const loadingText = document.querySelector('.loading-text');
        let simulatedProgress = 0;
        let redirecting = false;
        let simulationInterval;

        function getRandomIncrement() {
            return Math.random() * 5 + 1;
        }

        function startProgressSimulation() {
            simulationInterval = setInterval(() => {
                if (simulatedProgress < 95) {
                    simulatedProgress += getRandomIncrement();
                    if (simulatedProgress > 95) simulatedProgress = 95;
                    progressBar.style.width = `${simulatedProgress}%`;
                }
            }, 1000);
        }

        function checkAnalysisStatus() {
            if (redirecting) return;

            fetch(`/analysis_status/${analysisId}`)
                .then(response => {
                    // Si la respuesta no es OK, podría ser un error de servidor (500) antes de JSON
                    if (!response.ok) {
                        return response.text().then(text => { // Intentar leer como texto si no es JSON esperado
                            throw new Error(`Error HTTP: ${response.status} - ${text}`);
                        });
                    }
                    return response.json(); // Si es OK, esperar JSON
                })
                .then(data => {
                    if (data.status === 'completed') {
                        clearInterval(simulationInterval);
                        simulatedProgress = 100;
                        progressBar.style.width = '100%';
                        loadingText.textContent = '¡Análisis completado! Redirigiendo al informe...';
                        redirecting = true;

                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 1500);
                    } else if (data.status === 'error') {
                        clearInterval(simulationInterval);
                        loadingText.textContent = 'Error en el análisis. Redirigiendo a la página de error...';
                        redirecting = true;

                        setTimeout(() => {
                            window.location.href = data.redirect_url; // Esta URL ya viene del backend (ej. /analisis_SEO_error_<nombre>)
                        }, 1500);
                    } else if (data.status === 'in_progress') {
                        loadingText.textContent = 'Análisis en progreso...';
                        setTimeout(checkAnalysisStatus, 5000);
                    }
                })
                .catch(error => {
                    clearInterval(simulationInterval);
                    loadingText.textContent = 'Error de comunicación con el servidor.';
                    console.error('Error de fetch:', error);
                    redirecting = true;
                    // Redirige al backend en caso de un error de red o fetch grave
                    setTimeout(() => {
                        window.location.href = `/analysis_error_generic/network-error-from-js`; // Usa la ruta de error genérica
                    }, 1500);
                });
        }

        startProgressSimulation();
        checkAnalysisStatus();
    }

    // Usar un temporizador para esperar un momento y luego verificar los atributos data-
    // Esto es útil si los atributos se cargan dinámicamente o con un ligero retraso.
    let checkAttempts = 0;
    const maxCheckAttempts = 10; // Intentar 10 veces
    const checkInterval = 200; // Cada 200ms

    const checkDataAttributes = setInterval(() => {
        const bodyElement = document.body;
        const analysisId = bodyElement.dataset.analysisId;
        const nombreNegocio = bodyElement.dataset.nombreNegocio;

        if (analysisId && nombreNegocio) {
            clearInterval(checkDataAttributes); // Datos encontrados, detener la verificación
            initializeLoading(); // Iniciar la lógica de carga
        } else {
            checkAttempts++;
            if (checkAttempts >= maxCheckAttempts) {
                clearInterval(checkDataAttributes); // Superó los intentos, detener la verificación
                console.error("Error: analysisId o nombreNegocio no encontrado en el dataset del body después de múltiples intentos. Redirigiendo a error genérico.");
                // Redirige directamente al backend para manejar este error crítico de inicialización
                // Podemos usar una ruta de error genérica existente.
                window.location.href = `/analysis_error_generic/initial-data-missing`; // O una más específica si la tuvieras
            }
        }
    }, checkInterval);
});