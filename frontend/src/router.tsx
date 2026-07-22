import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/app/AppLayout'
import { AuthLayout } from '@/app/AuthLayout'
import { ProtectedRoute } from '@/app/ProtectedRoute'
import { AdminRoute, RoleHome, UserRoute } from '@/app/RoleRoute'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { UploadPage } from '@/pages/upload/UploadPage'
import { HistoryPage } from '@/pages/history/HistoryPage'
import { UploadDetailPage } from '@/pages/history/UploadDetailPage'
import { AdminPage } from '@/pages/admin/AdminPage'
import { AdminUserDetailPage } from '@/pages/admin/AdminUserDetailPage'
import { ProfilePage } from '@/pages/profile/ProfilePage'

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/', element: <RoleHome /> },
          { path: '/profile', element: <ProfilePage /> },
          {
            element: <UserRoute />,
            children: [
              { path: '/dashboard', element: <DashboardPage /> },
              { path: '/upload', element: <UploadPage /> },
              { path: '/history', element: <HistoryPage /> },
              { path: '/history/:uploadId', element: <UploadDetailPage /> },
            ],
          },
          {
            element: <AdminRoute />,
            children: [
              { path: '/admin', element: <AdminPage /> },
              { path: '/admin/users/:userId', element: <AdminUserDetailPage /> },
            ],
          },
        ],
      },
    ],
  },
])
