import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import { fetchCurrentUser, login as loginRequest, signup as signupRequest } from "../features/auth/api";

const AUTH_TOKEN_KEY = "neurolearn_access_token";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(AUTH_TOKEN_KEY));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const persistToken = useCallback((nextToken) => {
    if (nextToken) {
      localStorage.setItem(AUTH_TOKEN_KEY, nextToken);
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY);
    }
    setToken(nextToken);
  }, []);

  const refreshUser = useCallback(
    async (authToken = token) => {
      if (!authToken) {
        setUser(null);
        return null;
      }
      const me = await fetchCurrentUser(authToken);
      setUser(me);
      return me;
    },
    [token],
  );

  useEffect(() => {
    let active = true;

    async function initialize() {
      if (!token) {
        if (active) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const me = await fetchCurrentUser(token);
        if (active) {
          setUser(me);
        }
      } catch (error) {
        if (active) {
          persistToken(null);
          setUser(null);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    initialize();

    return () => {
      active = false;
    };
  }, [persistToken, token]);

  const signup = useCallback(
    async (payload) => {
      const response = await signupRequest(payload);
      persistToken(response.access_token);
      setUser(response.user);
      return response;
    },
    [persistToken],
  );

  const login = useCallback(
    async (payload) => {
      const response = await loginRequest(payload);
      persistToken(response.access_token);
      setUser(response.user);
      return response;
    },
    [persistToken],
  );

  const logout = useCallback(() => {
    persistToken(null);
    setUser(null);
  }, [persistToken]);

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      signup,
      login,
      logout,
      refreshUser,
    }),
    [token, user, loading, signup, login, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
