import React from 'react';
import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom';
import Authentication from './pages/authentication';
import Home from './pages/home';
import MainLayout from './components/layout/main-layout';
import Forum from './pages/forum';


const App = () => {
  const router = createBrowserRouter([
    {
      path: '/',
      element: <Authentication />
    },
    {
      path: '/',
      element: <MainLayout />,
      children: [
        {
          path: 'home',
          element: <Home />
        },
        {
          path: 'checker',
          element: <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold">Checker Page (Coming Soon)</h1>
          </div>
        },
        {
          path: 'forum',
          element: <Forum/>
        }
      ]
    }
  ]);

  return <RouterProvider router={router} />;
}

export default App;
