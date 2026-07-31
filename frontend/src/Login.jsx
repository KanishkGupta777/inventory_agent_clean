import { useState } from "react";
import { loginUser } from "./api";
import "./Login.css";

function Login({ onLoginSuccess }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        const data = await loginUser(username, password);

        if (data.error) {
            setError(data.error);
            setLoading(false);
        } else {
            onLoginSuccess(data); // Send user data back to App.jsx
        }
    };

    return (
        <div className="login-container">
            <form className="login-card" onSubmit={handleSubmit}>
                <h2>🍽️ Restaurant AI Login</h2>
                <p style={{ color: "#666", marginBottom: "20px", fontSize: "14px" }}>Enter your credentials to continue</p>

                {error && <p className="login-error">{error}</p>}

                <div className="input-group">
                    <label>Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="e.g. admin or manager1"
                        required
                    />
                </div>

                <div className="input-group">
                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        required
                    />
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>

                <div className="demo-creds">
                    <p><b>Demo Admin:</b> admin / admin123</p>
                    <p><b>Demo Manager:</b> manager1 / pass123</p>
                </div>
            </form>
        </div>
    );
}

export default Login;