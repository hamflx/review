import './App.css'
import { SidebarProvider } from './components/ui/sidebar'
import { AppSidebar } from './components/ui/app-sidebar'
import { Outlet } from 'react-router-dom'

function App() {
  return (
    <div>
      <SidebarProvider className='h-dvh'>
        <AppSidebar/>
        <Outlet></Outlet>
      </SidebarProvider>
    </div>
  )
}

export default App
