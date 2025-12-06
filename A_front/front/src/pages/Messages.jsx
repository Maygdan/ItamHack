import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/Messages.css";  // Создадим стиль

function Messages() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await api.get(`/api/messages/`);
      setMessages(response.data);
    } catch (error) {
      console.error("Error fetching messages:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (messageId, action) => {
    try {
      await api.post(`/api/messages/${messageId}/respond/`, { action });
      alert(`Запрос ${action === 'accept' ? 'принят' : 'отклонен'}`);
      fetchMessages();  // Обновить список
    } catch (error) {
      alert('Ошибка: ' + error.response?.data?.error);
    }
  };

  if (loading) {
    return <div>Загрузка...</div>;
  }

  return (
    <div className="messages-container">
      <div className="nav">
        <button onClick={() => navigate(-1)}>← Назад</button>
      </div>
      <h1>Сообщения</h1>
      <div className="messages-list">
        {messages.map((msg) => (
          <div key={msg.id} className="message-card">
            <p><strong>От:</strong> {msg.sender_username}</p>
            <p><strong>Команда:</strong> {msg.team_name}</p>
            <p>{msg.text}</p>
            <p><strong>Статус:</strong> {msg.status}</p>
            <p><small>{new Date(msg.sent_at).toLocaleString()}</small></p>
            {msg.status === 'pending' && (
              <div className="action-buttons">
                <button onClick={() => handleRespond(msg.id, 'accept')}>Принять</button>
                <button onClick={() => handleRespond(msg.id, 'decline')}>Отклонить</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Messages;
