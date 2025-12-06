import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/MyTeams.css";

function MyTeams() {
  const navigate = useNavigate();
  const [teams, setTeams] = useState([]);
  const [potentialMembers, setPotentialMembers] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMyTeams();
  }, []);

  const fetchMyTeams = async () => {
    try {
      const response = await api.get(`/api/my_teams/`);
      setTeams(response.data);
    } catch (error) {
      console.error("Error fetching my teams:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPotential = async (hackathonId, teamId) => {
    try {
      const response = await api.get(`/api/hackathons/${hackathonId}/potential_members/`);
      setPotentialMembers(prev => ({ ...prev, [teamId]: response.data }));
    } catch (error) {
      alert('Ошибка загрузки участников: ' + error.response?.data?.error);
    }
  };

  const inviteMember = async (teamId, userId) => {
    try {
      await api.post(`/api/teams/${teamId}/invite/`, { user_id: userId });
      alert('Приглашение отправлено!');
      setPotentialMembers(prev => ({ ...prev, [teamId]: prev[teamId].filter(u => u.id !== userId) }));
    } catch (error) {
      alert('Ошибка: ' + error.response?.data?.error);
    }
  };

  const deleteTeam = async (teamId) => {
    if (!confirm('Удалить команду?')) return;
    try {
      await api.delete(`/api/teams/${teamId}/delete/`);
      alert('Команда удалена!');
      fetchMyTeams();
    } catch (error) {
      alert('Ошибка: ' + error.response?.data?.error);
    }
  };

  const viewProfile = (user) => {
    alert(`Профиль ${user.display_name || user.username}: ${user.bio || 'Нет описания'}`);
  };

  if (loading) {
    return <div>Загрузка...</div>;
  }

  return (
    <div className="my-teams-container">
      <div className="nav">
        <button onClick={() => navigate(-1)}>← Назад</button>
      </div>
      <h1>Мои команды</h1>
      {teams.length === 0 ? (
        <p>У вас нет команд.</p>
      ) : (
        <div className="teams-list">
          {teams.map((team) => (
            <div key={team.id} className="team-card">
              <h3>{team.name}</h3>
              <p>Капитан: {team.captain_username}</p>
              <p>Участников: {team.member_count}/{team.size_max}</p>
              <h4>Члены команды:</h4>
              <ul>
                {team.members_list.map((member) => (
                  <li key={member.id}>
                    {member.username} <button onClick={() => viewProfile(member)}>Просмотр</button>
                  </li>
                ))}
              </ul>
              {team.captain_username === localStorage.getItem('username') && (
                <>
                  <button onClick={() => {
                    if (!potentialMembers[team.id]) fetchPotential(team.hackathon, team.id);
                    setPotentialMembers(prev => ({ ...prev, [team.id]: prev[team.id] || [] }));
                  }}>
                    {potentialMembers[team.id] ? 'Скрыть потенциальных' : 'Показать потенциальных'}
                  </button>
                  {potentialMembers[team.id] && (
                    <div className="potentials">
                      {potentialMembers[team.id].map((user) => (
                        <div key={user.id}>
                          {user.display_name || user.username} - {user.level}
                          <button onClick={() => inviteMember(team.id, user.id)}>Пригласить</button>
                        </div>
                      ))}
                    </div>
                  )}
                  <button onClick={() => deleteTeam(team.id)}>Удалить команду</button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyTeams;
