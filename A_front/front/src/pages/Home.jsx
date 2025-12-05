import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import "../styles/Home.css";
import LoadingIndicator from "../components/LoadingIndicator";

function Home() {
  const [username, setUsername] = useState("");
  const [hackathons, setHackathons] = useState([]);
  const [hackathonDates, setHackathonDates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState({ year: new Date().getFullYear(), month: new Date().getMonth() });
  const navigate = useNavigate();

  useEffect(() => {
    getUserInfo();
    getHackathons();
    getHackathonDates();
  }, []);

  const getUserInfo = async () => {
    try {
      const token = localStorage.getItem('access');
      if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUsername(payload.username || 'Пользователь');
      }
    } catch (error) {
      console.log("Error getting user info:", error);
    }
  };

  const getHackathons = async () => {
    try {
      const response = await api.get("/api/hackathons/");
      setHackathons(response.data);
    } catch (error) {
      console.log("Error getting hackathons:", error);
    }
  };

  const getHackathonDates = async () => {
    try {
      const response = await api.get("/api/hackathon-dates/");
      setHackathonDates(response.data.hackathon_dates.map(date => new Date(date)));
    } catch (error) {
      console.log("Error getting hackathon dates:", error);
    } finally {
      setLoading(false);
    }
  };

  const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  const changeMonth = (delta) => {
    const newDate = new Date(currentView.year, currentView.month + delta, 1);
    setCurrentView({ year: newDate.getFullYear(), month: newDate.getMonth() });
  };

  const isHackathonDay = (year, month, day) => {
    return hackathonDates.some(hDate =>
      hDate.getFullYear() === year &&
      hDate.getMonth() === month &&
      hDate.getDate() === day
    );
  };

  const generateDays = () => {
    const daysInMonth = new Date(currentView.year, currentView.month + 1, 0).getDate();
    const firstDay = new Date(currentView.year, currentView.month, 1).getDay();
    const days = [];

    // Adjust first day (0 = Sunday, so shift)
    const adjustedFirstDay = (firstDay === 0 ? 6 : firstDay - 1);

    for (let i = 0; i < adjustedFirstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const isHackathon = isHackathonDay(currentView.year, currentView.month, day);
      days.push(
        <div
          key={day}
          className={`calendar-day ${isHackathon ? 'hackathon-day' : 'regular-day'}`}
        >
          {day}
        </div>
      );
    }

    return days;
  };

  if (loading) {
    return <LoadingIndicator />;
  }

  return (
    <div className="home-container">
      <div className="home-nav">
        <Link to="/profile">👤 Профиль</Link>
        <button
          className="home-logout-btn"
          onClick={() => { localStorage.clear(); navigate('/'); }}
        >
          🚪 Выйти
        </button>
      </div>

      <div className="calendar-container">
        <h2>Календарь хакатонов</h2>
        <div className="custom-calendar">
          <div className="calendar-header">
            <button onClick={() => changeMonth(-1)}>{'<'}</button>
            <span>{monthNames[currentView.month]} {currentView.year}</span>
            <button onClick={() => changeMonth(1)}>{'>'}</button>
          </div>
          <div className="calendar-weekdays">
            {dayNames.map(day => <div key={day}>{day}</div>)}
          </div>
          <div className="calendar-days">
            {generateDays()}
          </div>
        </div>
      </div>

      <div className="hackathons-container">
        <h2>Текущие хакатоны</h2>
        <div className="hackathons-list">
          {hackathons.map((hackathon) => (
            <div key={hackathon.id} className="hackathon-card">
              <div className="hackathon-name">
                <h3>{hackathon.name}</h3>
                <p className="hackathon-category">{hackathon.category_display}</p>
              </div>
              <div className="hackathon-info-row">
                <div className="hackathon-date">{hackathon.start_date}</div>
                <div className="hackathon-difficulty">{hackathon.difficulty_display}</div>
                <div className="hackathon-teams">{hackathon.registered_teams}/{hackathon.max_teams} команд</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;
