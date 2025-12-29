// ✅ services/authService.js
import api from "./api";

export const login = async (userid, password) => {
  const res = await api.post("/auth/login", {
    userid,
    password,
  });
  return res.data;
};

export const getMe = async () => {
  const res = await api.get("/auth/me");
  return res.data;
};

export const logout = () => {
  localStorage.removeItem("authToken");
  localStorage.removeItem("user");
};
