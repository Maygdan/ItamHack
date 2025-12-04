import Form from "../components/Form"
import { useEffect } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"

function Login() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const code = searchParams.get('code');

    useEffect(() => {
        if (code) {
            // Redirect to telegram login page if code is in URL
            navigate(`/telegram-login?code=${code}`);
        }
    }, [code, navigate]);

    return (
        <div>
            <Form route="/api/token/" method="login" inFormElement={<a href="/telegram-login">Войти по коду из Telegram</a>} />
        </div>
    )
}

export default Login
