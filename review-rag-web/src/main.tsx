import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Outlet, RouterProvider } from 'react-router-dom'
import './index.css'
import { Files } from './routes/Files.tsx'
import { CreateFile } from './routes/CreateFile.tsx'

const router = createBrowserRouter([
  {
    path: '/file',
    element: <Outlet/>,
    children: [
      {
        path: 'list',
        element: <Files/>
      },
      {
        path: 'create',
        element: <CreateFile/>
      }
    ]
  }
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router}></RouterProvider>
  </StrictMode>,
)
