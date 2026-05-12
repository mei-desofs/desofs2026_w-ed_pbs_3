async function fetchWithRefresh(url, options = {}) {
    let response = await fetch(url, options);

    if (response.status === 401) {
        const refreshResp = await fetch(REFRESH_URL, { method: "POST" });

        if (refreshResp.ok) {
            response = await fetch(url, options);
        } else {
            window.location.href = LOGIN_URL;
        }
    }

    return response;
}