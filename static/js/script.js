// Exemplo de validação de formulário antes do envio
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    
    form.addEventListener("submit", function (event) {
        const password = document.querySelector("input[name='senha']").value;
        const username = document.querySelector("input[name='loginUser']").value;

        if (username.trim() === "" || password.trim() === "") {
            event.preventDefault(); // Previne o envio do formulário
            alert("Por favor, preencha todos os campos.");
        }
    });
});

// Função para exibir uma mensagem ao cadastrar um produto

