document.addEventListener('DOMContentLoaded', function() {
    const analysisId = document.body.dataset.analysisId; // Obtenemos el analysisId del dataset del body
    const businessName = document.body.dataset.businessName; 
    const progressBar = document.querySelector('.progress-bar');
    const loadingText = document.querySelector('.loading-text'); // Este será nuestro status-message
    let simulatedProgress = 0;
    let redirecting = false; // Flag para evitar múltiples redirecciones
    let simulationInterval; // Variable para almacenar el ID del intervalo de simulación

    function getRandomIncrement() {
        // Un incremento más suave para simular progresión
        return Math.random() * 5 + 1; // Incrementos entre 1% y 6%
    }

    function startProgressSimulation() {
        // Esta simulación es solo visual, la redirección la controla el backend
        simulationInterval = setInterval(() => {
            if (simulatedProgress < 95) { // No llegar al 100% en la simulación
                simulatedProgress += getRandomIncrement();
                if (simulatedProgress > 95) simulatedProgress = 95; // Tope para no llegar al 100%
                progressBar.style.width = `${simulatedProgress}%`;

                // Cambiar color de la barra (opcional, si lo defines en loading.css no es necesario aquí)
                // if (simulatedProgress > 30 && simulatedProgress < 70) {
                //     progressBar.style.backgroundColor = '#FBBC05'; // Amarillo
                // } else if (simulatedProgress >= 70) {
                //     progressBar.style.backgroundColor = '#EA4335'; // Rojo
                // }
            }
        }, 1000); // Actualiza la barra cada 1 segundo
    }

    function checkAnalysisStatus() {
        if (redirecting) return; // Si ya estamos redirigiendo, no hacer nada

        fetch(`/analisis_SEO_${businessName}`)
            .then(response => {
                // Si el backend responde con 200, significa que el análisis está listo
                if (response.status === 200) {
                    clearInterval(simulationInterval); // Detiene la simulación de la barra
                    simulatedProgress = 100; // Fija la barra al 100%
                    progressBar.style.width = '100%';
                    // Puedes cambiar el color a verde aquí si lo deseas, o dejar que el CSS lo maneje
                    // progressBar.style.backgroundColor = '#34A853'; // Verde (completado)

                    loadingText.textContent = '¡Análisis completado! Redirigiendo al informe...';
                    redirecting = true; // Establece la bandera de redirección

                    // Pequeño retardo visual antes de la redirección final
                    //setTimeout(() => {
                    //    window.location.href = `/analysis_status/${analysisId}`; // Redirige a la página de resultados
                    //}, 1500); // Redirige después de 1.5 segundos
                } else if (response.status === 202) {
                    // Si el estado es 202 (Accepted), sigue procesando
                    loadingText.textContent = 'Análisis en progreso... Por favor, espera.';
                    setTimeout(checkAnalysisStatus, 5000); // Vuelve a comprobar cada 5 segundos
                } else {
                    // Maneja otros errores
                    clearInterval(simulationInterval); // Detiene la simulación
                    // progressBar.style.backgroundColor = '#FF0000'; // Rojo (error)
                    loadingText.textContent = `Ocurrió un error: ${response.status}. Por favor, inténtalo de nuevo.`;
                    console.error('Error al verificar el estado:', response.status);
                }
            })
            .catch(error => {
                clearInterval(simulationInterval); // Detiene la simulación
                // progressBar.style.backgroundColor = '#FF0000'; // Rojo (error)
                loadingText.textContent = 'Error de red al verificar el estado. Asegúrate de tener conexión.';
                console.error('Error de red:', error);
            });
    }

    // Inicia la simulación de la barra de progreso y la comprobación del estado
    startProgressSimulation();
    checkAnalysisStatus();
});