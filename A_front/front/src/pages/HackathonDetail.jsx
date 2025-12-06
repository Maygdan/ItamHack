import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api from "../api";
import "../styles/HackathonDetail.css";
import LoadingIndicator from "../components/LoadingIndicator";

function HackathonDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [hackathonData, setHackathonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showMenu, setShowMenu] = useState(false);
  const [showCreateTeamForm, setShowCreateTeamForm] = useState(false);
  const [showJoinTeamForm, setShowJoinTeamForm] = useState(false);
  const [availableTeams, setAvailableTeams] = useState([]);
  const [potentialMembers, setPotentialMembers] = useState([]);
  const [isParticipated, setIsParticipated] = useState(false);  // Участник хакатона

  useEffect(() => {
    fetchHackathonDetail();
  }, [id]);

  const fetchHackathonDetail = async () => {
    try {
      const response = await api.get(`/api/hackathons/${id}/`);
      setHackathonData(response.data);
    } catch (error) {
      console.error("Error fetching hackathon details:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleParticipate = async () => {
    if (!showMenu) {
      try {
        await api.post(`/api/hackathons/${id}/participate/`);
        setIsParticipated(true);
        setShowMenu(true);
      } catch (error) {
        alert('Ошибка регистрации: ' + error.response?.data?.error);
      }
    } else {
      setShowMenu(false);
    }
  };

  const handleCreateTeam = async () => {
    if (!isParticipated) return;
    setShowCreateTeamForm(true);
    setShowMenu(false);
    // Загрузить потенциальных участников
    try {
      const response = await api.get(`/api/hackathons/${id}/potential_members/`);
      setPotentialMembers(response.data);
    } catch (error) {
      alert('Ошибка загрузки участников: ' + error.response?.data?.error);
    }
  };

  const submitCreateTeam = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const teamName = formData.get('teamName');
    try {
      const response = await api.post(`/api/hackathons/${id}/create_team/`, {
        name: teamName,
        size_min: hackathonData.hackathon.team_size_min,
        size_max: hackathonData.hackathon.team_size_max,
      });
      alert('Команда создана!');
      setShowCreateTeamForm(false);
      fetchHackathonDetail();  // Обновить список команд
    } catch (error) {
      alert('Ошибка создания команды: ' + error.response?.data?.error);
    }
  };

  const handleJoinTeam = async () => {
    if (!isParticipated) return;
    setShowJoinTeamForm(true);
    setShowMenu(false);
    try {
      const response = await api.get(`/api/hackathons/${id}/available_teams/`);
      setAvailableTeams(response.data);
    } catch (error) {
      alert('Ошибка загрузки команд: ' + error.response?.data?.error);
    }
  };

  const submitJoinRequest = async (teamId) => {
    try {
      await api.post(`/api/teams/${teamId}/join/`);
      alert('Запрос отправлен!');
      setShowJoinTeamForm(false);
    } catch (error) {
      alert('Ошибка запроса: ' + error.response?.data?.error);
    }
  };

  if (loading) {
    return <LoadingIndicator />;
  }

  if (!hackathonData) {
    return <div>Хакатон не найден</div>;
  }

  const { hackathon, teams } = hackathonData;

  return (
    <div className="hackathon-detail-container">
      <div className="detail-nav">
        <Link to="/home">← Назад к хакатонам</Link>
      </div>

      <div className="hackathon-info">
        <h1>{hackathon.name}</h1>
        <p><strong>Даты проведения:</strong> {hackathon.start_date} - {hackathon.end_date}</p>
        <p><strong>Время:</strong> {hackathon.date_range}</p>
        <p><strong>Сложность:</strong> {hackathon.difficulty_display}</p>
        <p><strong>Категория:</strong> {hackathon.category_display}</p>
        <p><strong>Размер команды:</strong> {hackathon.team_size_min} - {hackathon.team_size_max} участников</p>
        <p><strong>Зарегистрировано команд:</strong> {hackathon.registered_teams}/{hackathon.max_teams}</p>
        <p><strong>Партнёры:</strong> {hackathon.partners || 'Нет'}</p>
        <p><strong>Требуемые роли:</strong> {hackathon.required_roles.join(', ')}</p>
      </div>

      <div className="participation-section">
        <h2>Участвовать</h2>
        <div className="participation-wrapper">
          <button className="participate-btn" onClick={handleParticipate}>
            {isParticipated ? 'Дополнительные опции' : 'Принять участие'}
          </button>
          {showMenu && isParticipated && (
            <div className="participation-menu">
              <button onClick={handleCreateTeam}>Создать команду</button>
              <button onClick={handleJoinTeam}>Присоединиться к команде</button>
            </div>
          )}
        </div>
      </div>

      {showCreateTeamForm && (
        <div className="form-overlay">
          <div className="form-container">
            <h3>Создать команду</h3>
            <form onSubmit={submitCreateTeam}>
              <label>Название команды:</label>
              <input type="text" name="teamName" required />
              <button type="submit">Создать</button>
              <button type="button" onClick={() => setShowCreateTeamForm(false)}>Отмена</button>
            </form>
          </div>
        </div>
      )}

      {showJoinTeamForm && (
        <div className="form-overlay">
          <div className="form-container">
            <h3>Доступные команды</h3>
            <div className="teams-join-list">
              {availableTeams.map((team) => (
                <div key={team.id} className="join-team-item">
                  <p><strong>{team.name}</strong> - Капитан: {team.captain_username} ({team.member_count}/{team.size_max})</p>
                  <button onClick={() => submitJoinRequest(team.id)}>Подать заявку</button>
                </div>
              ))}
            </div>
            <button onClick={() => setShowJoinTeamForm(false)}>Закрыть</button>
          </div>
        </div>
      )}

      <div className="teams-section">
        <h2>Команды</h2>
        <div className="teams-list">
          {teams.map((team) => (
            <div key={team.id} className="team-card">
              <h3>{team.name}</h3>
              <p><strong>Капитан:</strong> {team.captain_username}</p>
              <p><strong>Участников:</strong> {team.member_count}/{team.size_max}</p>
              <p><strong>Члены:</strong> {team.members_list.map(m => m.username).join(', ')}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default HackathonDetail;
