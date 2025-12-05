import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function UserTypeRouter() {
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        // First, try to get current user info from localStorage or API
        const accessToken = localStorage.getItem('access');
        const refreshToken = localStorage.getItem('refresh');

        console.log('UserTypeRouter: checking tokens');
        console.log('access:', !!accessToken, 'refresh:', !!refreshToken);

        if (!accessToken || !refreshToken) {
            // No tokens at all - redirect to login
            console.log('UserTypeRouter: no tokens, redirecting to login');
            setLoading(false);
            navigate("/login", { replace: true });
            return;
        }

        // Always redirect to home for authenticated users
        navigate("/home", { replace: true });
    }, [navigate]);

    const checkUserType = async () => {
        try {
            console.log('UserTypeRouter: fetching profile');
            // Check user profile to determine type
            const res = await api.get("/api/profile/");
            const profile = res.data;
            console.log('UserTypeRouter: profile user_type?', profile.is_telegram_user);

            if (profile && profile.is_telegram_user) {
                // Telegram user - redirect to profile
                console.log('UserTypeRouter: redirecting to /profile');
                navigate("/profile", { replace: true });
            } else {
                // Regular user - redirect to home
                console.log('UserTypeRouter: redirecting to /home');
                navigate("/home", { replace: true });
            }
        } catch (error) {
            console.log("UserTypeRouter: Profile check failed:", error);

            // If profile doesn't exist, assume telegram user and redirect to profile
            // Profile component will handle missing profile case
            if (error.response?.status === 404 && localStorage.getItem('access')) {
                console.log("UserTypeRouter: Profile not found, assuming telegram user");
                navigate("/profile", { replace: true });
            } else {
                // Auth error or other issue - redirect to login
                console.log("UserTypeRouter: auth error or other, redirecting to login");
                navigate("/login", { replace: true });
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return null; // Component only handles redirecting
}

export default UserTypeRouter;
