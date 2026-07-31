const API_BASE = "http://127.0.0.1:8000";

export const getAllStores = async () => {
    const res = await fetch(`${API_BASE}/api/stores`);
    return res.json();
};

export const searchStores = async (query) => {
    const res = await fetch(`${API_BASE}/api/stores/search?q=${query}`);
    return res.json();
};

export const runAgent = async (storeId, storeName) => {
    const res = await fetch(`${API_BASE}/api/agents/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store_id: storeId, store_name: storeName }),
    });
    return res.json();
};

export const getAgentStatus = async (jobId) => {
    const res = await fetch(`${API_BASE}/api/agents/status/${jobId}`);
    return res.json();
};

export const loginUser = async (username, password) => {
    const res = await fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    return res.json();
};