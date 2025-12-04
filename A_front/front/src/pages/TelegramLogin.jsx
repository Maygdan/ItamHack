import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import api from "../api";
import "../styles/TelegramLogin.css";

function TelegramLogin() {
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const location = useLocation();

    useEffect(() => {
        const codeFromUrl = searchParams.get('code');
        if (codeFromUrl) {
            setCode(codeFromUrl);
        }
    }, [searchParams]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await api.post("/api/login_with_code/", { code });

            // Save tokens to localStorage
            if (res.data.access && res.data.refresh) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);

                // Navigate to root - UserTypeRouter will handle redirection based on user type
                navigate(location.state?.from || "/", { replace: true });
            } else {
                throw new Error("No tokens received");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Неверный или просроченный код");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="telegram-login-container">
            <div className="telegram-login-card">
                <h2 className="telegram-login-title">Войти</h2>

                <form onSubmit={handleSubmit}>
                    <div className="telegram-login-form">
                        <input
                            type="text"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            placeholder="Введите код из бота"
                            required
                            className="telegram-login-input"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || !code.trim()}
                        className="telegram-login-button"
                    >
                        {loading ? 'Вход...' : 'Войти'}
                    </button>
                </form>

                <p className="telegram-login-info">
                    <a href="https://t.me/DateHackbot?start=login" target="_blank" rel="noopener noreferrer">Получить код в @DateHackbot</a>
                </p>

                <div className="telegram-login-links">
                    <a href="/login">Обычный вход</a>
                </div>
            </div>
        </div>
    );
}

export default TelegramLogin;
