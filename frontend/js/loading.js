document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.querySelector('.progress-bar');
    const loadingText = document.querySelector('.loading-text');
    let progress = 0;

    // Simulación de la carga de información (esto lo controlarías desde tu backend)
    const interval = setInterval(() => {
        progress += getRandomIncrement(); // Incremento aleatorio para simular carga

        progressBar.style.width = `${progress}%`;

        if (progress >= 100) {
            clearInterval(interval);
            loadingText.textContent = 'Información generada. Redirigiendo...';
            // Aquí podrías redirigir a la siguiente página
            setTimeout(() => {
                window.location.href = '/resultado'; // Reemplaza '/resultado' con tu URL de destino
            }, 1500);
        } else if (progress > 30 && progress < 70) {
            progressBar.style.backgroundColor = '#FBBC05'; // Amarillo durante la carga media
        } else if (progress >= 70) {
            progressBar.style.backgroundColor = '#EA4335'; // Rojo casi al final
        }
    }, 200); // Intervalo de actualización (ajusta según necesites)

    // Función para obtener un incremento aleatorio (simula diferentes velocidades de carga)
    function getRandomIncrement() {
        return Math.random() * 2 + 1; // Incrementos entre 2% y 7%
    }
});

function checkAnalysisStatus() {
    // Consulta el estado del análisis usando el ID único
    fetch('/analysis_status/{{ analysis_id }}')
        .then(response => {
            if (response.status === 200) {
                // Si el estado es 200 (OK), el análisis está listo, redirige a la página de resultados
                window.location.href = '/analysis_status/{{ analysis_id }}';
            } else if (response.status === 202) {
                // Si el estado es 202 (Accepted), sigue procesando, espera y vuelve a comprobar
                setTimeout(checkAnalysisStatus, 5000); // Comprueba cada 5 segundos
            } else {
                // Maneja otros errores
                console.error('Error al verificar el estado:', response.status);
                document.getElementById('status-message').innerText = 'Ocurrió un error al verificar el estado del análisis.';
            }
        })
        .catch(error => {
            console.error('Error de red:', error);
            document.getElementById('status-message').innerText = 'Error de red al verificar el estado.';
        });
}
// Inicia la comprobación cuando la página se carga
document.addEventListener('DOMContentLoaded', checkAnalysisStatus);