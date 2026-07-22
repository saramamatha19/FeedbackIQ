import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import * as authApi from '@/api/auth'

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: authApi.fetchMe,
    retry: false,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: async (payload: { email: string; password: string; expectedRole: 'user' | 'admin' }) => {
      const user = await authApi.login(payload)
      if (user.role !== payload.expectedRole) {
        await authApi.logout()
        throw new Error(
          payload.expectedRole === 'admin'
            ? 'This account is not an admin.'
            : 'This is an admin account — sign in with the Admin option.',
        )
      }
      return user
    },
    onSuccess: (user) => {
      queryClient.setQueryData(['me'], user)
      navigate(user.role === 'admin' ? '/admin' : '/dashboard')
    },
  })
}

export function useRegister() {
  return useMutation({
    // Registration no longer logs the user in — the account is pending admin
    // approval, so there's no session to establish yet (see auth_service.authenticate_user).
    mutationFn: authApi.register,
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.setQueryData(['me'], null)
      navigate('/login')
    },
  })
}
