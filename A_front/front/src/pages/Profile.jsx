import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";
import "../styles/Profile.css";
import LoadingIndicator from "../components/LoadingIndicator";

function Profile() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({
        bio: '',
        skills: '',
        experience_months: 0
    });
    const navigate = useNavigate();

useEffect(() => {
    getProfile();
}, []);

const getProfile = async () => {
    try {
        const res = await api.get("/api/profile/");
        setProfile(res.data);
        setFormData({
            display_name: res.data.display_name || '',
            bio: res.data.bio || '',
            skills: res.data.skills || '',
            experience_months: res.data.experience_months || 0
        });
        } catch (error) {
            console.error("Error fetching profile:", error);
            // If no profile exists, show a message or create one
            if (error.response?.status === 404) {
                alert("Профиль не найден");
                navigate("/");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'experience_months' ? parseInt(value) || 0 : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await api.put("/api/profile/", formData);
            setProfile(res.data);
            setEditing(false);
            alert("Профиль обновлен!");
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("Ошибка при обновлении профиля");
        }
    };

    const handleAvatarChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formDataObj = new FormData();
        formDataObj.append('avatar', file);

        try {
            const res = await api.patch("/api/profile/", formDataObj, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setProfile(res.data);
            alert("Фото обновлено!");
        } catch (error) {
            console.error("Error updating avatar:", error);
            alert("Ошибка при обновлении фото");
        }
    };

    if (loading) {
        return <LoadingIndicator />;
    }

    // Handle case when profile doesn't exist yet for Telegram users
    if (!profile) {
        return <div className="profile-container">
            <h1>Личный кабинет</h1>
            <p>Профиль не найден. Возможное решение - обновите страницу или перезайдите.</p>
        </div>;
    }

    return (
        <div className="profile-container">
            <div className="profile-header">
                <h1>Личный кабинет</h1>
                <div className="profile-nav">
                    <Link to="/home">🏠 Главная</Link>
                    <button
                        onClick={() => { localStorage.clear(); navigate('/'); }}
                        style={{ marginLeft: '10px', background: '#ff4444', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '5px', cursor: 'pointer' }}
                    >
                        🚪 Выйти
                    </button>
                </div>
                {!editing && (
                    <button
                        className="profile-edit-btn"
                        onClick={() => setEditing(true)}
                    >
                        ✏️ Редактировать
                    </button>
                )}
            </div>

            <div className="profile-content">
                <div className="profile-avatar-section">
                    <div className="avatar-container">
                        {profile.avatar ? (
                            <img
                                src={profile.avatar}
                                alt="Аватар"
                                className="profile-avatar"
                            />
                        ) : (
                            <div className="profile-avatar-placeholder">
                                📷
                            </div>
                        )}
                        {editing && (
                            <label className="avatar-upload-btn">
                                <span className="plus-icon">+</span>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleAvatarChange}
                                    style={{ display: 'none' }}
                                />
                            </label>
                        )}
                    </div>
                </div>

                <div className="profile-info-section">
                    {!editing ? (
                        <>
                            <div className="profile-field">
                                <label>Отображаемое имя:</label>
                                <span>{profile.display_name || 'Не указано'}</span>
                            </div>

                            <div className="profile-field">
                                <label>Логин учетной записи:</label>
                                <span>{profile.username}</span>
                            </div>

                            {profile.level_display && (
                                <div className="profile-field">
                                    <label>Уровень:</label>
                                    <span className={`level-${profile.level}`}>
                                        {profile.level_display}
                                    </span>
                                </div>
                            )}

                            {!profile.level_display && (
                                <div className="profile-field">
                                    <label>Уровень:</label>
                                    <span className="level-beginner">Начинающий</span>
                                </div>
                            )}

                            {profile.experience_years && (
                                <div className="profile-field">
                                    <label>Опыт разработки:</label>
                                    <span>{profile.experience_years}</span>
                                </div>
                            )}

                            {profile.skills && (
                                <div className="profile-field">
                                    <label>Стек технологий:</label>
                                    <span>{profile.skills}</span>
                                </div>
                            )}

                            {profile.bio && (
                                <div className="profile-field">
                                    <label>О себе:</label>
                                    <span>{profile.bio}</span>
                                </div>
                            )}

                            {profile.hackathons_participated !== undefined && (
                                <div className="profile-field">
                                    <label>Участий в хакатонах:</label>
                                    <span>{profile.hackathons_participated}</span>
                                </div>
                            )}
                        </>
                    ) : (
                        <form onSubmit={handleSubmit} className="profile-edit-form">
                            <div className="form-field">
                                <label>Отображаемое имя:</label>
                                <input
                                    type="text"
                                    name="display_name"
                                    value={formData.display_name}
                                    onChange={handleInputChange}
                                    placeholder="Ваше имя для отображения"
                                    maxLength="100"
                                />
                            </div>

                            <div className="form-field">
                                <label>Опыт разработки (месяцы):</label>
                                <input
                                    type="number"
                                    name="experience_months"
                                    value={formData.experience_months}
                                    onChange={handleInputChange}
                                    min="0"
                                    max="600"
                                />
                            </div>

                            <div className="form-field">
                                <label>Стек технологий:</label>
                                <textarea
                                    name="skills"
                                    value={formData.skills}
                                    onChange={handleInputChange}
                                    rows="3"
                                    placeholder="Например: Python, React, Node.js..."
                                />
                            </div>

                            <div className="form-field">
                                <label>О себе:</label>
                                <textarea
                                    name="bio"
                                    value={formData.bio}
                                    onChange={handleInputChange}
                                    rows="4"
                                    placeholder="Расскажите о себе..."
                                />
                            </div>

                            <div className="form-actions">
                                <button type="submit" className="save-btn">💾 Сохранить</button>
                                <button
                                    type="button"
                                    className="cancel-btn"
                                    onClick={() => {
                                        setFormData({
                                            bio: profile.bio || '',
                                            skills: profile.skills || '',
                                            experience_months: profile.experience_months || 0
                                        });
                                        setEditing(false);
                                    }}
                                >
                                    ❌ Отмена
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Profile;
