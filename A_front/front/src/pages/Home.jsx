import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import "../styles/Home.css";
import LoadingIndicator from "../components/LoadingIndicator";

function Home() {
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getUserInfo();
  }, []);

  const getUserInfo = async () => {
    try {
      // We'll create a simple endpoint to get current user info
      // For now, just decode from token or show generic welcome
      const token = localStorage.getItem('access');
      if (token) {
        // Simple decode just for username display
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUsername(payload.username || 'Пользователь');
      }
    } catch (error) {
      console.log("Error getting user info:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingIndicator />;
  }

  return (
    <div className="home-container">
      <div className="home-title-centered">
        <h1 className="home-title">Удачной разработки! 🚀</h1>
      </div>
      <div className="home-nav-centered">
        <Link to="/profile">👤 Профиль</Link>
        <button
          className="home-logout-btn"
          onClick={() => { localStorage.clear(); navigate('/'); }}
        >
          🚪 Выйти
        </button>
      </div>
      <p className="home-subtitle">Добро пожаловать, {username}!</p>

      <div className="home-options">
        <div className="option-card" onClick={() => navigate('/telegram-login')}>
          <h3>🔐 Вход через Telegram</h3>
          <p>Используйте код для авторизации через бота</p>
        </div>

        <div className="option-card" onClick={() => navigate('/login')}>
          <h3>👤 Вход по логину/паролю</h3>
          <p>Стандартная аутентификация</p>
        </div>

        <div className="option-card" onClick={() => alert('Выйти из системы')}>
          <h3>🚪 Выход</h3>
          <p>Завершить сессию</p>
        </div>
      </div>
    </div>
  );
}

export default Home;
