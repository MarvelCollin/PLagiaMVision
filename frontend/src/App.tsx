import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Authentication from './pages/authentication';
import Home from './pages/home';
import MainLayout from './components/layout/main-layout';
import Forum from './pages/forum';
import Checker from './pages/checker';

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
          path: 'forum',
          element: <Forum/>
        },
        {
          path: 'checker',
          element: <Checker/>
        }
      ]
    }
  ]);

  return <RouterProvider router={router} />;
}

export default App;
