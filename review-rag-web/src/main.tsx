import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Outlet, RouterProvider } from 'react-router-dom'
import './index.css'
import { Files } from './routes/Files.tsx'
import { CreateFile } from './routes/CreateFile.tsx'
import App from './App.tsx'
import { Libraries } from './routes/Libraries.tsx'
import { Search } from './routes/Search.tsx'
import { CreateLibray } from './routes/CreateLibray.tsx'
import { LibraryDetail } from './routes/LibraryDetail.tsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App/>,
    children: [
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
            element: <LibraryDetail/>,
          },
        ]
      },
      {
        path: 'list',
        element: <Files/>,
      },
      {
        path: 'create',
        element: <CreateFile/>,
      },
    ]
  }
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router}></RouterProvider>
  </StrictMode>,
)
