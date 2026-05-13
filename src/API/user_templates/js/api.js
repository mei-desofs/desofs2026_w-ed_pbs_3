
async function apiRequest(url, options = {}) {
    console.log("Chamada API para:", url) // DEBUG
    // cookies (JWT) são enviadas no pedido
    options.credentials = 'include'; 

    let response = await fetch(url, options);

    // Token expirou
    if (response.status === 401) {
        console.log("Access token expirado. A tentar renovar...");

        // variável global definida no template
        const refreshUrl = window.REFRESH_URL || '/refresh'; 

        try {
            // endpoint de refresh
            const refreshResponse = await fetch(refreshUrl, {
                method: 'POST',
                credentials: 'include',
                headers: {'Content-Type': 'application/json'}
            });

            if (refreshResponse.ok) {
                console.log("Token renovado com sucesso. Repetindo pedido original.");
                return await fetch(url, options);
            } else {
                const errorData = await refreshResponse.json();
                console.error("Erro no servidor ao renovar:", errorData);
                throw new Error("Falha no refresh");
            }
        } catch (err) {
            console.warn("Sessão terminada:", err.message);
            // Redireciona para login
            window.location.href = window.LOGIN_URL || '/';
            return;
        }
    }

    return response;
}