import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Navigate, Outlet, RouterProvider } from 'react-router-dom'
import './index.scss'
import { CreateFile } from './routes/CreateFile.tsx'
import App from './App.tsx'
import { Libraries } from './routes/Libraries.tsx'
import { Search } from './routes/Search.tsx'
import { CreateLibray } from './routes/CreateLibray.tsx'
import { Documents } from './routes/Documents.tsx'
import './styles/unreset.scss'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App/>,
    children: [
      {
        path: '',
        element: <Navigate to="/search"/>
      },
      {
        path: 'search',
        element: <Search/>,
      },
      {
        path: 'library',
        element: <Outlet/>,
        children: [
          {
            path: 'list',
            element: <Libraries/>,
          },
          {
            path: 'create',
            element: <CreateLibray/>,
          },
          {
            path: 'detail/:id',
            element: <Outlet/>,
            children: [
              {
                path: 'document/list',
                element: <Documents/>,
              },
              {
                path: 'document/create',
                element: <CreateFile/>,
              },
            ]
          },
        ]
      },
    ]
  }
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router}></RouterProvider>
  </StrictMode>,
)
