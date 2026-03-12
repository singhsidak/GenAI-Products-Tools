/**
 * Zustand auth store.
 * Source of truth for the currently authenticated user.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '../services/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      setUser: (user) =>
        set({ user, isAuthenticated: !!user }),

      logout: () =>
        set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'csr-gen-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    },
  ),
)
