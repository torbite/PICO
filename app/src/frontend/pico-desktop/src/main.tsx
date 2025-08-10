import React from 'react'
import ReactDOM from 'react-dom/client'
import { createHashRouter, RouterProvider } from 'react-router-dom'
import './styles.css'
import SignInScreen from './screens/SignInScreen'
import SubscriptionGate from './screens/SubscriptionGate'
import ChatScreen from './screens/ChatScreen'

const router = createHashRouter([
  { path: '/', element: <SignInScreen /> },
  { path: '/sub', element: <SubscriptionGate /> },
  { path: '/chat', element: <ChatScreen /> }
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)