document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("zoom-container");
    const img = document.getElementById("product-img");
    const lens = document.getElementById("zoom-lens");
    const result = document.getElementById("zoom-result");

    if (!container || !img || !lens || !result) return;

    // Aguarda a imagem carregar totalmente para calcular o tamanho real
    img.onload = function() {
        setupZoom();
    };

    if (img.complete) {
        setupZoom();
    }

    function setupZoom() {
        result.style.backgroundImage = `url('${img.src}')`;

        // Fator de zoom baseado na proporção entre o tamanho real e o exibido
        const cx = img.naturalWidth / img.width;
        const cy = img.naturalHeight / img.height;

        result.style.backgroundSize = (img.naturalWidth) + "px " + (img.naturalHeight) + "px";

        container.addEventListener("mouseenter", function () {
            lens.style.display = "block";
            result.style.display = "block";
        });

        container.addEventListener("mouseleave", function () {
            lens.style.display = "none";
            result.style.display = "none";
        });

        container.addEventListener("mousemove", moveLens);

        function moveLens(e) {
            const rect = img.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;

            let lensWidth = lens.offsetWidth;
            let lensHeight = lens.offsetHeight;

            let pos_x = x - (lensWidth / 2);
            let pos_y = y - (lensHeight / 2);

            // Limites da lente dentro da imagem
            if (pos_x < 0) pos_x = 0;
            if (pos_x > img.width - lensWidth) pos_x = img.width - lensWidth;
            if (pos_y < 0) pos_y = 0;
            if (pos_y > img.height - lensHeight) pos_y = img.height - lensHeight;

            lens.style.left = pos_x + "px";
            lens.style.top = pos_y + "px";

            // Atualiza a posição do fundo ampliado acompanhando o mouse
            result.style.backgroundPosition = "-" + (pos_x * cx) + "px -" + (pos_y * cy) + "px";
        }
    }
});
