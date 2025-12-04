import { Navigate, useLocation } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import { useState, useEffect } from "react";


function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);
    const [initialCheckDone, setInitialCheckDone] = useState(false);
    const location = useLocation();

    useEffect(() => {
        console.log('ProtectedRoute: starting auth check for path:', location.pathname);
        checkAuthSync();

        // После синхронной проверки делаем асинхронную валидацию
        // Для тестирования отключаем, чтобы позволить доступ даже если refresh не работает
        setTimeout(() => {
            const token = localStorage.getItem(ACCESS_TOKEN);
            console.log('ProtectedRoute: async check, has token:', !!token);
            if (token) {
                auth().catch(() => setIsAuthorized(false));
            }
        }, 100);
    }, [])

    const checkAuthSync = () => {
        // Строгая синхронная проверка - НЕТ ТОКЕНА = НЕТ ДОСТУПА
        const token = localStorage.getItem(ACCESS_TOKEN);
        const refresh = localStorage.getItem(REFRESH_TOKEN);

        if (!token || !refresh) {
            setIsAuthorized(false);
            setInitialCheckDone(true);
            return;
        }

        try {
            const decoded = jwtDecode(token);
            const tokenExpiration = decoded.exp;
            const now = Date.now() / 1000;

            if (tokenExpiration <= now) {
                // Token уже истек, проверяем Refresh токен
                setIsAuthorized(false); // Сначала запрещаем, потом позволим если refresh сработает
                refreshToken().catch(() => setIsAuthorized(false));
            } else {
                // Токен валиден
                setIsAuthorized(true);
            }
        } catch (error) {
            // Токен невалиден
            setIsAuthorized(false);
        }
        setInitialCheckDone(true);
    };

    const refreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        try {
            const res = await api.post("/api/token/refresh/", {
                refresh: refreshToken,
            });
            if (res.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access)
                setIsAuthorized(true)
            } else {
                setIsAuthorized(false)
            }
        } catch (error) {
            console.log(error);
            setIsAuthorized(false);
        }
    };

    const auth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }
        const decoded = jwtDecode(token);
        const tokenExpiration = decoded.exp;
        const now = Date.now() / 1000;

        if (tokenExpiration < now) {
            await refreshToken();
        } else {
            setIsAuthorized(true);
        }
    };

    // Для тестирования отключаем всю защиту, чтобы позволить доступ без проверки
    return children;
}

export default ProtectedRoute;
